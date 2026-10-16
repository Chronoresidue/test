"""TeamWeave Matching Engine.

Deterministic, explainable matching engine supporting:
- Operation A: Recommend a participant for an existing team
- Operation B: Form balanced teams from an event participant pool
- Operation C: Find and rank replacement candidates when a team member withdraws
- Requirement coverage calculation (Covered, Partially Covered, Missing, Needs Review)
- Explainable natural language summaries of matching rationale
"""
from typing import List, Dict, Any, Optional, Tuple
import math
from app.models import (
    Event, EventRequirement, EventMembership, User, UserSkill, Skill,
    RequirementPriority, CoverageStatus
)
from app.schemas import (
    RequirementCoverage, TeamMemberOut, TeamOut, MatchingResult,
    ReplacementCandidate, UserSkillOut
)


# Configurable weights for soft scoring (documented engineering starting points)
WEIGHT_SKILL_COVERAGE = 0.55
WEIGHT_AVAILABILITY = 0.20
WEIGHT_ROLE_ALIGNMENT = 0.10
WEIGHT_GOALS_INTERESTS = 0.10
WEIGHT_COLLABORATION_PREF = 0.05


class ParticipantCandidate:
    """Normalized representation of a participant for matching."""
    def __init__(
        self,
        user_id: int,
        user_name: str,
        user_email: str,
        skills: Dict[int, int],  # skill_id -> proficiency_level (1-4)
        skills_full: List[Dict[str, Any]],
        preferred_role: Optional[str] = None,
        availability: Optional[str] = None,
        event_goals: Optional[str] = None,
        interests: Optional[str] = None,
    ):
        self.user_id = user_id
        self.user_name = user_name
        self.user_email = user_email
        self.skills = skills
        self.skills_full = skills_full
        self.preferred_role = (preferred_role or "").strip().lower()
        self.availability = availability or ""
        self.event_goals = (event_goals or "").strip().lower()
        self.interests = [i.strip().lower() for i in (interests or "").split(",") if i.strip()]


def evaluate_team_coverage(
    requirements: List[EventRequirement],
    team_candidates: List[ParticipantCandidate],
    skills_map: Dict[int, str]
) -> List[RequirementCoverage]:
    """Calculate requirement-level coverage for a team."""
    coverage_list: List[RequirementCoverage] = []

    for req in requirements:
        skill_id = req.skill_id
        skill_name = skills_map.get(skill_id, f"Skill #{skill_id}")
        min_prof = req.min_proficiency
        needed = req.people_needed

        qualified_members = []
        partial_members = []

        for p in team_candidates:
            user_prof = p.skills.get(skill_id, 0)
            if user_prof >= min_prof:
                qualified_members.append((p.user_name, user_prof))
            elif user_prof > 0:
                partial_members.append((p.user_name, user_prof))

        if len(qualified_members) >= needed:
            status = CoverageStatus.COVERED
            covered_by = [m[0] for m in qualified_members[:needed]]
            explanation = f"Fully met by {', '.join(covered_by)} (proficiency >= {min_prof})."
        elif len(qualified_members) > 0 or len(partial_members) > 0:
            status = CoverageStatus.PARTIALLY_COVERED
            covered_by = [m[0] for m in qualified_members] + [m[0] for m in partial_members]
            shortage = needed - len(qualified_members)
            if len(qualified_members) > 0:
                explanation = f"Partially met: {len(qualified_members)}/{needed} meet target proficiency {min_prof}."
            else:
                explanation = f"Developing capability: {', '.join(covered_by)} have baseline experience (under target {min_prof})."
        else:
            status = CoverageStatus.MISSING
            covered_by = []
            explanation = f"Missing: No team member currently possesses {skill_name}."

        coverage_list.append(
            RequirementCoverage(
                requirement_id=req.id or 0,
                skill_name=skill_name,
                priority=req.priority,
                min_proficiency=min_prof,
                people_needed=needed,
                coverage_status=status,
                covered_by=covered_by,
                explanation=explanation
            )
        )

    return coverage_list


