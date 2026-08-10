from fastapi import APIRouter

from app.agents.orchestrator import AgentOrchestrator
from app.schemas.orchestrator import (
    AgentExecutionRequest,
    AgentExecutionResponse,
)

router = APIRouter()

orchestrator = AgentOrchestrator()


@router.get("/order")
def get_execution_order():
    return {
        "execution_order": orchestrator.get_execution_order()
    }


@router.post(
    "/next",
    response_model=AgentExecutionResponse
)
def get_next_agent(
    request: AgentExecutionRequest
):
    next_agent = orchestrator.get_next_agent(
        request.completed_agents
    )

    return {
        "next_agent": next_agent
    }