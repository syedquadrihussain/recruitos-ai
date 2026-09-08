from app.services.jd_parser import parse_jd


def check_candidate(candidate, jd_text):

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
    # Match Score
    # --------------------------------

    max_score = sum(skill_weights.values())

    if max_score > 0:

        match_score = (
            total_score / max_score
        ) * 100

    else:

        match_score = 0

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
    # Recommendation
    # --------------------------------

    if qualified and match_score >= 90:

        recommendation = "Strong Match"

    elif qualified:

        recommendation = "Good Match"

    else:

        recommendation = "Not an Exact Match"

    return {
        "name": candidate["name"],
        "overall_experience": candidate["overall_experience"],
        "qualified": qualified,
        "recommendation": recommendation,
        "reasons": reasons,
        "must_have_results": must_have_results,
        "nice_to_have_score": nice_to_have_score,
        "total_score": total_score,
        "match_score": round(match_score, 1),
        "experience_closeness_score": round(
            experience_closeness_score,
            1
        ),
        "matched_skills": matched_skills,
        "matched_experience": matched_experience
    }