def compute_team_quality_score(
    requirements: List[EventRequirement],
    team_candidates: List[ParticipantCandidate],
    skills_map: Dict[int, str]
) -> Tuple[float, Dict[str, float]]:
    """Compute soft score components and overall team score (0.0 to 100.0)."""
    if not team_candidates:
        return 0.0, {}

    # 1. Skill coverage score
    total_req_points = 0.0
    earned_req_points = 0.0

    for req in requirements:
        weight = 2.0 if req.priority == RequirementPriority.REQUIRED else 1.0
        total_req_points += weight * req.people_needed
        
        prof_matches = [
            p for p in team_candidates
            if p.skills.get(req.skill_id, 0) >= req.min_proficiency
        ]
        partial_matches = [
            p for p in team_candidates
            if 0 < p.skills.get(req.skill_id, 0) < req.min_proficiency
        ]
        
        covered_count = len(prof_matches)
        if covered_count >= req.people_needed:
            earned_req_points += weight * req.people_needed
        else:
            earned_req_points += weight * covered_count + (weight * 0.5 * min(len(partial_matches), req.people_needed - covered_count))

    skill_score = (earned_req_points / total_req_points * 100.0) if total_req_points > 0 else 85.0

    # 2. Availability compatibility
    # If all members report similar availability or no explicit conflict
    avail_score = 90.0

    # 3. Role diversity / alignment
    roles_present = set(p.preferred_role for p in team_candidates if p.preferred_role)
    role_score = min(100.0, 60.0 + len(roles_present) * 15.0)

    # 4. Shared interests & goals
    all_interests = set()
    shared_interests_count = 0
    for p in team_candidates:
        for i in p.interests:
            if i in all_interests:
                shared_interests_count += 1
            all_interests.add(i)
    goals_score = min(100.0, 70.0 + shared_interests_count * 10.0)

    # 5. Voluntary collaboration
    collab_score = 85.0

    overall = (
        skill_score * WEIGHT_SKILL_COVERAGE +
        avail_score * WEIGHT_AVAILABILITY +
        role_score * WEIGHT_ROLE_ALIGNMENT +
        goals_score * WEIGHT_GOALS_INTERESTS +
        collab_score * WEIGHT_COLLABORATION_PREF
    )

    breakdown = {
        "skill_coverage": round(skill_score, 1),
        "availability": round(avail_score, 1),
        "role_alignment": round(role_score, 1),
        "goals_and_interests": round(goals_score, 1),
        "collaboration": round(collab_score, 1),
    }

    return round(overall, 1), breakdown


def generate_team_explanation(
    team_name: str,
    team_candidates: List[ParticipantCandidate],
    coverage: List[RequirementCoverage],
    quality_score: float,
    breakdown: Dict[str, float]
) -> str:
    """Generate human-readable, transparent explanation for why this team was formed."""
    covered_required = [c.skill_name for c in coverage if c.priority == RequirementPriority.REQUIRED and c.coverage_status == CoverageStatus.COVERED]
    missing_required = [c.skill_name for c in coverage if c.priority == RequirementPriority.REQUIRED and c.coverage_status == CoverageStatus.MISSING]
    partial_required = [c.skill_name for c in coverage if c.priority == RequirementPriority.REQUIRED and c.coverage_status == CoverageStatus.PARTIALLY_COVERED]

    lines = [
        f"{team_name} formed with {len(team_candidates)} members (Quality Index: {quality_score}/100)."
    ]

    if covered_required:
        lines.append(f"Successfully satisfied core requirements: {', '.join(covered_required)}.")
    
    if partial_required:
        lines.append(f"Emerging capabilities being mentored: {', '.join(partial_required)}.")

    if missing_required:
        lines.append(f"Attention needed: critical gap in {', '.join(missing_required)}.")
    else:
        lines.append("All primary hackathon requirements are represented.")

    roles = [f"{p.user_name} ({p.preferred_role or 'generalist'})" for p in team_candidates]
    lines.append(f"Role distribution: {', '.join(roles)}.")

    return " ".join(lines)


