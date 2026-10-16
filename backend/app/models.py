"""TeamWeave Database Models.

Entities: User, Skill, UserSkill, Evidence, Event, EventRequirement,
EventMembership, Team, TeamMembership, MatchingRun, DailyChallenge,
ChallengeAttempt, BadgeDefinition, EarnedBadge, DailyCompletion, Feedback.
"""
from datetime import datetime, date
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
import enum


# ─── Enums ────────────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    PARTICIPANT = "participant"
    ORGANIZER = "organizer"


class ProficiencyLevel(int, enum.Enum):
    EXPLORING = 1
    DEVELOPING = 2
    INDEPENDENT = 3
    ADVANCED = 4


class EvidenceType(str, enum.Enum):
    SELF_REPORTED = "self_reported"
    ASSESSMENT_SUPPORTED = "assessment_supported"
    EVIDENCE_LINKED = "evidence_linked"
    NOT_ASSESSED = "not_assessed"


class RequirementPriority(str, enum.Enum):
    REQUIRED = "required"
    PREFERRED = "preferred"


class CoverageStatus(str, enum.Enum):
    COVERED = "covered"
    PARTIALLY_COVERED = "partially_covered"
    MISSING = "missing"
    NEEDS_REVIEW = "needs_review"


class MembershipStatus(str, enum.Enum):
    ACTIVE = "active"
    LEFT = "left"
    REMOVED = "removed"
    WAITLISTED = "waitlisted"


class TeamStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class EventStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    MATCHING = "matching"
    TEAMS_PUBLISHED = "teams_published"
    COMPLETED = "completed"


# ─── Users ────────────────────────────────────────────────────────────────────

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    full_name: str
    role: str = Field(default=UserRole.PARTICIPANT)
    bio: Optional[str] = None
    interests: Optional[str] = None  # comma-separated
    preferred_roles: Optional[str] = None  # comma-separated
    learning_goals: Optional[str] = None
    timezone: str = Field(default="Asia/Kolkata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    skills: List["UserSkill"] = Relationship(back_populates="user")
    evidences: List["Evidence"] = Relationship(back_populates="user")
    event_memberships: List["EventMembership"] = Relationship(back_populates="user")
    earned_badges: List["EarnedBadge"] = Relationship(back_populates="user")
    challenge_attempts: List["ChallengeAttempt"] = Relationship(back_populates="user")
    daily_completions: List["DailyCompletion"] = Relationship(back_populates="user")


# ─── Skills ───────────────────────────────────────────────────────────────────

class Skill(SQLModel, table=True):
    __tablename__ = "skills"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    category: str = Field(default="general")
    aliases: Optional[str] = None  # comma-separated aliases
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserSkill(SQLModel, table=True):
    __tablename__ = "user_skills"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    skill_id: int = Field(foreign_key="skills.id", index=True)
    proficiency_level: int = Field(default=1)  # 1-4
    evidence_type: str = Field(default=EvidenceType.SELF_REPORTED)
    assessment_score: Optional[float] = None
    verified: bool = Field(default=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(back_populates="skills")
    skill: Optional[Skill] = Relationship()


# ─── Evidence ─────────────────────────────────────────────────────────────────

class Evidence(SQLModel, table=True):
    __tablename__ = "evidences"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    skill_id: Optional[int] = Field(default=None, foreign_key="skills.id")
    title: str
    url: Optional[str] = None
    description: Optional[str] = None
    evidence_kind: str = Field(default="project")  # project, certificate, portfolio, research
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="evidences")
    skill: Optional[Skill] = Relationship()


# ─── Events ───────────────────────────────────────────────────────────────────

class Event(SQLModel, table=True):
    __tablename__ = "events"

    id: Optional[int] = Field(default=None, primary_key=True)
    organizer_id: int = Field(foreign_key="users.id", index=True)
    name: str
    description: Optional[str] = None
    category: str = Field(default="hackathon")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    registration_deadline: Optional[datetime] = None
    min_team_size: int = Field(default=3)
    max_team_size: int = Field(default=5)
    status: str = Field(default=EventStatus.DRAFT)
    participation_mode: str = Field(default="hybrid")  # in_person, remote, hybrid
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    requirements: List["EventRequirement"] = Relationship(back_populates="event")
    memberships: List["EventMembership"] = Relationship(back_populates="event")
    teams: List["Team"] = Relationship(back_populates="event")


class EventRequirement(SQLModel, table=True):
    __tablename__ = "event_requirements"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="events.id", index=True)
    skill_id: int = Field(foreign_key="skills.id")
    priority: str = Field(default=RequirementPriority.REQUIRED)
    min_proficiency: int = Field(default=2)
    people_needed: int = Field(default=1)
    explanation: Optional[str] = None

    event: Optional[Event] = Relationship(back_populates="requirements")
    skill: Optional[Skill] = Relationship()


