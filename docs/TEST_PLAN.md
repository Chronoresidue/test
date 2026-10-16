# TeamWeave — Quality Assurance & Test Plan

**Test Engine:** Pytest 7.4.3 + FastAPI TestClient  
**Suite Location:** `backend/tests/test_teamweave.py`  
**Frontend Verification:** Production Vite Bundle (`vite build`)

---

## 1. Test Matrix and Verification Coverage

| Test Area | Target Scenario | Verification Method | Status |
|---|---|---|---|
| **Healthcheck** | Service availability & codename verification | `GET /api/health` returns status: healthy, codename: Living Weave | PASSED |
| **Authentication** | JWT creation, bcrypt verification, role isolation | `POST /api/auth/login`, `GET /api/auth/me` with Bearer token | PASSED |
| **Matching Determinism** | Same participant pool and requirements yield identical team assignments | Pure function execution of `form_teams_operation_b` compared across runs | PASSED |
| **Gamification Flow** | Question delivery, answer submission, streak calculation | `GET /api/gamification/daily-challenge`, `POST /submit` | PASSED |
| **Reshuffling & Replacement** | Member withdrawal, lost capability delta, ranked candidate scoring | `withdraw_team_member` and `get_replacement_candidates` | PASSED |
| **Frontend Production Build** | Zero syntax, TypeScript, or asset bundling errors | `npm run build` generates optimized bundle in 1.00s | PASSED |

---

## 2. Running Automated Tests

To run the backend test suite:
```bash
cd backend
python -m pytest -v
```

To run frontend build checks:
```bash
cd frontend
npm run build
```
