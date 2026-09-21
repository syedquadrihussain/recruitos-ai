from langgraph.graph import StateGraph, END

from app.services.multi_agent_state import (
    MultiAgentState
)

from app.services.supervisor_agent import (
    supervisor_node
)


# =========================================================
# Routing Functions
# =========================================================

def route_from_supervisor(
    state: MultiAgentState
) -> str:
    """
    Route the workflow based on the Supervisor decision.
    """

    next_agent = state.get(
        "next_agent",
        "END"
    )

    if next_agent == "SEARCH":
        return "search"

    if next_agent == "SCREENING":
        return "screening"

    if next_agent == "MATCHING":
        return "matching"

    return "end"


# =========================================================
# Temporary Search Agent
# =========================================================

def search_agent_node(
    state: MultiAgentState
) -> MultiAgentState:
    """
    Temporary Search Agent.

    Simulates candidate discovery so that the
    Multi-Agent routing architecture can be tested.
    """

    print(
        "\nSEARCH AGENT"
    )

    print(
        "Search Agent discovering candidates..."
    )

    state["candidates"] = [
        {
            "name": "Ahmed",
            "skills": [
                "Python",
                "FastAPI",
                "RAG"
            ]
        },
        {
            "name": "Sara",
            "skills": [
                "Python",
                "FastAPI"
            ]
        }
    ]

    state["last_agent"] = "SEARCH"

    print(
        "Candidates discovered:",
        len(state["candidates"])
    )

    return state


# =========================================================
# Temporary Screening Agent
# =========================================================

def screening_agent_node(
    state: MultiAgentState
) -> MultiAgentState:
    """
    Temporary Screening Agent.

    Simulates mandatory requirement screening.
    """

    print(
        "\nSCREENING AGENT"
    )

    print(
        "Screening discovered candidates..."
    )

    screened_candidates = []

    for candidate in state.get(
        "candidates",
        []
    ):

        screened_candidates.append(
            {
                **candidate,
                "screened": True
            }
        )

    state["screened_candidates"] = (
        screened_candidates
    )

    state["last_agent"] = "SCREENING"

    print(
        "Candidates screened:",
        len(
            state["screened_candidates"]
        )
    )

    return state


# =========================================================
# Temporary Matching Agent
# =========================================================

def matching_agent_node(
    state: MultiAgentState
) -> MultiAgentState:
    """
    Temporary Matching Agent.

    Simulates detailed candidate-to-JD matching.
    """

    print(
        "\nMATCHING AGENT"
    )

    print(
        "Matching screened candidates..."
    )

    matched_candidates = []

    for candidate in state.get(
        "screened_candidates",
        []
    ):

        if candidate.get(
            "screened",
            False
        ):

            matched_candidates.append(
                {
                    **candidate,
                    "matched": True
                }
            )

    state["matched_candidates"] = (
        matched_candidates
    )

    state["last_agent"] = "MATCHING"

    print(
        "Candidates matched:",
        len(
            state["matched_candidates"]
        )
    )

    return state


# =========================================================
# Build Multi-Agent Graph
# =========================================================

def build_multi_agent_graph():

    workflow = StateGraph(
        MultiAgentState
    )

    # -----------------------------------------------------
    # Add Nodes
    # -----------------------------------------------------

    workflow.add_node(
        "supervisor",
        supervisor_node
    )

    workflow.add_node(
        "search",
        search_agent_node
    )

    workflow.add_node(
        "screening",
        screening_agent_node
    )

    workflow.add_node(
        "matching",
        matching_agent_node
    )

    # -----------------------------------------------------
    # Entry Point
    # -----------------------------------------------------

    workflow.set_entry_point(
        "supervisor"
    )

    # -----------------------------------------------------
    # Supervisor Routing
    # -----------------------------------------------------

    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "search": "search",
            "screening": "screening",
            "matching": "matching",
            "end": END
        }
    )

    # -----------------------------------------------------
    # Specialist Agents Return to Supervisor
    # -----------------------------------------------------

    workflow.add_edge(
        "search",
        "supervisor"
    )

    workflow.add_edge(
        "screening",
        "supervisor"
    )

    workflow.add_edge(
        "matching",
        "supervisor"
    )

    return workflow.compile()


# =========================================================
# Test Workflow
# =========================================================

if __name__ == "__main__":

    graph = build_multi_agent_graph()

    initial_state = {
        "user_request": (
            "Find qualified Python FastAPI RAG developers."
        ),

        "jd_text": """
        Python FastAPI RAG Developer

        Required skills:

        Python - 5 years
        FastAPI - 2 years
        RAG - 2 years
        """,

        "target_count": 2,

        "current_task": "",

        "last_agent": "",

        "candidates": [],

        "screened_candidates": [],

        "matched_candidates": [],

        "next_agent": "",

        "workflow_complete": False,

        "stop_reason": ""
    }

    final_state = graph.invoke(
        initial_state
    )

    print(
        "\n=============================="
    )

    print(
        "FINAL MULTI-AGENT STATE"
    )

    print(
        "=============================="
    )

    print(
        "Candidates:",
        len(
            final_state["candidates"]
        )
    )

    print(
        "Screened candidates:",
        len(
            final_state["screened_candidates"]
        )
    )

    print(
        "Matched candidates:",
        len(
            final_state["matched_candidates"]
        )
    )

    print(
        "Last agent:",
        final_state["last_agent"]
    )

    print(
        "Workflow complete:",
        final_state["workflow_complete"]
    )

    print(
        "Stop reason:",
        final_state["stop_reason"]
    )