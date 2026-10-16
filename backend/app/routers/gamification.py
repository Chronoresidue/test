"""Gamification router: daily challenges, streak tracking, honest badges."""
import json
from datetime import datetime, date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.database import get_session
from app.models import (
    DailyChallenge, ChallengeAttempt, DailyCompletion,
    BadgeDefinition, EarnedBadge, User
)
from app.schemas import (
    DailyChallengeOut, ChallengeSubmit, ChallengeResult,
    StreakInfo, BadgeOut
)
from app.auth import get_current_user

router = APIRouter(prefix="/api/gamification", tags=["gamification"])


@router.get("/daily-challenge", response_model=DailyChallengeOut)
def get_daily_challenge(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Retrieve today's active skill challenge."""
    today = date.today()
    # Check if already completed today
    completed = session.exec(
        select(DailyCompletion).where(
            DailyCompletion.user_id == current_user.id,
            DailyCompletion.completion_date == today
        )
    ).first()

    # Pick a challenge deterministically based on day of year
    challenges = session.exec(select(DailyChallenge)).all()
    if not challenges:
        raise HTTPException(status_code=404, detail="No daily challenges available")

    day_index = today.toordinal() % len(challenges)
    challenge = challenges[day_index]

    options_list = json.loads(challenge.options) if challenge.options else []

    return DailyChallengeOut(
        id=challenge.id,
        question=challenge.question,
        options=options_list,
        skill_category=challenge.skill_category,
        difficulty=challenge.difficulty,
        already_completed=completed is not None
    )


@router.post("/daily-challenge/submit", response_model=ChallengeResult)
def submit_daily_challenge(
    sub_in: ChallengeSubmit,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Submit answer for today's challenge."""
    today = date.today()
    challenges = session.exec(select(DailyChallenge)).all()
    if not challenges:
        raise HTTPException(status_code=404, detail="No daily challenges found")

    day_index = today.toordinal() % len(challenges)
    challenge = challenges[day_index]

    is_correct = (sub_in.selected_index == challenge.correct_index)

    # Record attempt
    attempt = ChallengeAttempt(
        user_id=current_user.id,
        challenge_id=challenge.id,
        selected_index=sub_in.selected_index,
        is_correct=is_correct
    )
    session.add(attempt)

    # Check / record completion
    already_done = session.exec(
        select(DailyCompletion).where(
            DailyCompletion.user_id == current_user.id,
            DailyCompletion.completion_date == today
        )
    ).first()

    if not already_done and is_correct:
        completion = DailyCompletion(
            user_id=current_user.id,
            completion_date=today,
            challenge_id=challenge.id
        )
        session.add(completion)

    session.commit()

    # Calculate streak
    streak_info = calculate_user_streak(current_user.id, session)

    # Badge evaluation: First Challenge, 3-Day Streak, 7-Day Streak
    check_and_award_badges(current_user.id, streak_info.current_streak, session)

    return ChallengeResult(
        is_correct=is_correct,
        correct_index=challenge.correct_index,
        explanation=challenge.explanation,
        streak=streak_info.current_streak
    )


def calculate_user_streak(user_id: int, session: Session) -> StreakInfo:
    """Calculate consecutive daily completion streak."""
    completions = session.exec(
        select(DailyCompletion)
        .where(DailyCompletion.user_id == user_id)
        .order_by(DailyCompletion.completion_date.desc())
    ).all()

    if not completions:
        return StreakInfo(current_streak=0, longest_streak=0, total_completions=0, today_completed=False)

    completion_dates = {c.completion_date for c in completions}
    today = date.today()
    today_completed = today in completion_dates

    # Current streak calculation
    current_streak = 0
    check_day = today if today_completed else (today - timedelta(days=1))

    while check_day in completion_dates:
        current_streak += 1
        check_day -= timedelta(days=1)

    return StreakInfo(
        current_streak=current_streak,
        longest_streak=max(current_streak, len(completion_dates)),
        total_completions=len(completion_dates),
        today_completed=today_completed
    )


def check_and_award_badges(user_id: int, current_streak: int, session: Session):
    """Award milestone badges honestly without inflation."""
    # First Challenge badge
    first_badge = session.exec(select(BadgeDefinition).where(BadgeDefinition.name == "First Step")).first()
    if first_badge:
        has_earned = session.exec(
            select(EarnedBadge).where(
                EarnedBadge.user_id == user_id,
                EarnedBadge.badge_id == first_badge.id
            )
        ).first()
        if not has_earned:
            eb = EarnedBadge(user_id=user_id, badge_id=first_badge.id)
            session.add(eb)
            session.commit()

    # 3-Day Streak badge
    if current_streak >= 3:
        streak_badge = session.exec(select(BadgeDefinition).where(BadgeDefinition.name == "Consistent Weaver")).first()
        if streak_badge:
            has_earned = session.exec(
                select(EarnedBadge).where(
                    EarnedBadge.user_id == user_id,
                    EarnedBadge.badge_id == streak_badge.id
                )
            ).first()
            if not has_earned:
                eb = EarnedBadge(user_id=user_id, badge_id=streak_badge.id)
                session.add(eb)
                session.commit()


@router.get("/streak", response_model=StreakInfo)
def get_streak_info(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get current streak stats."""
    return calculate_user_streak(current_user.id, session)


@router.get("/badges", response_model=List[BadgeOut])
def list_badges(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """List all badges with earned timestamp for current user."""
    all_defs = session.exec(select(BadgeDefinition)).all()
    earned_map = {
        eb.badge_id: eb.earned_at
        for eb in session.exec(select(EarnedBadge).where(EarnedBadge.user_id == current_user.id)).all()
    }

    results = []
    for b in all_defs:
        results.append(
            BadgeOut(
                id=b.id,
                name=b.name,
                description=b.description,
                icon=b.icon,
                earned_at=earned_map.get(b.id)
            )
        )
    return results
