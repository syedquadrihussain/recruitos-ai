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