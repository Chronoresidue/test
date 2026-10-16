"""Pydantic schemas for API request/response validation."""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ─── Auth ─────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email: str
    password: str = Field(min_length=6)
    full_name: str = Field(min_length=1)
    role: str = "participant"


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    bio: Optional[str] = None
    interests: Optional[str] = None
    preferred_roles: Optional[str] = None
    learning_goals: Optional[str] = None
    timezone: str = "Asia/Kolkata"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    interests: Optional[str] = None
    preferred_roles: Optional[str] = None
    learning_goals: Optional[str] = None
    timezone: Optional[str] = None


# ─── Skills ───────────────────────────────────────────────────────────────────

class SkillOut(BaseModel):
    id: int
    name: str
    category: str
    aliases: Optional[str] = None


class UserSkillCreate(BaseModel):
    skill_id: int
    proficiency_level: int = Field(ge=1, le=4)


class UserSkillOut(BaseModel):
    id: int
    skill_id: int
    skill_name: str = ""
    skill_category: str = ""
    proficiency_level: int
    evidence_type: str
    assessment_score: Optional[float] = None
    verified: bool = False


class UserSkillUpdate(BaseModel):
    proficiency_level: Optional[int] = Field(default=None, ge=1, le=4)


# ─── Evidence ─────────────────────────────────────────────────────────────────

class EvidenceCreate(BaseModel):
    skill_id: Optional[int] = None
    title: str
    url: Optional[str] = None
    description: Optional[str] = None
    evidence_kind: str = "project"


class EvidenceOut(BaseModel):
    id: int
    skill_id: Optional[int] = None
    title: str
    url: Optional[str] = None
    description: Optional[str] = None
    evidence_kind: str


# ─── Events ───────────────────────────────────────────────────────────────────

class EventCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: str = "hackathon"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    registration_deadline: Optional[datetime] = None
    min_team_size: int = Field(default=3, ge=2)
    max_team_size: int = Field(default=5, ge=2)
    participation_mode: str = "hybrid"


class EventOut(BaseModel):
    id: int
    organizer_id: int
    name: str
    description: Optional[str] = None
    category: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    registration_deadline: Optional[datetime] = None
    min_team_size: int
    max_team_size: int
    status: str
    participation_mode: str
    participant_count: int = 0
    created_at: datetime


class EventUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    registration_deadline: Optional[datetime] = None
    min_team_size: Optional[int] = None
    max_team_size: Optional[int] = None
    status: Optional[str] = None
    participation_mode: Optional[str] = None


# ─── Event Requirements ──────────────────────────────────────────────────────

class EventRequirementCreate(BaseModel):
    skill_id: int
    priority: str = "required"
    min_proficiency: int = Field(default=2, ge=1, le=4)
    people_needed: int = Field(default=1, ge=1)
    explanation: Optional[str] = None


class EventRequirementOut(BaseModel):
    id: int
    event_id: int
    skill_id: int
    skill_name: str = ""
    priority: str
    min_proficiency: int
    people_needed: int
    explanation: Optional[str] = None


# ─── Event Membership ────────────────────────────────────────────────────────

class EventJoin(BaseModel):
    availability: Optional[str] = None
    preferred_role: Optional[str] = None
    event_goals: Optional[str] = None


class EventMembershipOut(BaseModel):
    id: int
    event_id: int
    user_id: int
    user_name: str = ""
    user_email: str = ""
    status: str
    availability: Optional[str] = None
    preferred_role: Optional[str] = None
    event_goals: Optional[str] = None
    joined_at: datetime
    skills: List[UserSkillOut] = []


# ─── Teams ────────────────────────────────────────────────────────────────────

class TeamMemberOut(BaseModel):
    user_id: int
    user_name: str
    role_in_team: Optional[str] = None
    status: str
    skills: List[UserSkillOut] = []
    contribution_explanation: Optional[str] = None


class RequirementCoverage(BaseModel):
    requirement_id: int
    skill_name: str
    priority: str
    min_proficiency: int
    people_needed: int
    coverage_status: str  # covered, partially_covered, missing
    covered_by: List[str] = []  # user names
    explanation: str = ""


class TeamOut(BaseModel):
    id: int
    event_id: int
    name: str
    status: str
    members: List[TeamMemberOut] = []
    coverage: List[RequirementCoverage] = []
    matching_explanation: Optional[str] = None
    quality_score: Optional[float] = None


class MatchingResult(BaseModel):
    teams: List[TeamOut]
    unassigned: List[EventMembershipOut] = []
    summary: str = ""
    matching_run_id: Optional[int] = None


# ─── Gamification ─────────────────────────────────────────────────────────────

class DailyChallengeOut(BaseModel):
    id: int
    question: str
    options: List[str]
    skill_category: str
    difficulty: str
    already_completed: bool = False


class ChallengeSubmit(BaseModel):
    selected_index: int


class ChallengeResult(BaseModel):
    is_correct: bool
    correct_index: int
    explanation: Optional[str] = None
    streak: int = 0


class StreakInfo(BaseModel):
    current_streak: int
    longest_streak: int = 0
    total_completions: int = 0
    today_completed: bool = False


class BadgeOut(BaseModel):
    id: int
    name: str
    description: str
    icon: str
    earned_at: Optional[datetime] = None


# ─── Feedback ─────────────────────────────────────────────────────────────────

class FeedbackCreate(BaseModel):
    event_id: int
    team_id: Optional[int] = None
    communication_rating: Optional[int] = Field(default=None, ge=1, le=5)
    collaboration_rating: Optional[int] = Field(default=None, ge=1, le=5)
    responsibility_rating: Optional[int] = Field(default=None, ge=1, le=5)
    distribution_rating: Optional[int] = Field(default=None, ge=1, le=5)
    overall_rating: Optional[int] = Field(default=None, ge=1, le=5)
    comments: Optional[str] = None


class FeedbackOut(BaseModel):
    id: int
    event_id: int
    user_id: int
    team_id: Optional[int] = None
    communication_rating: Optional[int] = None
    collaboration_rating: Optional[int] = None
    responsibility_rating: Optional[int] = None
    distribution_rating: Optional[int] = None
    overall_rating: Optional[int] = None
    comments: Optional[str] = None
    created_at: datetime


# ─── Replacement ──────────────────────────────────────────────────────────────

class ReplacementCandidate(BaseModel):
    user_id: int
    user_name: str
    skills: List[UserSkillOut] = []
    fills_requirements: List[str] = []
    explanation: str = ""
    impact_score: float = 0.0
