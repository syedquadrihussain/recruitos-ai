from fastapi import APIRouter
from pydantic import BaseModel

from app.services.agent_service import run_agent


router = APIRouter(
    prefix="/agent",
    tags=["Agent"]
)


class AgentRequest(BaseModel):
    message: str


@router.post("/chat")
def chat_with_agent(request: AgentRequest):

    result = run_agent(request.message)

    return {
        "response": result
    }

def search_candidates(skill):

    candidates = [
        {
            "name": "Ahmed",
            "skills": ["Python", "RAG", "FastAPI"]
        },
        {
            "name": "Sarah",
            "skills": ["Python", "Machine Learning"]
        },
        {
            "name": "John",
            "skills": ["Java", "Spring Boot"]
        }
    ]

    matching_candidates = []

    for candidate in candidates:

        if skill.lower() in [
            candidate_skill.lower()
            for candidate_skill in candidate["skills"]
        ]:
            matching_candidates.append(candidate)

    return matching_candidates


def score_candidate(name):

    scores = {
        "Ahmed": 5,
        "John": 2,
        "Sarah": 4
    }

    return f"{name} has a candidate score of {scores.get(name, 0)} out of 5."