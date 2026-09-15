from app.services.jd_parser import parse_jd
from app.services.semantic_matcher import calculate_semantic_score


def check_candidate(
    candidate,
    jd_text,
    resume_text=None
):
    jd = parse_jd(jd_text)

    must_have = jd["must_have"]
    nice_to_have = jd["nice_to_have"]
    skill_weights = jd["skill_weights"]

    qualified = True
    reasons = []
    matched_skills = []
    matched_experience = []
    must_have_results = []

    total_score = 0
    experience_closeness = []

    # --------------------------------------------------
    # CANDIDATE SKILLS
    # --------------------------------------------------

    candidate_skills = {
        skill.lower()
        for skill in candidate.get("skills", [])
    }

    # --------------------------------------------------
    # CANDIDATE ROLES
    # --------------------------------------------------

    candidate_roles = {
        role.lower()
        for role in candidate.get("roles", [])
    }

    # --------------------------------------------------
    # CANDIDATE EXPERIENCE
    # --------------------------------------------------

    candidate_experience = {
        skill.lower(): years
        for skill, years
        in candidate.get("experience", {}).items()
    }

    # --------------------------------------------------
    # HELPER
    # --------------------------------------------------
    #
    # A requirement can be satisfied when it exists
    # either as a candidate skill or as a candidate role.
    #
    # Example:
    #
    # JD:
    # Business Development Manager
    #
    # Candidate:
    # roles:
    # Business Development Manager
    #
    # This should count as a match even if the
    # skills list only contains "Business Development".

    def candidate_has_requirement(skill):
        skill_lower = skill.lower()

        return (
            skill_lower in candidate_skills
            or skill_lower in candidate_roles
        )

    # --------------------------------------------------
    # MUST-HAVE SKILLS
    # --------------------------------------------------

    for skill, required_experience in must_have.items():

        candidate_has_skill = candidate_has_requirement(
            skill
        )

        candidate_skill_experience = (
            candidate_experience.get(
                skill.lower()
            )
        )

        # --------------------------------------------------
        # Required experience specified
        # --------------------------------------------------

        if required_experience > 0:

            if not candidate_has_skill:

                qualified = False

                must_have_results.append({
                    "skill": skill,
                    "required": required_experience,
                    "candidate": "Skill/role not found",
                    "status": "FAIL",
                    "gap": None
                })

                reasons.append(
                    f"{skill}: Skill or relevant role "
                    f"not found in candidate data"
                )

                continue

            if (
                candidate_skill_experience is not None
                and candidate_skill_experience
                >= required_experience
            ):

                matched_skills.append(skill)

                matched_experience.append(
                    f"{skill}: "
                    f"{candidate_skill_experience} years"
                )

                must_have_results.append({
                    "skill": skill,
                    "required": required_experience,
                    "candidate": candidate_skill_experience,
                    "status": "PASS",
                    "gap": 0
                })

                total_score += skill_weights[skill]

                experience_closeness.append(1.0)

            else:

                qualified = False

                if candidate_skill_experience is None:

                    candidate_value = (
                        "Years not explicitly available"
                    )

                    gap = None

                    reasons.append(
                        f"{skill}: Required "
                        f"{required_experience} years, "
                        f"candidate experience not explicitly available"
                    )

                else:

                    candidate_value = (
                        candidate_skill_experience
                    )

                    gap = (
                        required_experience
                        - candidate_skill_experience
                    )

                    reasons.append(
                        f"{skill}: Required "
                        f"{required_experience} years, "
                        f"candidate has "
                        f"{candidate_skill_experience} years"
                    )

                must_have_results.append({
                    "skill": skill,
                    "required": required_experience,
                    "candidate": candidate_value,
                    "status": "FAIL",
                    "gap": gap
                })

                if (
                    candidate_skill_experience is not None
                    and required_experience > 0
                ):

                    closeness = (
                        candidate_skill_experience
                        / required_experience
                    )

                    experience_closeness.append(
                        closeness
                    )

        # --------------------------------------------------
        # Required experience NOT specified
        # --------------------------------------------------

        else:

            if candidate_has_skill:

                matched_skills.append(skill)

                if candidate_skill_experience is not None:

                    matched_experience.append(
                        f"{skill}: "
                        f"{candidate_skill_experience} years"
                    )

                    experience_value = (
                        candidate_skill_experience
                    )

                else:

                    matched_experience.append(
                        f"{skill}: "
                        f"Years not explicitly available"
                    )

                    experience_value = (
                        "Years not explicitly available"
                    )

                must_have_results.append({
                    "skill": skill,
                    "required": "Not specified",
                    "candidate": experience_value,
                    "status": "PASS",
                    "gap": 0
                })

                total_score += skill_weights[skill]

            else:

                qualified = False

                must_have_results.append({
                    "skill": skill,
                    "required": "Not specified",
                    "candidate": "Skill/role not found",
                    "status": "FAIL",
                    "gap": None
                })

                reasons.append(
                    f"{skill}: Skill or relevant role "
                    f"not found in candidate data"
                )

    # --------------------------------------------------
    # NICE-TO-HAVE SKILLS
    # --------------------------------------------------

    nice_to_have_score = 0

    for skill in nice_to_have:

        if candidate_has_requirement(skill):

            nice_to_have_score += 1

            matched_skills.append(skill)

            total_score += skill_weights[skill]

    # --------------------------------------------------
    # RULE-BASED SCORE
    # --------------------------------------------------

    max_score = sum(
        skill_weights.values()
    )

    if max_score > 0:

        rule_based_score = (
            total_score / max_score
        ) * 100

    else:

        rule_based_score = 0

    # --------------------------------------------------
    # EXPERIENCE CLOSENESS SCORE
    # --------------------------------------------------

    if experience_closeness:

        experience_closeness_score = (
            sum(experience_closeness)
            / len(experience_closeness)
        ) * 100

    else:

        experience_closeness_score = 0

    # --------------------------------------------------
    # SEMANTIC SCORE
    # --------------------------------------------------

    semantic_score = 0
    semantic_matches = []

    if resume_text:

        semantic_result = calculate_semantic_score(
            resume_text,
            jd_text
        )

        semantic_score = (
            semantic_result["semantic_score"]
        )

        semantic_matches = (
            semantic_result["matched_chunks"]
        )

    # --------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------
    #
    # Semantic relevance contributes to the score,
    # but NEVER overrides mandatory qualification.

    final_score = (
        rule_based_score * 0.70
    ) + (
        semantic_score * 0.30
    )

    # --------------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------------

    if qualified and final_score >= 90:

        recommendation = "Strong Match"

    elif qualified and final_score >= 70:

        recommendation = "Good Match"

    elif not qualified and semantic_score >= 70:

        recommendation = (
            "Potential Match - "
            "Mandatory Requirements Not Met"
        )

    elif semantic_score >= 70:

        recommendation = "Potential Match"

    else:

        recommendation = "Not an Exact Match"

    # --------------------------------------------------
    # SEMANTIC REASON
    # --------------------------------------------------

    if semantic_score >= 80:

        reasons.append(
            "Resume content is highly relevant "
            "to the job description"
        )

    elif semantic_score >= 60:

        reasons.append(
            "Resume content is moderately relevant "
            "to the job description"
        )

    else:

        reasons.append(
            "Resume content has limited semantic "
            "relevance to the job description"
        )

    # --------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------

    return {
        "name": candidate["name"],
        "overall_experience": candidate[
            "overall_experience"
        ],
        "qualified": qualified,
        "recommendation": recommendation,
        "reasons": reasons,
        "must_have_results": must_have_results,
        "nice_to_have_score": nice_to_have_score,
        "total_score": total_score,
        "rule_based_score": round(
            rule_based_score,
            1
        ),
        "semantic_score": round(
            semantic_score,
            1
        ),
        "final_score": round(
            final_score,
            1
        ),
        "experience_closeness_score": round(
            experience_closeness_score,
            1
        ),
        "matched_skills": matched_skills,
        "matched_experience": matched_experience,
        "semantic_matches": semantic_matches
    }