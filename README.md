# TeamWeave — Living Weave 🧵

> **Intelligent, Explainable Skill-Based Team Formation Platform**  
> *Built for hackathons, engineering studios, and multi-disciplinary project formation.*

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.2+-61DAFB.svg)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8.3+-646CFF.svg)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.4+-38B2AC.svg)](https://tailwindcss.com)
[![Tests](https://img.shields.io/badge/Pytest-Passing-brightgreen.svg)]()

---

## 🌟 What is TeamWeave?

Traditional hackathons form teams through blind random draws or popularity-driven cliques, leading to skill imbalances (e.g., four backend engineers with no UI developer) or isolating beginners.

**TeamWeave (Codename: Living Weave)** is an end-to-end intelligent team formation platform that replaces opaque grouping with **transparent, requirement-level capability matching**:
- **Requirement-Level Coverage:** Evaluates teams against event requirements (e.g. React L2+, Python L2+, Figma L2+) rather than headcount.
- **Separation of Ability & Evidence:** Participants declare skills across a 4-tier proficiency model (`Exploring`, `Developing`, `Independent`, `Advanced`). External evidence (GitHub, Figma, papers) supports declarations without penalizing non-traditional developers.
- **Deterministic & Auditable Matchmaking:** Greedy allocation with pairwise swap optimization produces explainable, reproducible rosters.
- **The Team Blueprint:** A signature visual component displaying quality scores (0–100), requirement coverage status (Covered, Partially Covered, Missing), and natural language rationale.
- **Graceful Reshuffling:** Quantifies lost capabilities when a member withdraws and ranks unassigned candidates with explainable impact scores for one-click approval.
- **Honest Gamification:** Daily challenges, streak counters, and milestone badges that encourage consistency without metric inflation.

---

## 🚀 Instant Demonstration Credentials

The platform comes pre-seeded with a comprehensive demo environment ("Living Weave Hackathon 2026") and 12 realistic participants. Use the **Quick Persona Switcher** in the top navigation bar or log in with:

| Persona | Role | Email | Password |
|---|---|---|---|
| **Dr. Aarav Patel** | Organizer | `organizer@teamweave.dev` | `password123` |
| **Maya Sharma** | Frontend Specialist (React L4) | `maya@teamweave.dev` | `password123` |
| **Rohan Deshmukh** | Backend Specialist (FastAPI L4) | `rohan@teamweave.dev` | `password123` |
| **Priya Nair** | AI/ML Researcher (PyTorch L4) | `priya@teamweave.dev` | `password123` |
| **Ananya Sen** | UI/UX Designer (Figma L4) | `ananya@teamweave.dev` | `password123` |

---

## 🛠️ Tech Stack & Architecture

- **Backend:** Python 3.10+, FastAPI, SQLModel (SQLAlchemy 2.0 + Pydantic v2), python-jose (JWT), passlib/bcrypt.
- **Frontend:** React 19, Vite, Tailwind CSS, Lucide Icons, Space Grotesk & Inter typography.
- **Database:** SQLite (default local file `backend/teamweave.db`) with zero-friction migration path to PostgreSQL.
- **Design System:** Living Weave (Warm paper canvas `#F6F4ED`, deep ink `#182724`, woven teal `#17A982`, cobalt `#536FF1`, coral `#ED8B76`, gold `#D5A747`).

---

## 🏃 Quickstart Guide

### 1. Backend Server
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend runs on `http://127.0.0.1:8000` with Swagger docs at `http://127.0.0.1:8000/docs`.*

### 2. Frontend Development Server
```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```
*Frontend runs on `http://127.0.0.1:5173`.*

### 3. Running Automated Tests
```bash
cd backend
python -m pytest -v
```

---

## 📚 In-Depth Documentation

- [Product Specification](docs/PRODUCT_SPEC.md)
- [Design System Guide](docs/DESIGN_SYSTEM.md)
- [Matching Algorithm Specification](docs/MATCHING_ALGORITHM.md)
- [Database Schema & Data Model](docs/DATA_MODEL.md)
- [Test Plan & Verification Report](docs/TEST_PLAN.md)
