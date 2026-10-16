"""Event and requirements management router."""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import (
    Event, EventRequirement, EventMembership, User, Skill, UserSkill,
    UserRole, EventStatus, MembershipStatus
)
from app.schemas import (
    EventCreate, EventOut, EventUpdate, EventRequirementCreate,
    EventRequirementOut, EventJoin, EventMembershipOut, UserSkillOut
)
from app.auth import get_current_user, require_organizer

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=List[EventOut])
def list_events(session: Session = Depends(get_session)):
    """List all available events."""
    events = session.exec(select(Event).order_by(Event.created_at.desc())).all()
    results = []
    for e in events:
        p_count = session.exec(
            select(EventMembership).where(
                EventMembership.event_id == e.id,
                EventMembership.status == MembershipStatus.ACTIVE
            )
        ).all()
        results.append(
            EventOut(
                id=e.id,
                organizer_id=e.organizer_id,
                name=e.name,
                description=e.description,
                category=e.category,
                start_date=e.start_date,
                end_date=e.end_date,
                registration_deadline=e.registration_deadline,
                min_team_size=e.min_team_size,
                max_team_size=e.max_team_size,
                status=e.status,
                participation_mode=e.participation_mode,
                participant_count=len(p_count),
                created_at=e.created_at
            )
        )
    return results


@router.post("", response_model=EventOut)
def create_event(
    event_in: EventCreate,
    current_user: User = Depends(require_organizer),
    session: Session = Depends(get_session)
):
    """Create a new event (organizer only)."""
    event = Event(
        organizer_id=current_user.id,
        name=event_in.name,
        description=event_in.description,
        category=event_in.category,
        start_date=event_in.start_date,
        end_date=event_in.end_date,
        registration_deadline=event_in.registration_deadline,
        min_team_size=event_in.min_team_size,
        max_team_size=event_in.max_team_size,
        participation_mode=event_in.participation_mode,
        status=EventStatus.OPEN
    )
    session.add(event)
    session.commit()
    session.refresh(event)

    return EventOut(
        id=event.id,
        organizer_id=event.organizer_id,
        name=event.name,
        description=event.description,
        category=event.category,
        start_date=event.start_date,
        end_date=event.end_date,
        registration_deadline=event.registration_deadline,
        min_team_size=event.min_team_size,
        max_team_size=event.max_team_size,
        status=event.status,
        participation_mode=event.participation_mode,
        participant_count=0,
        created_at=event.created_at
    )


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, session: Session = Depends(get_session)):
    """Get single event details."""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    p_count = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event.id,
            EventMembership.status == MembershipStatus.ACTIVE
        )
    ).all()

    return EventOut(
        id=event.id,
        organizer_id=event.organizer_id,
        name=event.name,
        description=event.description,
        category=event.category,
        start_date=event.start_date,
        end_date=event.end_date,
        registration_deadline=event.registration_deadline,
        min_team_size=event.min_team_size,
        max_team_size=event.max_team_size,
        status=event.status,
        participation_mode=event.participation_mode,
        participant_count=len(p_count),
        created_at=event.created_at
    )


@router.put("/{event_id}", response_model=EventOut)
def update_event(
    event_id: int,
    event_in: EventUpdate,
    current_user: User = Depends(require_organizer),
    session: Session = Depends(get_session)
):
    """Update event configuration (organizer only)."""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not the event organizer")

    for field, val in event_in.dict(exclude_unset=True).items():
        setattr(event, field, val)
    event.updated_at = datetime.utcnow()
    session.add(event)
    session.commit()
    session.refresh(event)

    p_count = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event.id,
            EventMembership.status == MembershipStatus.ACTIVE
        )
    ).all()

    return EventOut(
        id=event.id,
        organizer_id=event.organizer_id,
        name=event.name,
        description=event.description,
        category=event.category,
        start_date=event.start_date,
        end_date=event.end_date,
        registration_deadline=event.registration_deadline,
        min_team_size=event.min_team_size,
        max_team_size=event.max_team_size,
        status=event.status,
        participation_mode=event.participation_mode,
        participant_count=len(p_count),
        created_at=event.created_at
    )


# ─── Event Requirements ──────────────────────────────────────────────────────

@router.get("/{event_id}/requirements", response_model=List[EventRequirementOut])
def get_event_requirements(event_id: int, session: Session = Depends(get_session)):
    """List skill requirements for an event."""
    reqs = session.exec(
        select(EventRequirement).where(EventRequirement.event_id == event_id)
    ).all()

    results = []
    for r in reqs:
        skill = session.get(Skill, r.skill_id)
        results.append(
            EventRequirementOut(
                id=r.id,
                event_id=r.event_id,
                skill_id=r.skill_id,
                skill_name=skill.name if skill else f"Skill #{r.skill_id}",
                priority=r.priority,
                min_proficiency=r.min_proficiency,
                people_needed=r.people_needed,
                explanation=r.explanation
            )
        )
    return results


