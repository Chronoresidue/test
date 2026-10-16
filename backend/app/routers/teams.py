"""Teams and Team Blueprint router (including withdrawal and reshuffling)."""
import json
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import (
    Event, EventRequirement, EventMembership, Team, TeamMembership,
    AuditLog, User, Skill, UserSkill, MembershipStatus, TeamStatus, EventStatus
)
from app.schemas import (
    TeamOut, TeamMemberOut, RequirementCoverage, ReplacementCandidate,
    UserSkillOut
)
from app.auth import get_current_user, require_organizer
from app.matching_engine import (
    ParticipantCandidate, evaluate_team_coverage, compute_team_quality_score,
    generate_team_explanation, find_replacement_candidates
)

router = APIRouter(prefix="/api/teams", tags=["teams"])


def build_team_out_dto(team: Team, session: Session) -> TeamOut:
    """Helper to assemble full Team Blueprint data with coverage and scores."""
    event = session.get(Event, team.event_id)
    requirements = session.exec(
        select(EventRequirement).where(EventRequirement.event_id == team.event_id)
    ).all()
    skills = session.exec(select(Skill)).all()
    skills_map = {s.id: s.name for s in skills}

    active_memberships = session.exec(
        select(TeamMembership).where(
            TeamMembership.team_id == team.id,
            TeamMembership.status == MembershipStatus.ACTIVE
        )
    ).all()

    team_candidates: List[ParticipantCandidate] = []
    members_out: List[TeamMemberOut] = []

    for tm in active_memberships:
        user = session.get(User, tm.user_id)
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

        pc = ParticipantCandidate(
            user_id=user.id,
            user_name=user.full_name,
            user_email=user.email,
            skills=skills_dict,
            skills_full=skills_full,
            preferred_role=tm.role_in_team or user.preferred_roles,
            availability=None,
            event_goals=user.learning_goals,
            interests=user.interests
        )
        team_candidates.append(pc)

        # Contribution explanations
        contrib_parts = []
        if tm.role_in_team:
            contrib_parts.append(f"Role: {tm.role_in_team}")
        for req in requirements:
            prof = skills_dict.get(req.skill_id, 0)
            if prof >= req.min_proficiency:
                s_name = skills_map.get(req.skill_id, f"Skill #{req.skill_id}")
                contrib_parts.append(f"Fulfills {s_name} (L{prof})")

        members_out.append(
            TeamMemberOut(
                user_id=user.id,
                user_name=user.full_name,
                role_in_team=tm.role_in_team or "Contributor",
                status=tm.status,
                skills=[UserSkillOut(**s) for s in skills_full],
                contribution_explanation="; ".join(contrib_parts) if contrib_parts else "Versatile contributor"
            )
        )

    coverage = evaluate_team_coverage(requirements, team_candidates, skills_map)
    quality_score, breakdown = compute_team_quality_score(requirements, team_candidates, skills_map)
    explanation = generate_team_explanation(team.name, team_candidates, coverage, quality_score, breakdown)

    return TeamOut(
        id=team.id,
        event_id=team.event_id,
        name=team.name,
        status=team.status,
        members=members_out,
        coverage=coverage,
        matching_explanation=explanation,
        quality_score=quality_score
    )


@router.get("/events/{event_id}", response_model=List[TeamOut])
def get_event_teams(event_id: int, session: Session = Depends(get_session)):
    """List all teams for an event."""
    teams = session.exec(select(Team).where(Team.event_id == event_id)).all()
    return [build_team_out_dto(t, session) for t in teams]


@router.get("/{team_id}", response_model=TeamOut)
def get_team_blueprint(team_id: int, session: Session = Depends(get_session)):
    """Signature Component: Team Blueprint detailed breakdown."""
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return build_team_out_dto(team, session)


@router.post("/{team_id}/publish", response_model=TeamOut)
def publish_team(
    team_id: int,
    current_user: User = Depends(require_organizer),
    session: Session = Depends(get_session)
):
    """Publish a draft team."""
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    team.status = TeamStatus.PUBLISHED
    team.updated_at = datetime.utcnow()
    session.add(team)

    # Log audit
    audit = AuditLog(
        event_id=team.event_id,
        user_id=current_user.id,
        action="team_published",
        details=json.dumps({"team_id": team.id, "team_name": team.name})
    )
    session.add(audit)
    session.commit()
    session.refresh(team)

    return build_team_out_dto(team, session)


@router.post("/events/{event_id}/publish-all")
def publish_all_event_teams(
    event_id: int,
    current_user: User = Depends(require_organizer),
    session: Session = Depends(get_session)
):
    """Publish all formed teams for an event."""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    teams = session.exec(select(Team).where(Team.event_id == event_id)).all()
    for t in teams:
        t.status = TeamStatus.PUBLISHED
        t.updated_at = datetime.utcnow()
        session.add(t)

    event.status = EventStatus.TEAMS_PUBLISHED
    session.add(event)

    audit = AuditLog(
        event_id=event_id,
        user_id=current_user.id,
        action="all_teams_published",
        details=json.dumps({"published_count": len(teams)})
    )
    session.add(audit)
    session.commit()

    return {"status": "success", "published_count": len(teams)}