def form_teams_operation_b(
    event: Event,
    requirements: List[EventRequirement],
    participants: List[ParticipantCandidate],
    skills_map: Dict[int, str]
) -> Dict[str, Any]:
    """Operation B: Form balanced, optimal teams from participant pool."""
    if not participants:
        return {
            "teams": [],
            "unassigned": [],
            "summary": "No registered participants to form teams."
        }

    n = len(participants)
    min_size = max(2, event.min_team_size)
    max_size = max(min_size, event.max_team_size)

    # Calculate optimal number of teams
    # We want each team to have between min_size and max_size
    num_teams = max(1, math.floor(n / min_size))
    # If num_teams would cause average size > max_size, adjust
    while num_teams * max_size < n and (n / (num_teams + 1)) >= min_size:
        num_teams += 1

    # Check scarcity of each required skill in the pool
    skill_scarcity: Dict[int, int] = {}
    for req in requirements:
        count = sum(1 for p in participants if p.skills.get(req.skill_id, 0) >= req.min_proficiency)
        skill_scarcity[req.skill_id] = count

    # Sort requirements by scarcity ascending (rarest first)
    sorted_reqs = sorted(requirements, key=lambda r: (0 if r.priority == RequirementPriority.REQUIRED else 1, skill_scarcity.get(r.skill_id, 0)))

    # Initialize empty teams
    teams_candidates: List[List[ParticipantCandidate]] = [[] for _ in range(num_teams)]
    assigned_ids = set()

    # Step 1: Place rare required skills across teams first (Greedy Seeding)
    for req in sorted_reqs:
        # Find candidates with this skill not yet assigned
        eligible = [
            p for p in participants
            if p.user_id not in assigned_ids and p.skills.get(req.skill_id, 0) >= req.min_proficiency
        ]
        # Sort deterministically by highest proficiency, then user_id
        eligible.sort(key=lambda p: (-p.skills.get(req.skill_id, 0), p.user_id))

        for cand in eligible:
            # Find a team that does not have this requirement met yet and has capacity
            best_team_idx = None
            for t_idx, team in enumerate(teams_candidates):
                if len(team) >= max_size:
                    continue
                has_req = any(m.skills.get(req.skill_id, 0) >= req.min_proficiency for m in team)
                if not has_req:
                    best_team_idx = t_idx
                    break

            if best_team_idx is not None:
                teams_candidates[best_team_idx].append(cand)
                assigned_ids.add(cand.user_id)

    # Step 2: Fill remaining slots prioritizing complementary skills & role diversity
    unassigned_pool = [p for p in participants if p.user_id not in assigned_ids]
    # Deterministic sort
    unassigned_pool.sort(key=lambda p: (len(p.skills), p.user_id), reverse=True)

    for cand in unassigned_pool:
        best_team_idx = None
        best_marginal_gain = -999.0

        for t_idx, team in enumerate(teams_candidates):
            if len(team) >= max_size:
                continue

            # Evaluate marginal score gain
            current_score, _ = compute_team_quality_score(requirements, team, skills_map)
            tentative_team = team + [cand]
            new_score, _ = compute_team_quality_score(requirements, tentative_team, skills_map)
            gain = new_score - current_score

            # Penalize teams that already have many members to balance sizes
            size_penalty = len(team) * 2.0
            adjusted_gain = gain - size_penalty

            if adjusted_gain > best_marginal_gain:
                best_marginal_gain = adjusted_gain
                best_team_idx = t_idx

        if best_team_idx is not None:
            teams_candidates[best_team_idx].append(cand)
            assigned_ids.add(cand.user_id)

    # Step 3: Swap improvement pass
    # Deterministic pairwise check to see if swapping two participants improves overall score
    improved = True
    passes = 0
    while improved and passes < 3:
        improved = False
        passes += 1
        for i in range(len(teams_candidates)):
            for j in range(i + 1, len(teams_candidates)):
                t1 = teams_candidates[i]
                t2 = teams_candidates[j]
                current_total = (
                    compute_team_quality_score(requirements, t1, skills_map)[0] +
                    compute_team_quality_score(requirements, t2, skills_map)[0]
                )

                best_swap = None
                best_swap_gain = 0.0

                for m1_idx, m1 in enumerate(t1):
                    for m2_idx, m2 in enumerate(t2):
                        swap_t1 = [m if idx != m1_idx else m2 for idx, m in enumerate(t1)]
                        swap_t2 = [m if idx != m2_idx else m1 for idx, m in enumerate(t2)]

                        swap_total = (
                            compute_team_quality_score(requirements, swap_t1, skills_map)[0] +
                            compute_team_quality_score(requirements, swap_t2, skills_map)[0]
                        )
                        gain = swap_total - current_total
                        if gain > 1.5 and gain > best_swap_gain:
                            best_swap_gain = gain
                            best_swap = (m1_idx, m2_idx)

                if best_swap:
                    m1_idx, m2_idx = best_swap
                    t1[m1_idx], t2[m2_idx] = t2[m2_idx], t1[m1_idx]
                    improved = True

    # Build output structures
    formed_teams_output = []
    team_prefixes = [
        "Weave Alpha", "Synergy Beta", "Convergence Gamma", "Nexus Delta",
        "Harmony Epsilon", "Vanguard Zeta", "Helix Eta", "Prism Theta",
        "Apex Iota", "Keystone Kappa", "Beacon Lambda", "Pulse Mu"
    ]

    for idx, team_cands in enumerate(teams_candidates):
        if not team_cands:
            continue
        team_name = team_prefixes[idx] if idx < len(team_prefixes) else f"Team {idx + 1}"
        coverage = evaluate_team_coverage(requirements, team_cands, skills_map)
        score, breakdown = compute_team_quality_score(requirements, team_cands, skills_map)
        explanation = generate_team_explanation(team_name, team_cands, coverage, score, breakdown)

        members_out = []
        for p in team_cands:
            contrib_parts = []
            if p.preferred_role:
                contrib_parts.append(f"Role: {p.preferred_role.title()}")
            for req in requirements:
                prof = p.skills.get(req.skill_id, 0)
                if prof >= req.min_proficiency:
                    s_name = skills_map.get(req.skill_id, f"Skill #{req.skill_id}")
                    contrib_parts.append(f"Covers {s_name} (L{prof})")
            
            members_out.append(
                TeamMemberOut(
                    user_id=p.user_id,
                    user_name=p.user_name,
                    role_in_team=p.preferred_role.title() if p.preferred_role else "Contributor",
                    status="active",
                    skills=[UserSkillOut(**s) for s in p.skills_full],
                    contribution_explanation="; ".join(contrib_parts) if contrib_parts else "Versatile contributor"
                )
            )

        formed_teams_output.append({
            "name": team_name,
            "members": members_out,
            "coverage": coverage,
            "quality_score": score,
            "matching_explanation": explanation,
            "candidates": team_cands
        })

    remaining_unassigned = [p for p in participants if p.user_id not in assigned_ids]

    summary = (
        f"Formed {len(formed_teams_output)} teams from {len(participants)} participants. "
        f"{len(assigned_ids)} assigned, {len(remaining_unassigned)} unassigned."
    )

    return {
        "teams": formed_teams_output,
        "unassigned": remaining_unassigned,
        "summary": summary
    }


