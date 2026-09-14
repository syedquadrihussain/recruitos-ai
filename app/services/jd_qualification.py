from app.services.jd_parser import parse_jd


def get_required_skills(jd_text):
    """
    Extract must-have skills from the Job Description.
    """

    jd = parse_jd(jd_text)

    return list(
        jd["must_have"].keys()
    )


def get_required_skill_experience(jd_text):
    """
    Extract required skills and their minimum
    years of experience from the Job Description.

    Example:

    Python - 5 years
    RAG - 2 years
    FastAPI - 2 years

    Returns:

    {
        "Python": 5,
        "RAG": 2,
        "FastAPI": 2
    }
    """

    jd = parse_jd(jd_text)

    return jd["must_have"]


def qualify_candidate(
    candidate,
    required_skills
):
    """
    Check whether a candidate has all required skills.

    This function is kept simple for backward
    compatibility with existing RecruitOS tests.
    """

    candidate_skills = {
        skill.lower()
        for skill in candidate["skills"]
    }

    for required_skill in required_skills:

        if required_skill.lower() not in candidate_skills:

            return False

    return True


def qualify_candidate_with_experience(
    candidate,
    required_skill_experience
):
    """
    Check whether a candidate has every required skill
    AND meets the minimum experience requirement.

    Example:

    Required:
    Python -> 5 years
    RAG -> 2 years
    FastAPI -> 2 years

    Candidate:
    Python -> 6 years
    RAG -> 2 years
    FastAPI -> 3 years

    Result:
    Qualified
    """

    candidate_skills = {
        skill.lower()
        for skill in candidate.get("skills", [])
    }

    candidate_experience = {
        skill.lower(): years
        for skill, years
        in candidate.get("experience", {}).items()
    }

    for required_skill, required_years in (
        required_skill_experience.items()
    ):

        required_skill_lower = (
            required_skill.lower()
        )

        # -------------------------------------------------
        # Skill must exist
        # -------------------------------------------------

        if required_skill_lower not in candidate_skills:

            return False

        # -------------------------------------------------
        # If JD specifies experience,
        # candidate must meet it.
        # -------------------------------------------------

        candidate_years = candidate_experience.get(
            required_skill_lower,
            0
        )

        if candidate_years < required_years:

            return False

    return True


def qualify_candidates(
    candidates,
    required_skills
):
    """
    Return only candidates who satisfy
    all required skills.

    This function is kept for compatibility
    with the existing RecruitOS pipeline.
    """

    return [
        candidate
        for candidate in candidates
        if qualify_candidate(
            candidate,
            required_skills
        )
    ]


def qualify_candidates_with_experience(
    candidates,
    required_skill_experience
):
    """
    Return only candidates who satisfy all required
    skills AND minimum experience requirements.
    """

    return [
        candidate
        for candidate in candidates
        if qualify_candidate_with_experience(
            candidate,
            required_skill_experience
        )
    ]