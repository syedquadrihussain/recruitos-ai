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

    # --------------------------------
    # Check Must Have Skills
    # --------------------------------

    for skill, required_experience in must_have.items():

        candidate_experience = candidate["experience"].get(
            skill,
            0
        )

        if candidate_experience >= required_experience:

            matched_skills.append(skill)

            matched_experience.append(
                f"{skill}: {candidate_experience} years"
            )

            must_have_results.append({
                "skill": skill,
                "required": required_experience,
                "candidate": candidate_experience,
                "status": "PASS",
                "gap": 0
            })

            total_score += skill_weights[skill]

            experience_closeness.append(1.0)

        else:

            qualified = False

            gap = required_experience - candidate_experience

            reasons.append(
                f"{skill}: Required {required_experience} years, "
                f"candidate has {candidate_experience} years"
            )

            must_have_results.append({
                "skill": skill,
                "required": required_experience,
                "candidate": candidate_experience,
                "status": "FAIL",
                "gap": gap
            })

            if required_experience > 0:

                closeness = (
                    candidate_experience / required_experience
                )

                experience_closeness.append(closeness)

            else:

                experience_closeness.append(0)

    # --------------------------------
    # Nice to Have Skills
    # --------------------------------

    nice_to_have_score = 0

    for skill in nice_to_have:

        if skill in candidate.get("skills", []):

            nice_to_have_score += 1

            matched_skills.append(skill)

            total_score += skill_weights[skill]

    # --------------------------------
    # Rule-Based Match Score
    # --------------------------------

    max_score = sum(skill_weights.values())

    if max_score > 0:

        rule_based_score = (
            total_score / max_score
        ) * 100

    else:

        rule_based_score = 0

    # --------------------------------
    # Experience Closeness Score
    # --------------------------------

    if experience_closeness:

        experience_closeness_score = (
            sum(experience_closeness)
            / len(experience_closeness)
        ) * 100

    else:

        experience_closeness_score = 0

    # --------------------------------
    # Semantic Matching
    # --------------------------------

    semantic_score = 0
    semantic_matches = []

    if resume_text:

        semantic_result = calculate_semantic_score(
            resume_text,
            jd_text
        )

        semantic_score = semantic_result[
            "semantic_score"
        ]

        semantic_matches = semantic_result[
            "matched_chunks"
        ]

    # --------------------------------
    # Final Combined Score
    # --------------------------------

    final_score = (
        rule_based_score * 0.70
    ) + (
        semantic_score * 0.30
    )

    # --------------------------------
    # Recommendation
    # --------------------------------

    if qualified and final_score >= 90:

        recommendation = "Strong Match"

    elif qualified and final_score >= 70:

        recommendation = "Good Match"

    elif semantic_score >= 70:

        recommendation = "Potential Match"

    else:

        recommendation = "Not an Exact Match"

    # --------------------------------
    # Semantic Reason
    # --------------------------------

    if semantic_score >= 80:

        reasons.append(
            "Resume content is highly relevant to the job description"
        )

    elif semantic_score >= 60:

        reasons.append(
            "Resume content is moderately relevant to the job description"
        )

    else:

        reasons.append(
            "Resume content has limited semantic relevance to the job description"
        )

    return {
        "name": candidate["name"],
        "overall_experience": candidate["overall_experience"],
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