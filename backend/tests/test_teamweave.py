"""Automated test suite for TeamWeave backend."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.main import app
from app.database import get_session
from app.models import User, Event, Skill, EventRequirement, UserRole, RequirementPriority
from app.matching_engine import (
    ParticipantCandidate, form_teams_operation_b, evaluate_team_coverage,
    CoverageStatus
)

client = TestClient(app)


def test_healthcheck():
    """Verify health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["codename"] == "Living Weave"


def test_demo_seed_and_auth():
    """Verify seeded users can authenticate and retrieve profile."""
    # Login organizer
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "organizer@teamweave.dev", "password": "password123"}
    )
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    assert data["user"]["role"] == "organizer"

    token = data["access_token"]
    me_resp = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "organizer@teamweave.dev"


def test_matching_engine_deterministic():
    """Verify matching engine produces deterministic, identical results for same inputs."""
    event = Event(id=99, organizer_id=1, name="Test Event", min_team_size=2, max_team_size=3)
    reqs = [
        EventRequirement(id=1, event_id=99, skill_id=1, priority=RequirementPriority.REQUIRED, min_proficiency=2, people_needed=1),
        EventRequirement(id=2, event_id=99, skill_id=2, priority=RequirementPriority.REQUIRED, min_proficiency=2, people_needed=1),
    ]
    skills_map = {1: "React", 2: "Python"}

    participants = [
        ParticipantCandidate(user_id=101, user_name="Alice", user_email="a@test.com", skills={1: 3}, skills_full=[], preferred_role="Frontend"),
        ParticipantCandidate(user_id=102, user_name="Bob", user_email="b@test.com", skills={2: 3}, skills_full=[], preferred_role="Backend"),
        ParticipantCandidate(user_id=103, user_name="Charlie", user_email="c@test.com", skills={1: 2}, skills_full=[], preferred_role="Frontend"),
        ParticipantCandidate(user_id=104, user_name="Diana", user_email="d@test.com", skills={2: 4}, skills_full=[], preferred_role="Backend"),
    ]

    res1 = form_teams_operation_b(event, reqs, participants, skills_map)
    res2 = form_teams_operation_b(event, reqs, participants, skills_map)

    # Identical output
    assert len(res1["teams"]) == len(res2["teams"])
    assert res1["teams"][0]["name"] == res2["teams"][0]["name"]
    team1_members_run1 = [m.user_id for m in res1["teams"][0]["members"]]
    team1_members_run2 = [m.user_id for m in res2["teams"][0]["members"]]
    assert team1_members_run1 == team1_members_run2


def test_daily_challenge_flow():
    """Verify participant can retrieve and answer daily challenge."""
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "maya@teamweave.dev", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get challenge
    ch_resp = client.get("/api/gamification/daily-challenge", headers=headers)
    assert ch_resp.status_code == 200
    ch_data = ch_resp.json()
    assert len(ch_data["options"]) > 0

    # Submit answer
    sub_resp = client.post(
        "/api/gamification/daily-challenge/submit",
        json={"selected_index": 0},
        headers=headers
    )
    assert sub_resp.status_code == 200
    assert "is_correct" in sub_resp.json()