@router.post("/{event_id}/requirements", response_model=EventRequirementOut)
def add_event_requirement(
    event_id: int,
    req_in: EventRequirementCreate,
    current_user: User = Depends(require_organizer),
    session: Session = Depends(get_session)
):
    """Add a requirement to an event (organizer only)."""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.organizer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not the event organizer")

    skill = session.get(Skill, req_in.skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    req = EventRequirement(
        event_id=event_id,
        skill_id=req_in.skill_id,
        priority=req_in.priority,
        min_proficiency=req_in.min_proficiency,
        people_needed=req_in.people_needed,
        explanation=req_in.explanation
    )
    session.add(req)
    session.commit()
    session.refresh(req)

    return EventRequirementOut(
        id=req.id,
        event_id=req.event_id,
        skill_id=req.skill_id,
        skill_name=skill.name,
        priority=req.priority,
        min_proficiency=req.min_proficiency,
        people_needed=req.people_needed,
        explanation=req.explanation
    )


@router.delete("/{event_id}/requirements/{req_id}")
def delete_event_requirement(
    event_id: int,
    req_id: int,
    current_user: User = Depends(require_organizer),
    session: Session = Depends(get_session)
):
    """Delete a requirement from an event."""
    req = session.get(EventRequirement, req_id)
    if req and req.event_id == event_id:
        session.delete(req)
        session.commit()
    return {"status": "success", "message": "Requirement removed"}


# ─── Joining & Participant Pool ───────────────────────────────────────────────

@router.post("/{event_id}/join", response_model=EventMembershipOut)
def join_event(
    event_id: int,
    join_in: EventJoin,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Participant joins an event with preferences."""
    event = session.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    existing = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event_id,
            EventMembership.user_id == current_user.id
        )
    ).first()

    if existing:
        existing.status = MembershipStatus.ACTIVE
        existing.availability = join_in.availability
        existing.preferred_role = join_in.preferred_role
        existing.event_goals = join_in.event_goals
        session.add(existing)
        session.commit()
        session.refresh(existing)
        mem = existing
    else:
        mem = EventMembership(
            event_id=event_id,
            user_id=current_user.id,
            status=MembershipStatus.ACTIVE,
            availability=join_in.availability,
            preferred_role=join_in.preferred_role,
            event_goals=join_in.event_goals
        )
        session.add(mem)
        session.commit()
        session.refresh(mem)

    # Fetch user skills
    user_skills = session.exec(
        select(UserSkill).where(UserSkill.user_id == current_user.id)
    ).all()
    skills_out = []
    for us in user_skills:
        s = session.get(Skill, us.skill_id)
        skills_out.append(
            UserSkillOut(
                id=us.id,
                skill_id=us.skill_id,
                skill_name=s.name if s else "",
                skill_category=s.category if s else "",
                proficiency_level=us.proficiency_level,
                evidence_type=us.evidence_type,
                verified=us.verified
            )
        )

    return EventMembershipOut(
        id=mem.id,
        event_id=mem.event_id,
        user_id=mem.user_id,
        user_name=current_user.full_name,
        user_email=current_user.email,
        status=mem.status,
        availability=mem.availability,
        preferred_role=mem.preferred_role,
        event_goals=mem.event_goals,
        joined_at=mem.joined_at,
        skills=skills_out
    )


@router.get("/{event_id}/participants", response_model=List[EventMembershipOut])
def get_event_participants(
    event_id: int,
    session: Session = Depends(get_session)
):
    """List all registered participants and their declared capabilities."""
    memberships = session.exec(
        select(EventMembership).where(
            EventMembership.event_id == event_id,
            EventMembership.status == MembershipStatus.ACTIVE
        )
    ).all()

    results = []
    for mem in memberships:
        user = session.get(User, mem.user_id)
        if not user:
            continue
        user_skills = session.exec(
            select(UserSkill).where(UserSkill.user_id == user.id)
        ).all()
        skills_out = []
        for us in user_skills:
            s = session.get(Skill, us.skill_id)
            skills_out.append(
                UserSkillOut(
                    id=us.id,
                    skill_id=us.skill_id,
                    skill_name=s.name if s else "",
                    skill_category=s.category if s else "",
                    proficiency_level=us.proficiency_level,
                    evidence_type=us.evidence_type,
                    verified=us.verified
                )
            )

        results.append(
            EventMembershipOut(
                id=mem.id,
                event_id=mem.event_id,
                user_id=mem.user_id,
                user_name=user.full_name,
                user_email=user.email,
                status=mem.status,
                availability=mem.availability,
                preferred_role=mem.preferred_role,
                event_goals=mem.event_goals,
                joined_at=mem.joined_at,
                skills=skills_out
            )
        )

    return results
