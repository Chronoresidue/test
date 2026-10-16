# TeamWeave Matching Algorithm Specification

**Product Codename:** Living Weave  
**Module:** `backend/app/matching_engine.py`  
**Version:** 1.0.0 (Deterministic Greedy Allocation with Pairwise Improvement Pass)

---

## 1. Overview and Core Philosophy

Traditional hackathon team formation either relies on random assignment or naive matchmaking that optimizes solely for total headcounts or self-reported popularity. 

TeamWeave takes an **explainable, capability-centric approach**:
- **Requirement-Level Coverage:** Each team's viability is evaluated against specific event requirements (e.g. at least one React L2+ engineer, at least one Python L2+ engineer).
- **Separation of Ability and Evidence:** Declared proficiency levels (1–4) determine capability matching. External evidence (repos, papers, certificates) confirms support without unfairly penalizing beginners or participants from non-traditional backgrounds.
- **Deterministic & Auditable:** Identical participant pools and event configurations produce identical team allocations.
- **Explainability First:** Natural language explanations accompany every formed team, detailing why members were placed together and which requirements each member satisfies.

---

## 2. Operations Supported

### Operation A — Candidate Recommendation for Existing Teams
When a team has open spots or seeks a specific specialist:
1. Filters eligible, registered participants not currently in a team.
2. Identifies unfilled or weakly covered requirements for the target team.
3. Ranks candidates by marginal coverage improvement and preferred role alignment.
4. Generates an explainable impact breakdown for the organizer.

### Operation B — Pool Team Formation (Primary Hackathon Matchmaking)
When forming teams from an event participant pool:
1. **Hard Constraints Check:**
   - Participant must be registered (`status = 'active'`).
   - Team sizes strictly bound by `[min_team_size, max_team_size]`.
   - Each participant belongs to at most one team per event.
2. **Scarcity Analysis:**
   - Computes scarcity for each required skill across the participant pool.
   - Requirements with the fewest qualifying participants are prioritized first.
3. **Greedy Seeding Pass:**
   - Distributes scarce required capabilities across teams to prevent clustering of rare skills in a single team.
4. **Complementary Balancing Pass:**
   - Places remaining participants into teams using marginal soft quality score improvements (role diversity, availability compatibility, shared interests).
5. **Deterministic Pairwise Swap Improvement Pass:**
   - Evaluates candidate participant swaps between teams.
   - Accepts swaps only if the total quality index strictly increases without violating any hard constraints.
6. **Requirement-Level Coverage Evaluation:**
   - Categorizes each requirement as **Covered**, **Partially Covered**, or **Missing**.
7. **Natural Language Rationale Generation:**
   - Produces readable explanations of the team's composition and coverage.

### Operation C — Reshuffling & Replacement on Withdrawal
When a team member withdraws or leaves:
1. Marks membership state as `left`.
2. Computes the exact capability delta lost by the team.
3. Evaluates unassigned participants against the newly created gaps.
4. Computes an impact score (0–100%) and explanatory text.
5. Surfaces ranked replacement candidates to the organizer for one-click approval and transactional membership updates.

---

## 3. Mathematical & Scoring Model

### Provisional Soft-Score Weights
The soft quality score (0–100) balances multi-disciplinary synergy:
- **55% Skill Coverage & Complementary Capabilities:** Evaluates required and preferred skill targets met with minimum proficiency thresholds.
- **20% Availability Compatibility:** Evaluates overlapping work schedule blocks (e.g., weekends, weekday evenings).
- **10% Role Diversity & Alignment:** Rewards diverse contribution roles (frontend, backend, AI/ML, design, DevOps).
- **10% Shared Interests & Goals:** Encourages teams with aligned project ambitions.
- **5% Voluntary Collaboration Preferences:** Respects mutual preferences when specified.

### Requirement Coverage States
- **Covered (Green):** Team has at least `people_needed` participants meeting `min_proficiency`.
- **Partially Covered (Amber):** Capabilities exist within the team, but headcount or target proficiency is partially under the threshold.
- **Missing (Coral):** No team member possesses the declared skill.
- **Needs Review (Neutral):** Information is insufficient or unverified.
