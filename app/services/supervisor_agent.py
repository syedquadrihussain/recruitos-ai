from app.services.multi_agent_state import (
    MultiAgentState
)


# =========================================================
# Supervisor Instructions
# =========================================================

SUPERVISOR_PROMPT = """
You are the Supervisor Agent for RecruitOS AI.

Your responsibility is to coordinate specialized
recruitment agents.

Available agents:

SEARCH
- Finds relevant candidates.

SCREENING
- Checks mandatory requirements and experience.

MATCHING
- Evaluates candidate-to-job-description relevance
  and ranking.

END
- Finishes the workflow when the recruitment task
  has enough information.

Rules:

1. Do not perform candidate search yourself.

2. Do not perform candidate qualification yourself.

3. Do not perform candidate matching yourself.

4. Decide which specialist should act next.

5. SEARCH should be used when candidates still need
   to be discovered.

6. SCREENING should be used after candidates have
   been discovered and need requirement validation.

7. MATCHING should be used after screening when
   candidates need detailed JD-to-resume evaluation.

8. END should be selected when the workflow is complete.

9. The recruiter remains the final decision maker.

Return only one of:

SEARCH
SCREENING
MATCHING
END
"""


# =========================================================
# Supervisor Decision
# =========================================================

def choose_next_agent(
    state: MultiAgentState
) -> str:
    """
    Decide which specialist agent should execute next.

    This first version uses deterministic workflow rules.
    The LLM-based Supervisor will be introduced after
    the routing architecture is tested.
    """

    # -----------------------------------------------------
    # Workflow already complete
    # -----------------------------------------------------

    if state.get("workflow_complete", False):

        return "END"

    # -----------------------------------------------------
    # Target already reached
    # -----------------------------------------------------

    target_count = state.get(
        "target_count",
        0
    )

    matched_candidates = state.get(
        "matched_candidates",
        []
    )

    if (
        target_count > 0
        and len(matched_candidates)
        >= target_count
    ):

        return "END"

    # -----------------------------------------------------
    # No candidates discovered yet
    # -----------------------------------------------------

    candidates = state.get(
        "candidates",
        []
    )

    if not candidates:

        return "SEARCH"

    # -----------------------------------------------------
    # Candidates exist but have not been screened
    # -----------------------------------------------------

    screened_candidates = state.get(
        "screened_candidates",
        []
    )

    if not screened_candidates:

        return "SCREENING"

    # -----------------------------------------------------
    # Candidates have been screened but not matched
    # -----------------------------------------------------

    if not matched_candidates:

        return "MATCHING"

    # -----------------------------------------------------
    # Default
    # -----------------------------------------------------

    return "END"


# =========================================================
# Supervisor Node
# =========================================================

def supervisor_node(
    state: MultiAgentState
) -> MultiAgentState:
    """
    Supervisor node for the Multi-Agent workflow.

    The Supervisor examines the shared state and
    determines which specialist should act next.
    """

    next_agent = choose_next_agent(
        state
    )

    state["next_agent"] = next_agent
    state["current_task"] = next_agent

    print(
        "\n=============================="
    )

    print(
        "SUPERVISOR AGENT"
    )

    print(
        "=============================="
    )

    print(
        "Candidates:",
        len(
            state.get(
                "candidates",
                []
            )
        )
    )

    print(
        "Screened candidates:",
        len(
            state.get(
                "screened_candidates",
                []
            )
        )
    )

    print(
        "Matched candidates:",
        len(
            state.get(
                "matched_candidates",
                []
            )
        )
    )

    print(
        "Supervisor decision:",
        next_agent
    )

    if next_agent == "END":

        state["workflow_complete"] = True

        if not state.get("stop_reason"):

            state["stop_reason"] = (
                "SUPERVISOR_COMPLETED"
            )

    return state