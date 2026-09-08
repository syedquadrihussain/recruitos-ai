# --------------------------------
# Candidate Profiles
# --------------------------------

candidate_profiles = {

    "candidate_001": {
        "name": "Ahmed",
        "overall_experience": 6,
        "skills": [
            "Python",
            "FastAPI",
            "RAG",
            "Docker"
        ],
        "experience": {
            "Python": 6,
            "FastAPI": 3,
            "RAG": 2,
            "Docker": 1
        }
    },

    "candidate_002": {
        "name": "John",
        "overall_experience": 7,
        "skills": [
            "Java",
            "Spring Boot",
            "AWS",
            "Docker"
        ],
        "experience": {
            "Java": 7,
            "AWS": 3,
            "Docker": 2
        }
    },

    "candidate_003": {
        "name": "Sara",
        "overall_experience": 4,
        "skills": [
            "Python",
            "Django",
            "SQL",
            "AWS"
        ],
        "experience": {
            "Python": 4,
            "SQL": 5,
            "AWS": 2
        }
    }
}


def get_candidate(candidate_id):

    return candidate_profiles.get(candidate_id)