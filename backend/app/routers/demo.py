"""Demo and seed data management router."""
import json
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.models import (
    User, Skill, UserSkill, Evidence, Event, EventRequirement,
    EventMembership, DailyChallenge, BadgeDefinition, EarnedBadge,
    DailyCompletion, UserRole, EvidenceType, RequirementPriority,
    EventStatus, MembershipStatus
)
from app.auth import hash_password

router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.post("/seed")
def seed_demo_data(session: Session = Depends(get_session)):
    """Seed comprehensive realistic demonstration dataset."""
    # 1. Clean existing records to ensure fresh reproducible state
    # (Optional: or only seed if empty)
    existing_users = session.exec(select(User)).first()
    if existing_users:
        return {"status": "already_seeded", "message": "Demo data already exists"}

    # 2. Seed Skills
    skills_data = [
        {"name": "React", "category": "frontend", "aliases": "React.js, Next.js"},
        {"name": "TypeScript", "category": "frontend", "aliases": "TS"},
        {"name": "Tailwind CSS", "category": "frontend", "aliases": "Tailwind"},
        {"name": "Python", "category": "backend", "aliases": "Py"},
        {"name": "FastAPI", "category": "backend", "aliases": "FastAPI, API"},
        {"name": "PostgreSQL", "category": "backend", "aliases": "Postgres, SQL"},
        {"name": "PyTorch", "category": "ai_ml", "aliases": "Torch, Deep Learning"},
        {"name": "Machine Learning", "category": "ai_ml", "aliases": "ML, Scikit-learn"},
        {"name": "LLM Engineering", "category": "ai_ml", "aliases": "RAG, Prompt Engineering"},
        {"name": "UI/UX Design", "category": "design", "aliases": "Product Design"},
        {"name": "Figma", "category": "design", "aliases": "Wireframing, Prototyping"},
        {"name": "Docker & Cloud", "category": "devops", "aliases": "DevOps, Containerization"},
        {"name": "Product Strategy", "category": "product", "aliases": "Scrum, Product Management"},
    ]

    skill_objs = {}
    for s in skills_data:
        obj = session.exec(select(Skill).where(Skill.name == s["name"])).first()
        if not obj:
            obj = Skill(name=s["name"], category=s["category"], aliases=s.get("aliases"))
            session.add(obj)
            session.commit()
            session.refresh(obj)
        skill_objs[s["name"]] = obj

    # 3. Seed Users
    # 1 Organizer
    org = User(
        email="organizer@teamweave.dev",
        hashed_password=hash_password("password123"),
        full_name="Dr. Aarav Patel",
        role=UserRole.ORGANIZER,
        bio="Lead Hackathon Director & Tech Community Organizer",
        interests="Hackathons, Community, AI Innovation",
        timezone="Asia/Kolkata"
    )
    session.add(org)
    session.commit()
    session.refresh(org)

    # 12 Diverse Participants
    participants_data = [
        {
            "name": "Maya Sharma",
            "email": "maya@teamweave.dev",
            "role": "frontend",
            "bio": "Frontend architect specializing in high-performance web UIs and design tokens.",
            "skills": [("React", 4), ("TypeScript", 3), ("Tailwind CSS", 4), ("UI/UX Design", 2)],
            "interests": "Generative Art, Web Performance, Design Systems",
            "evidence": ("Portfolio Website", "https://maya.dev", "Built design system with 50+ components")
        },
        {
            "name": "Rohan Deshmukh",
            "email": "rohan@teamweave.dev",
            "role": "backend",
            "bio": "Backend engineer passionate about high-throughput APIs and async architectures.",
            "skills": [("Python", 4), ("FastAPI", 4), ("PostgreSQL", 3), ("Docker & Cloud", 3)],
            "interests": "Distributed Systems, Microservices, Security",
            "evidence": ("FastAPI Core Boilerplate", "https://github.com/rohan/fastapi-pack", "Open-source template with 200+ stars")
        },
        {
            "name": "Priya Nair",
            "email": "priya@teamweave.dev",
            "role": "ai_engineer",
            "bio": "Applied AI researcher focusing on multimodal models and explainable AI.",
            "skills": [("PyTorch", 4), ("Machine Learning", 4), ("Python", 3), ("LLM Engineering", 4)],
            "interests": "Explainable AI, Agentic Workflows, Neural Search",
            "evidence": ("Multimodal RAG Paper", "https://arxiv.org/abs/fake", "Published paper on latent retrieval")
        },
        {
            "name": "Ananya Sen",
            "email": "ananya@teamweave.dev",
            "role": "designer",
            "bio": "Product and visual designer with an eye for cartographic layouts and typography.",
            "skills": [("UI/UX Design", 4), ("Figma", 4), ("Tailwind CSS", 2)],
            "interests": "Cartography, Micro-interactions, Accessibility",
            "evidence": ("Figma Community UI Kit", "https://figma.com/@ananya", "Living Weave design token collection")
        },
        {
            "name": "Kabir Mehta",
            "email": "kabir@teamweave.dev",
            "role": "fullstack",
            "bio": "Full-stack developer enjoying the intersection of Python backends and modern React.",
            "skills": [("React", 3), ("Python", 3), ("FastAPI", 3), ("TypeScript", 2)],
            "interests": "Full Stack Web, Collaborative Whiteboards",
            "evidence": ("SaaS MVP Launch", "https://kabir.app", "Built end-to-end event tracker")
        },
        {
            "name": "Tanvi Rao",
            "email": "tanvi@teamweave.dev",
            "role": "ml_engineer",
            "bio": "Data scientist exploring graph neural networks and team formation algorithms.",
            "skills": [("Machine Learning", 3), ("Python", 3), ("PostgreSQL", 2)],
            "interests": "Graph Algorithms, Data Analytics",
            "evidence": ("Kaggle Expert Notebook", "https://kaggle.com/tanvi", "Top 5% finish in tabular challenge")
        },
        {
            "name": "Devansh Gupta",
            "email": "devansh@teamweave.dev",
            "role": "devops",
            "bio": "Infrastructure enthusiast who makes deployments seamless with Docker & CI/CD.",
            "skills": [("Docker & Cloud", 4), ("Python", 2), ("PostgreSQL", 3)],
            "interests": "Cloud Native, Observability, Serverless",
            "evidence": ("Kubernetes Cluster Setup", "https://github.com/devansh/k8s", "GitOps deployment configuration")
        },
        {
            "name": "Neha Joshi",
            "email": "neha@teamweave.dev",
            "role": "frontend",
            "bio": "Creative technologist building accessible interactive canvas animations.",
            "skills": [("React", 3), ("Tailwind CSS", 3), ("UI/UX Design", 2)],
            "interests": "Interactive Graphics, SVG Animation",
            "evidence": ("Interactive Canvas Demo", "https://codepen.io/neha", "Smooth spring physics visualizations")
        },
        {
            "name": "Arjun Varma",
            "email": "arjun@teamweave.dev",
            "role": "product",
            "bio": "Product manager bridging customer needs, engineering velocity, and pitch delivery.",
            "skills": [("Product Strategy", 4), ("Python", 1), ("UI/UX Design", 2)],
            "interests": "Product Discovery, Lean Startups, User Research",
            "evidence": ("Hackathon Winning Pitch", "https://slides.com/arjun", "First place pitch deck at FinTech Sprint")
        },
        {
            "name": "Ishita Saxena",
            "email": "ishita@teamweave.dev",
            "role": "backend",
            "bio": "Junior developer eager to contribute clean Python code and learn from senior peers.",
            "skills": [("Python", 2), ("FastAPI", 2), ("PostgreSQL", 1)],
            "interests": "API Development, Open Source",
            "evidence": ("REST API Course Capstone", "https://github.com/ishita/crud", "Task management API with JWT")
        },
        {
            "name": "Vikram Sethi",
            "email": "vikram@teamweave.dev",
            "role": "frontend",
            "bio": "Budding frontend developer enthusiastic about Tailwind and responsive designs.",
            "skills": [("React", 2), ("Tailwind CSS", 2)],
            "interests": "Responsive Design, CSS Grid, Micro-interactions",
            "evidence": ("Landing Page Collection", "https://vikram.design", "Five responsive landing pages")
        },
        {
            "name": "Zoya Khan",
            "email": "zoya@teamweave.dev",
            "role": "ai_engineer",
            "bio": "Natural Language Processing enthusiast working on local LLM quantization.",
            "skills": [("Python", 3), ("LLM Engineering", 3), ("Machine Learning", 2)],
            "interests": "Local LLMs, Open Weights Models",
            "evidence": ("Model Evaluation Benchmark", "https://huggingface.co/zoya", "Fine-tuned Gemma adapter")
        }
    ]

    participant_users = []
    for p in participants_data:
        user = User(
            email=p["email"],
            hashed_password=hash_password("password123"),
            full_name=p["name"],
            role=UserRole.PARTICIPANT,
            bio=p["bio"],
            preferred_roles=p["role"],
            interests=p["interests"],
            timezone="Asia/Kolkata"
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        participant_users.append(user)

        # Add skills
        for s_name, level in p["skills"]:
            s_obj = skill_objs.get(s_name)
            if s_obj:
                us = UserSkill(
                    user_id=user.id,
                    skill_id=s_obj.id,
                    proficiency_level=level,
                    evidence_type=EvidenceType.EVIDENCE_LINKED if level >= 3 else EvidenceType.SELF_REPORTED,
                    verified=(level >= 3)
                )
                session.add(us)

        # Add evidence
        if "evidence" in p:
            title, url, desc = p["evidence"]
            ev = Evidence(
                user_id=user.id,
                title=title,
                url=url,
                description=desc,
                evidence_kind="project"
            )
            session.add(ev)

        session.commit()

    # 4. Seed Hackathon Event
    now = datetime.utcnow()
    event = Event(
        organizer_id=org.id,
        name="Living Weave Hackathon 2026",
        description="An intelligent hackathon bringing together engineers, designers, and AI specialists to weave next-generation collaborative systems.",
        category="hackathon",
        start_date=now + timedelta(days=2),
        end_date=now + timedelta(days=4),
        registration_deadline=now + timedelta(days=1),
        min_team_size=3,
        max_team_size=4,
        participation_mode="hybrid",
        status=EventStatus.OPEN
    )
    session.add(event)
    session.commit()
    session.refresh(event)

    # 5. Add Event Requirements
    requirements_specs = [
        ("React", RequirementPriority.REQUIRED, 2, 1, "Must have at least one frontend builder capable of delivering UI components."),
        ("Python", RequirementPriority.REQUIRED, 2, 1, "Must have at least one backend engineer for core API services."),
        ("UI/UX Design", RequirementPriority.PREFERRED, 2, 1, "Helpful to have dedicated design expertise for polished user flow."),
        ("Machine Learning", RequirementPriority.PREFERRED, 2, 1, "Recommended for teams implementing intelligent capabilities.")
    ]

    for s_name, prio, min_prof, people, exp in requirements_specs:
        s_obj = skill_objs.get(s_name)
        if s_obj:
            req = EventRequirement(
                event_id=event.id,
                skill_id=s_obj.id,
                priority=prio,
                min_proficiency=min_prof,
                people_needed=people,
                explanation=exp
            )
            session.add(req)
    session.commit()

    # 6. Register all 12 participants into the event
    for p_user in participant_users:
        mem = EventMembership(
            event_id=event.id,
            user_id=p_user.id,
            status=MembershipStatus.ACTIVE,
            preferred_role=p_user.preferred_roles,
            availability=json.dumps(["weekend_full", "weekday_evening"]),
            event_goals="Win best technical innovation and learn cross-disciplinary collaboration."
        )
        session.add(mem)
    session.commit()

    # 7. Seed Daily Challenges
    challenges_data = [
        {
            "question": "In React 18+, which hook is best suited for deferring non-urgent UI updates to keep inputs responsive?",
            "options": json.dumps(["useDeferredValue", "useMemo", "useCallback", "useLayoutEffect"]),
            "correct_index": 0,
            "skill_category": "frontend",
            "difficulty": "medium",
            "explanation": "useDeferredValue allows React to defer rendering a part of the UI tree, ensuring the main user interactions remain fluid."
        },
        {
            "question": "What is the primary benefit of FastAPI's dependency injection system (Depends)?",
            "options": json.dumps([
                "It automatically compiles Python to C++",
                "It enables clean, testable code reuse for db sessions and auth guards",
                "It removes the need for Pydantic models",
                "It runs queries in parallel threads by default"
            ]),
            "correct_index": 1,
            "skill_category": "backend",
            "difficulty": "easy",
            "explanation": "FastAPI's Depends system provides modular, reusable fixtures for request validation, authorization checks, and database session management."
        },
        {
            "question": "In Vector Search / RAG applications, why is cosine similarity commonly preferred over Euclidean distance?",
            "options": json.dumps([
                "Cosine similarity is unaffected by text length and focuses on vector orientation/angle",
                "Euclidean distance cannot handle negative numbers",
                "Cosine similarity runs on GPUs while Euclidean only runs on CPUs",
                "Euclidean distance cannot be normalized"
            ]),
            "correct_index": 0,
            "skill_category": "ai_ml",
            "difficulty": "medium",
            "explanation": "Cosine similarity measures the angle between vectors, capturing semantic alignment regardless of embedding magnitude differences caused by token length."
        },
        {
            "question": "According to the Living Weave design philosophy, what distinguishes honest gamification from manipulative gamification?",
            "options": json.dumps([
                "Honest gamification rewards active engagement and real consistency without pretending it measures absolute technical skill",
                "Honest gamification uses more spinning wheels and gold coins",
                "Honest gamification gives higher scores to people with more GitHub stars",
                "Honest gamification automatically ranks beginners lower"
            ]),
            "correct_index": 0,
            "skill_category": "design",
            "difficulty": "easy",
            "explanation": "Honest gamification clearly distinguishes streak/participation activity from capability assessment, avoiding false credentialism."
        }
    ]

    for c in challenges_data:
        dc = DailyChallenge(
            question=c["question"],
            options=c["options"],
            correct_index=c["correct_index"],
            skill_category=c["skill_category"],
            difficulty=c["difficulty"],
            explanation=c["explanation"]
        )
        session.add(dc)
    session.commit()

    # 8. Seed Badge Definitions
    badges_data = [
        {"name": "First Step", "description": "Completed your first daily skill challenge.", "icon": "sparkles", "criteria": "first_challenge"},
        {"name": "Consistent Weaver", "description": "Maintained a 3-day daily learning streak.", "icon": "flame", "criteria": "3_day_streak"},
        {"name": "Skill Pioneer", "description": "Declared and linked evidence for 3 or more capabilities.", "icon": "shield-check", "criteria": "3_verified_skills"},
        {"name": "Balanced Collaborator", "description": "Successfully completed a team formation cycle.", "icon": "users", "criteria": "team_joined"},
    ]

    for b in badges_data:
        bd = BadgeDefinition(
            name=b["name"],
            description=b["description"],
            icon=b["icon"],
            criteria=b["criteria"]
        )
        session.add(bd)
    session.commit()

    return {
        "status": "success",
        "message": "Demo environment populated successfully",
        "organizer_email": "organizer@teamweave.dev",
        "participant_email": "maya@teamweave.dev",
        "demo_password": "password123",
        "event_id": event.id,
        "participant_count": len(participant_users)
    }
