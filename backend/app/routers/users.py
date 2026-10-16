"""User profile, skills, and evidence router."""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import User, Skill, UserSkill, Evidence, EvidenceType
from app.schemas import (
    UserOut, UserUpdate, SkillOut, UserSkillCreate, UserSkillOut,
    EvidenceCreate, EvidenceOut
)
from app.auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])


# ─── Profile ──────────────────────────────────────────────────────────────────

@router.put("/me", response_model=UserOut)
def update_profile(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update current user profile."""
    for field, val in user_in.dict(exclude_unset=True).items():
        setattr(current_user, field, val)
    current_user.updated_at = datetime.utcnow()
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return UserOut(**current_user.dict())


# ─── Skills Catalog ───────────────────────────────────────────────────────────

@router.get("/skills/catalog", response_model=List[SkillOut])
def get_skills_catalog(session: Session = Depends(get_session)):
    """List standard skills catalog."""
    skills = session.exec(select(Skill).order_by(Skill.category, Skill.name)).all()
    return [SkillOut(**s.dict()) for s in skills]


# ─── User Skills ──────────────────────────────────────────────────────────────

@router.get("/me/skills", response_model=List[UserSkillOut])
def get_my_skills(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all declared skills for current user."""
    user_skills = session.exec(
        select(UserSkill).where(UserSkill.user_id == current_user.id)
    ).all()

    results = []
    for us in user_skills:
        skill = session.get(Skill, us.skill_id)
        results.append(
            UserSkillOut(
                id=us.id,
                skill_id=us.skill_id,
                skill_name=skill.name if skill else f"Skill #{us.skill_id}",
                skill_category=skill.category if skill else "general",
                proficiency_level=us.proficiency_level,
                evidence_type=us.evidence_type,
                assessment_score=us.assessment_score,
                verified=us.verified
            )
        )
    return results


@router.post("/me/skills", response_model=UserSkillOut)
def add_or_update_my_skill(
    skill_in: UserSkillCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Add or update a skill proficiency."""
    skill = session.get(Skill, skill_in.skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    existing = session.exec(
        select(UserSkill).where(
            UserSkill.user_id == current_user.id,
            UserSkill.skill_id == skill_in.skill_id
        )
    ).first()

    if existing:
        existing.proficiency_level = skill_in.proficiency_level
        existing.updated_at = datetime.utcnow()
        session.add(existing)
        session.commit()
        session.refresh(existing)
        us = existing
    else:
        us = UserSkill(
            user_id=current_user.id,
            skill_id=skill_in.skill_id,
            proficiency_level=skill_in.proficiency_level,
            evidence_type=EvidenceType.SELF_REPORTED
        )
        session.add(us)
        session.commit()
        session.refresh(us)

    return UserSkillOut(
        id=us.id,
        skill_id=us.skill_id,
        skill_name=skill.name,
        skill_category=skill.category,
        proficiency_level=us.proficiency_level,
        evidence_type=us.evidence_type,
        assessment_score=us.assessment_score,
        verified=us.verified
    )


@router.delete("/me/skills/{skill_id}")
def remove_my_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Remove a declared skill."""
    existing = session.exec(
        select(UserSkill).where(
            UserSkill.user_id == current_user.id,
            UserSkill.skill_id == skill_id
        )
    ).first()
    if existing:
        session.delete(existing)
        session.commit()
    return {"status": "success", "message": "Skill removed"}


# ─── Evidence ─────────────────────────────────────────────────────────────────

@router.get("/me/evidence", response_model=List[EvidenceOut])
def get_my_evidence(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get all submitted evidence for current user."""
    evidences = session.exec(
        select(Evidence).where(Evidence.user_id == current_user.id)
    ).all()
    return [EvidenceOut(**e.dict()) for e in evidences]


@router.post("/me/evidence", response_model=EvidenceOut)
def add_evidence(
    ev_in: EvidenceCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Add a project link or portfolio proof for a skill."""
    evidence = Evidence(
        user_id=current_user.id,
        skill_id=ev_in.skill_id,
        title=ev_in.title,
        url=ev_in.url,
        description=ev_in.description,
        evidence_kind=ev_in.evidence_kind
    )
    session.add(evidence)

    # If linked to a skill, upgrade evidence_type from self_reported to evidence_linked
    if ev_in.skill_id:
        user_skill = session.exec(
            select(UserSkill).where(
                UserSkill.user_id == current_user.id,
                UserSkill.skill_id == ev_in.skill_id
            )
        ).first()
        if user_skill:
            user_skill.evidence_type = EvidenceType.EVIDENCE_LINKED
            session.add(user_skill)

    session.commit()
    session.refresh(evidence)
    return EvidenceOut(**evidence.dict())


@router.delete("/me/evidence/{evidence_id}")
def delete_evidence(
    evidence_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete an evidence item."""
    ev = session.get(Evidence, evidence_id)
    if ev and ev.user_id == current_user.id:
        session.delete(ev)
        session.commit()
    return {"status": "success", "message": "Evidence removed"}
