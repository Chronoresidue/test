"""Post-event feedback router."""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Feedback, Event, User, TeamMembership
from app.schemas import FeedbackCreate, FeedbackOut
from app.auth import get_current_user

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackOut)
def submit_feedback(
    fb_in: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Submit post-event team collaboration feedback."""
    event = session.get(Event, fb_in.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    fb = Feedback(
        event_id=fb_in.event_id,
        user_id=current_user.id,
        team_id=fb_in.team_id,
        communication_rating=fb_in.communication_rating,
        collaboration_rating=fb_in.collaboration_rating,
        responsibility_rating=fb_in.responsibility_rating,
        distribution_rating=fb_in.distribution_rating,
        overall_rating=fb_in.overall_rating,
        comments=fb_in.comments
    )
    session.add(fb)
    session.commit()
    session.refresh(fb)

    return FeedbackOut(**fb.dict())


@router.get("/events/{event_id}", response_model=List[FeedbackOut])
def get_event_feedback(
    event_id: int,
    session: Session = Depends(get_session)
):
    """Get feedback entries for an event."""
    feedbacks = session.exec(
        select(Feedback).where(Feedback.event_id == event_id)
    ).all()
    return [FeedbackOut(**f.dict()) for f in feedbacks]
