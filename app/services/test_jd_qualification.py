from app.services.jd_qualification import (
    get_required_skills,
    get_required_skill_experience,
    qualify_candidate,
    qualify_candidates,
    qualify_candidate_with_experience,
    qualify_candidates_with_experience
)


# ---------------------------------------------------------
# JD skill extraction
# ---------------------------------------------------------

def test_get_required_skills():

    jd = """
    Must Have:
    Python - 5 years
    RAG - 3 years
    FastAPI - 2 years

    Nice to Have:
    Docker
    AWS
    """

    required_skills = get_required_skills(
        jd
    )

    assert "Python" in required_skills
    assert "RAG" in required_skills
    assert "FastAPI" in required_skills


# ---------------------------------------------------------
# JD experience extraction
# ---------------------------------------------------------

def test_get_required_skill_experience():

    jd = """
    Must Have:
    Python - 5 years
    RAG - 3 years
    FastAPI - 2 years

    Nice to Have:
    Docker
    AWS
    """

    required_experience = (
        get_required_skill_experience(
            jd
        )
    )

    assert (
        required_experience["Python"]
        == 5
    )

    assert (
        required_experience["RAG"]
        == 3
    )

    assert (
        required_experience["FastAPI"]
        == 2
    )


# ---------------------------------------------------------
# Basic skill qualification
# ---------------------------------------------------------

def test_candidate_qualified_when_all_skills_match():

    candidate = {

        "name": "Ahmed",

        "skills": [
            "Python",
            "RAG",
            "FastAPI"
        ]
    }

    required_skills = [
        "Python",
        "RAG",
        "FastAPI"
    ]

    assert qualify_candidate(
        candidate,
        required_skills
    ) is True


def test_candidate_not_qualified_when_skill_missing():

    candidate = {

        "name": "Sara",

        "skills": [
            "Python",
            "FastAPI"
        ]
    }

    required_skills = [
        "Python",
        "RAG",
        "FastAPI"
    ]

    assert qualify_candidate(
        candidate,
        required_skills
    ) is False


def test_qualify_candidates_returns_only_matches():

    candidates = [

        {
            "name": "Ahmed",

            "skills": [
                "Python",
                "RAG",
                "FastAPI"
            ]
        },

        {
            "name": "Sara",

            "skills": [
                "Python"
            ]
        }
    ]

    required_skills = [
        "Python",
        "RAG",
        "FastAPI"
    ]

    qualified = qualify_candidates(
        candidates,
        required_skills
    )

    assert len(qualified) == 1
    assert qualified[0]["name"] == "Ahmed"


# ---------------------------------------------------------
# Experience-aware qualification
# ---------------------------------------------------------

def test_candidate_qualified_when_experience_matches():

    candidate = {

        "name": "Ahmed",

        "skills": [
            "Python",
            "RAG",
            "FastAPI"
        ],

        "experience": {
            "Python": 6,
            "RAG": 3,
            "FastAPI": 3
        }
    }

    required_experience = {

        "Python": 5,
        "RAG": 2,
        "FastAPI": 2
    }

    assert qualify_candidate_with_experience(
        candidate,
        required_experience
    ) is True


def test_candidate_not_qualified_when_experience_is_low():

    candidate = {

        "name": "Sara",

        "skills": [
            "Python",
            "RAG",
            "FastAPI"
        ],

        "experience": {
            "Python": 3,
            "RAG": 2,
            "FastAPI": 2
        }
    }

    required_experience = {

        "Python": 5,
        "RAG": 2,
        "FastAPI": 2
    }

    assert qualify_candidate_with_experience(
        candidate,
        required_experience
    ) is False


def test_candidate_not_qualified_when_required_skill_missing():

    candidate = {

        "name": "John",

        "skills": [
            "Python",
            "FastAPI"
        ],

        "experience": {
            "Python": 7,
            "FastAPI": 4
        }
    }

    required_experience = {

        "Python": 5,
        "RAG": 2,
        "FastAPI": 2
    }

    assert qualify_candidate_with_experience(
        candidate,
        required_experience
    ) is False


def test_candidate_with_exact_experience_is_qualified():

    candidate = {

        "name": "David",

        "skills": [
            "Python",
            "RAG",
            "FastAPI"
        ],

        "experience": {
            "Python": 5,
            "RAG": 2,
            "FastAPI": 2
        }
    }

    required_experience = {

        "Python": 5,
        "RAG": 2,
        "FastAPI": 2
    }

    assert qualify_candidate_with_experience(
        candidate,
        required_experience
    ) is True


def test_qualify_candidates_with_experience():

    candidates = [

        {
            "name": "Ahmed",

            "skills": [
                "Python",
                "RAG",
                "FastAPI"
            ],

            "experience": {
                "Python": 6,
                "RAG": 3,
                "FastAPI": 3
            }
        },

        {
            "name": "Sara",

            "skills": [
                "Python",
                "RAG",
                "FastAPI"
            ],

            "experience": {
                "Python": 3,
                "RAG": 2,
                "FastAPI": 2
            }
        },

        {
            "name": "John",

            "skills": [
                "Python",
                "FastAPI"
            ],

            "experience": {
                "Python": 7,
                "FastAPI": 4
            }
        }
    ]

    required_experience = {

        "Python": 5,
        "RAG": 2,
        "FastAPI": 2
    }

    qualified = (
        qualify_candidates_with_experience(
            candidates,
            required_experience
        )
    )

    assert len(qualified) == 1

    assert (
        qualified[0]["name"]
        == "Ahmed"
    )