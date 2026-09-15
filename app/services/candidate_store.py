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
    },

    "candidate_004": {
        "name": "David",
        "overall_experience": 8,
        "skills": [
            "Python",
            "FastAPI",
            "RAG",
            "LangChain",
            "Docker"
        ],
        "experience": {
            "Python": 8,
            "FastAPI": 5,
            "RAG": 4,
            "LangChain": 3,
            "Docker": 4
        }
    },

    "candidate_005": {
        "name": "Priya",
        "overall_experience": 7,
        "skills": [
            "Python",
            "FastAPI",
            "RAG",
            "AWS"
        ],
        "experience": {
            "Python": 7,
            "FastAPI": 4,
            "RAG": 3,
            "AWS": 4
        }
    },

    "candidate_006": {
        "name": "Michael",
        "overall_experience": 6,
        "skills": [
            "Python",
            "Machine Learning",
            "SQL",
            "AWS"
        ],
        "experience": {
            "Python": 6,
            "Machine Learning": 4,
            "SQL": 5,
            "AWS": 3
        }
    },

    "candidate_007": {
        "name": "Fatima",
        "overall_experience": 5,
        "skills": [
            "Python",
            "RAG",
            "LangChain",
            "SQL"
        ],
        "experience": {
            "Python": 5,
            "RAG": 2,
            "LangChain": 2,
            "SQL": 3
        }
    },

    "candidate_008": {
        "name": "Robert",
        "overall_experience": 9,
        "skills": [
            "Java",
            "AWS",
            "Docker",
            "Kubernetes"
        ],
        "experience": {
            "Java": 9,
            "AWS": 6,
            "Docker": 5,
            "Kubernetes": 4
        }
    }
}


def get_candidate(candidate_id):
    return candidate_profiles.get(candidate_id)


def generate_candidate_id():
    """
    Generates the next candidate_XXX id based on how many
    candidates already exist in the store.
    """

    next_number = len(candidate_profiles) + 1

    return f"candidate_{next_number:03d}"


def add_candidate(candidate_id, candidate_data):
    """
    Saves a newly extracted candidate (e.g. from an uploaded
    resume) into the store so search/retrieval can find them.

    candidate_data is expected to have the same shape produced
    by extract_candidate(): name, overall_experience, skills,
    experience, etc.
    """

    candidate_profiles[candidate_id] = candidate_data

    return candidate_id