# ─── Withdrawal and Reshuffling ───────────────────────────────────────────────

@router.post("/{team_id}/withdraw/{user_id}")
def withdraw_team_member(
    team_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Withdraw or remove a team member gracefully."""
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Only the member themselves or an organizer can withdraw
    if current_user.id != user_id and current_user.role != "organizer":
        raise HTTPException(status_code=403, detail="Not authorized to remove this member")

    tm = session.exec(
        select(TeamMembership).where(
            TeamMembership.team_id == team_id,
            TeamMembership.user_id == user_id,
            TeamMembership.status == MembershipStatus.ACTIVE
        )
    ).first()

    if not tm:
        raise HTTPException(status_code=404, detail="Active membership not found")

    tm.status = MembershipStatus.LEFT
    tm.left_at = datetime.utcnow()
    session.add(tm)

    # Audit log
    audit = AuditLog(
        event_id=team.event_id,
        user_id=current_user.id,
        action="member_withdrawn",
        details=json.dumps({"team_id": team.id, "withdrawn_user_id": user_id})
    )
    session.add(audit)
    session.commit()

    return {"status": "success", "message": "Member withdrawn from team"}


@router.get("/{team_id}/replacement-candidates", response_model=List[ReplacementCandidate])
def get_replacement_candidates(
    team_id: int,
    session: Session = Depends(get_session)
):
    """Find and rank unassigned participants who can fill team gaps."""
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    event_id = team.event_id
    requirements = session.exec(
        select(EventRequirement).where(EventRequirement.event_id == event_id)
    ).all()
    skills = session.exec(select(Skill)).all()
    skills_map = {s.id: s.name for s in skills}

    # Identify currently assigned user IDs in any active team for this event
    assigned_tms = session.exec(
        select(TeamMembership)
        .join(Team)
        .where(Team.event_id == event_id, TeamMembership.status == MembershipStatus.ACTIVE)
    ).all()
    assigned_user_ids = {m.user_id for m in assigned_tms}

    # Find unassigned registered participants
    event_mems = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event_id,
            EventMembership.status == MembershipStatus.ACTIVE
        )
    ).all()

    available_candidates: List[ParticipantCandidate] = []
    for em in event_mems:
        if em.user_id in assigned_user_ids:
            continue
        user = session.get(User, em.user_id)
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

        available_candidates.append(
            ParticipantCandidate(
                user_id=user.id,
                user_name=user.full_name,
                user_email=user.email,
                skills=skills_dict,
                skills_full=skills_full,
                preferred_role=em.preferred_role or user.preferred_roles,
                availability=em.availability,
                event_goals=em.event_goals or user.learning_goals,
                interests=user.interests
            )
        )

    # Current team members
    active_mems = session.exec(
        select(TeamMembership).where(
            TeamMembership.team_id == team_id,
            TeamMembership.status == MembershipStatus.ACTIVE
        )
    ).all()
    team_members: List[ParticipantCandidate] = []
    for tm in active_mems:
        u = session.get(User, tm.user_id)
        if not u:
            continue
        u_skills = session.exec(select(UserSkill).where(UserSkill.user_id == u.id)).all()
        team_members.append(
            ParticipantCandidate(
                user_id=u.id,
                user_name=u.full_name,
                user_email=u.email,
                skills={us.skill_id: us.proficiency_level for us in u_skills},
                skills_full=[],
                preferred_role=tm.role_in_team
            )
        )

    # Dummy placeholder withdrawn user
    fake_user = User(id=0, email="", full_name="", hashed_password="")
    return find_replacement_candidates(
        withdrawn_user=fake_user,
        team_members=team_members,
        event_requirements=requirements,
        available_pool=available_candidates,
        skills_map=skills_map
    )


@router.post("/{team_id}/approve-replacement/{user_id}")
def approve_replacement(
    team_id: int,
    user_id: int,
    current_user: User = Depends(require_organizer),
    session: Session = Depends(get_session)
):
    """Organizer approves a replacement candidate into the team."""
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    candidate_user = session.get(User, user_id)
    if not candidate_user:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Add candidate to team
    new_tm = TeamMembership(
        team_id=team_id,
        user_id=user_id,
        status=MembershipStatus.ACTIVE,
        role_in_team=candidate_user.preferred_roles or "Specialist"
    )
    session.add(new_tm)

    # Audit log
    audit = AuditLog(
        event_id=team.event_id,
        user_id=current_user.id,
        action="replacement_approved",
        details=json.dumps({"team_id": team.id, "added_user_id": user_id, "user_name": candidate_user.full_name})
    )
    session.add(audit)
    session.commit()

    return {"status": "success", "message": f"{candidate_user.full_name} added to {team.name}"}
