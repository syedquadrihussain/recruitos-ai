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

def choose_next_agent(state: MultiAgentState) -> str:
    """Choose the next step using completion flags and bounded search retries."""

    if state.get("workflow_complete", False):
        return "END"

    target_count = state.get("target_count", 0)
    shortlisted = state.get("shortlisted_candidates", [])

    if target_count > 0 and len(shortlisted) >= target_count:
        return "END"

    candidates = state.get("candidates", [])

    if not candidates:
        attempts = state.get("search_attempts", 0)
        max_attempts = max(1, state.get("max_search_attempts", 3))
        return "END" if attempts >= max_attempts else "SEARCH"

    screened = state.get("screened_candidates", [])
    screening_completed = state.get(
        "screening_completed", bool(screened)
    )

    if not screening_completed:
        return "SCREENING"

    matched = state.get("matched_candidates", [])
    matching_completed = state.get(
        "matching_completed", bool(matched)
    )

    if not matching_completed:
        return "MATCHING"

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
        "Shortlisted candidates:",
        len(
            state.get(
                "shortlisted_candidates",
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
            if (
                not state.get("candidates", [])
                and state.get("search_attempts", 0)
                >= max(1, state.get("max_search_attempts", 3))
            ):
                state["stop_reason"] = "SEARCH_ATTEMPTS_EXHAUSTED"
            else:
                state["stop_reason"] = "SUPERVISOR_COMPLETED"

    return state