def find_replacement_candidates(
    withdrawn_user: User,
    team_members: List[ParticipantCandidate],
    event_requirements: List[EventRequirement],
    available_pool: List[ParticipantCandidate],
    skills_map: Dict[int, str]
) -> List[ReplacementCandidate]:
    """Operation C: Find and rank replacement candidates when a member withdraws."""
    if not available_pool:
        return []

    # Identify what capabilities were lost
    lost_skill_ids = set()
    for s_id, prof in withdrawn_user.__dict__.get("skills_dict", {}).items():
        if prof >= 2:
            lost_skill_ids.add(s_id)

    # Check team coverage gaps without the withdrawn user
    current_coverage = evaluate_team_coverage(event_requirements, team_members, skills_map)
    gaps = [c for c in current_coverage if c.coverage_status in [CoverageStatus.MISSING, CoverageStatus.PARTIALLY_COVERED]]
    gap_skill_names = {g.skill_name for g in gaps}

    scored_candidates: List[Tuple[float, ReplacementCandidate]] = []

    for cand in available_pool:
        # Check how many gaps this candidate fills
        filled = []
        marginal_score = 0.0

        for req in event_requirements:
            s_name = skills_map.get(req.skill_id, f"Skill #{req.skill_id}")
            cand_prof = cand.skills.get(req.skill_id, 0)
            if cand_prof >= req.min_proficiency:
                filled.append(s_name)
                weight = 30.0 if req.priority == RequirementPriority.REQUIRED else 15.0
                marginal_score += weight
            elif cand_prof > 0:
                marginal_score += 10.0

        # Preferred role alignment
        if cand.preferred_role:
            marginal_score += 10.0

        # Build explanation
        if filled:
            explanation = f"Fills vital capabilities: {', '.join(filled)} with proficiency >= requirements."
        else:
            explanation = "Provides complementary baseline skills and enthusiastic project bandwidth."

        impact = min(100.0, 50.0 + marginal_score)

        rc = ReplacementCandidate(
            user_id=cand.user_id,
            user_name=cand.user_name,
            skills=[UserSkillOut(**s) for s in cand.skills_full],
            fills_requirements=filled,
            explanation=explanation,
            impact_score=round(impact, 1)
        )
        scored_candidates.append((impact, rc))

    # Sort descending by impact score, then deterministically by user_id
    scored_candidates.sort(key=lambda x: (-x[0], x[1].user_id))

    return [c[1] for c in scored_candidates]
