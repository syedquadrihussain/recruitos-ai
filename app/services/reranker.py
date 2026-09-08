def rerank_candidates(candidates, required_skills):

    for candidate in candidates:

        score = 0

        for skill in required_skills:

            if skill in candidate["skills"]:
                score += 1

        candidate["score"] = score

    return candidates