class EventMembership(SQLModel, table=True):
    __tablename__ = "event_memberships"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="events.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    status: str = Field(default=MembershipStatus.ACTIVE)
    availability: Optional[str] = None  # JSON string of available slots
    preferred_role: Optional[str] = None
    event_goals: Optional[str] = None
    joined_at: datetime = Field(default_factory=datetime.utcnow)

    event: Optional[Event] = Relationship(back_populates="memberships")
    user: Optional[User] = Relationship(back_populates="event_memberships")


# ─── Teams ────────────────────────────────────────────────────────────────────

class Team(SQLModel, table=True):
    __tablename__ = "teams"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="events.id", index=True)
    name: str
    status: str = Field(default=TeamStatus.DRAFT)
    matching_run_id: Optional[int] = Field(default=None, foreign_key="matching_runs.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    event: Optional[Event] = Relationship(back_populates="teams")
    members: List["TeamMembership"] = Relationship(back_populates="team")


class TeamMembership(SQLModel, table=True):
    __tablename__ = "team_memberships"

    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="teams.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    status: str = Field(default=MembershipStatus.ACTIVE)
    role_in_team: Optional[str] = None
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    left_at: Optional[datetime] = None

    team: Optional[Team] = Relationship(back_populates="members")
    user: Optional[User] = Relationship()


# ─── Matching ─────────────────────────────────────────────────────────────────

class MatchingRun(SQLModel, table=True):
    __tablename__ = "matching_runs"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="events.id", index=True)
    algorithm_version: str = Field(default="greedy_v1")
    config_snapshot: Optional[str] = None  # JSON of weights used
    total_participants: int = Field(default=0)
    assigned_count: int = Field(default=0)
    unassigned_count: int = Field(default=0)
    teams_formed: int = Field(default=0)
    explanation_summary: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ─── Daily Challenges & Gamification ─────────────────────────────────────────

class DailyChallenge(SQLModel, table=True):
    __tablename__ = "daily_challenges"

    id: Optional[int] = Field(default=None, primary_key=True)
    question: str
    options: str  # JSON array of option strings
    correct_index: int
    skill_category: str = Field(default="general")
    difficulty: str = Field(default="medium")
    explanation: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChallengeAttempt(SQLModel, table=True):
    __tablename__ = "challenge_attempts"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    challenge_id: int = Field(foreign_key="daily_challenges.id")
    selected_index: int
    is_correct: bool
    attempted_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="challenge_attempts")


class DailyCompletion(SQLModel, table=True):
    __tablename__ = "daily_completions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    completion_date: date
    challenge_id: int = Field(foreign_key="daily_challenges.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="daily_completions")


class BadgeDefinition(SQLModel, table=True):
    __tablename__ = "badge_definitions"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: str
    icon: str = Field(default="award")
    criteria: str  # JSON rules
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EarnedBadge(SQLModel, table=True):
    __tablename__ = "earned_badges"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    badge_id: int = Field(foreign_key="badge_definitions.id")
    earned_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional[User] = Relationship(back_populates="earned_badges")
    badge: Optional[BadgeDefinition] = Relationship()


# ─── Feedback ─────────────────────────────────────────────────────────────────

class Feedback(SQLModel, table=True):
    __tablename__ = "feedbacks"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="events.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    team_id: Optional[int] = Field(default=None, foreign_key="teams.id")
    communication_rating: Optional[int] = None  # 1-5
    collaboration_rating: Optional[int] = None
    responsibility_rating: Optional[int] = None
    distribution_rating: Optional[int] = None
    overall_rating: Optional[int] = None
    comments: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ─── Audit ────────────────────────────────────────────────────────────────────

class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: Optional[int] = Field(default=None, foreign_key="events.id")
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    action: str  # e.g. "team_published", "member_left", "replacement_approved"
    details: Optional[str] = None  # JSON
    created_at: datetime = Field(default_factory=datetime.utcnow)
