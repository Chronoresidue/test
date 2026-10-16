"""Matching execution and recommendation router."""
import json
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import (
    Event, EventRequirement, EventMembership, Team, TeamMembership,
    MatchingRun, User, Skill, UserSkill, EventStatus, MembershipStatus,
    TeamStatus
)
from app.schemas import MatchingResult, TeamOut, EventMembershipOut, UserSkillOut
from app.auth import get_current_user, require_organizer
from app.matching_engine import (
    ParticipantCandidate, form_teams_operation_b, evaluate_team_coverage,
    compute_team_quality_score, generate_team_explanation
)

router = APIRouter(prefix="/api/matching", tags=["matching"])


@router.post("/events/{event_id}/run", response_model=MatchingResult)
def run_event_matching(
    event_id: int,
    current_user: User = Depends(require_organizer),
    session: Session = Depends(get_session)
):
    """Run Operation B: Form balanced teams from event participant pool."""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only event organizer can run matching")

    # Fetch event requirements
    requirements = session.exec(
        select(EventRequirement).where(EventRequirement.event_id == event_id)
    ).all()

    # Fetch skills map
    skills = session.exec(select(Skill)).all()
    skills_map = {s.id: s.name for s in skills}

    # Fetch active participants
    memberships = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event_id,
            EventMembership.status == MembershipStatus.ACTIVE
        )
    ).all()

    if not memberships:
        raise HTTPException(status_code=400, detail="No registered participants in this event")

    participant_candidates: List[ParticipantCandidate] = []
    for mem in memberships:
        user = session.get(User, mem.user_id)
        if not user:
            continue
        user_skills = session.exec(
            select(UserSkill).where(UserSkill.user_id == user.id)
        ).all()
        
        skills_dict = {us.skill_id: us.proficiency_level for us in user_skills}
        skills_full = []
        for us in user_skills:
            s_name = skills_map.get(us.skill_id, f"Skill #{us.skill_id}")
            s_obj = session.get(Skill, us.skill_id)
            skills_full.append({
                "id": us.id,
                "skill_id": us.skill_id,
                "skill_name": s_name,
                "skill_category": s_obj.category if s_obj else "general",
                "proficiency_level": us.proficiency_level,
                "evidence_type": us.evidence_type,
                "assessment_score": us.assessment_score,
                "verified": us.verified
            })

        participant_candidates.append(
            ParticipantCandidate(
                user_id=user.id,
                user_name=user.full_name,
                user_email=user.email,
                skills=skills_dict,
                skills_full=skills_full,
                preferred_role=mem.preferred_role or user.preferred_roles,
                availability=mem.availability,
                event_goals=mem.event_goals or user.learning_goals,
                interests=user.interests
            )
        )

    # Execute matching engine
    result = form_teams_operation_b(
        event=event,
        requirements=requirements,
        participants=participant_candidates,
        skills_map=skills_map
    )

    # Remove prior draft teams for this event to allow clean recalculation
    old_teams = session.exec(select(Team).where(Team.event_id == event_id)).all()
    for ot in old_teams:
        old_mems = session.exec(select(TeamMembership).where(TeamMembership.team_id == ot.id)).all()
        for om in old_mems:
            session.delete(om)
        session.delete(ot)
    session.commit()

    # Record Matching Run
    assigned_count = sum(len(t["members"]) for t in result["teams"])
    unassigned_count = len(result["unassigned"])
    run = MatchingRun(
        event_id=event_id,
        algorithm_version="greedy_v1",
        config_snapshot=json.dumps({"version": "1.0", "weights": "standard"}),
        total_participants=len(participant_candidates),
        assigned_count=assigned_count,
        unassigned_count=unassigned_count,
        teams_formed=len(result["teams"]),
        explanation_summary=result["summary"]
    )
    session.add(run)
    session.commit()
    session.refresh(run)

    # Persist formed teams and memberships
    persisted_teams: List[TeamOut] = []
    for team_data in result["teams"]:
        team = Team(
            event_id=event_id,
            name=team_data["name"],
            status=TeamStatus.DRAFT,
            matching_run_id=run.id
        )
        session.add(team)
        session.commit()
        session.refresh(team)

        for m_out in team_data["members"]:
            tm = TeamMembership(
                team_id=team.id,
                user_id=m_out.user_id,
                status=MembershipStatus.ACTIVE,
                role_in_team=m_out.role_in_team
            )
            session.add(tm)
        session.commit()

        persisted_teams.append(
            TeamOut(
                id=team.id,
                event_id=team.event_id,
                name=team.name,
                status=team.status,
                members=team_data["members"],
                coverage=team_data["coverage"],
                matching_explanation=team_data["matching_explanation"],
                quality_score=team_data["quality_score"]
            )
        )

    # Format unassigned members
    unassigned_out: List[EventMembershipOut] = []
    for u in result["unassigned"]:
        unassigned_out.append(
            EventMembershipOut(
                id=0,
                event_id=event_id,
                user_id=u.user_id,
                user_name=u.user_name,
                user_email=u.user_email,
                status="unassigned",
                preferred_role=u.preferred_role,
                joined_at=datetime.utcnow(),
                skills=[UserSkillOut(**s) for s in u.skills_full]
            )
        )

    # Update event status
    event.status = EventStatus.MATCHING
    session.add(event)
    session.commit()

    return MatchingResult(
        teams=persisted_teams,
        unassigned=unassigned_out,
        summary=result["summary"],
        matching_run_id=run.id
    )
