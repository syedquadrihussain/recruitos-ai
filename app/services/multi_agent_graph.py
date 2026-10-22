from langgraph.graph import StateGraph, END

from app.services.multi_agent_state import MultiAgentState
from app.services.supervisor_agent import supervisor_node
from app.services.recruitos_search import search_recruitos
from app.services.jd_qualification import get_required_skill_experience
from app.services.candidate_matcher import check_candidate
from app.services.candidate_ranker import rank_candidates


# =========================================================
# Supervisor Routing
# =========================================================

def route_from_supervisor(state: MultiAgentState) -> str:
    next_agent = state.get("next_agent", "END")

    routes = {
        "SEARCH": "search",
        "SCREENING": "screening",
        "MATCHING": "matching",
    }

    return routes.get(next_agent, "end")


# =========================================================
# Search Agent
# =========================================================

def search_agent_node(state: MultiAgentState) -> MultiAgentState:
    """Retrieve candidate profiles using RecruitOS search."""

    print("\nSEARCH AGENT")

    jd_text = state.get("jd_text", "")
    query = state.get("user_request", "").strip()

    if not query:
        query = jd_text.strip()

    # Count the attempt before skill extraction and retrieval.
    # Failures in either operation are handled consistently.
    state["search_attempts"] = state.get("search_attempts", 0) + 1

    try:
        required_skills = list(
            get_required_skill_experience(jd_text).keys()
        )

        candidates = search_recruitos(
            query=query,
            strategy="HYBRID_SEARCH",
            required_skills=required_skills,
            top_k=5,
        )

        state["last_search_error"] = ""

    except Exception as error:
        # Record the failure and allow the supervisor to decide
        # whether another bounded search attempt is appropriate.
        candidates = []
        state["last_search_error"] = (
            f"{type(error).__name__}: {error}"
        )

        print("Search failed:", state["last_search_error"])

    state["candidates"] = candidates
    state["last_agent"] = "SEARCH"

    print("Candidates retrieved:", len(candidates))

    candidates_with_evidence = sum(
        bool((candidate.get("resume_text") or "").strip())
        for candidate in candidates
    )

    print(
        "Candidates with resume evidence:",
        candidates_with_evidence,
    )

    return state


# =========================================================
# Screening Agent
# =========================================================

def screening_agent_node(state: MultiAgentState) -> MultiAgentState:
    """Screen candidates independently so one failure does not abort the batch."""

    print("\nSCREENING AGENT")

    screening_results = []
    screening_errors = []
    jd_text = state.get("jd_text", "")
    candidates = state.get("candidates", [])

    for index, candidate in enumerate(candidates):
        candidate_id = (
            candidate.get("candidate_id", f"unknown_candidate_{index}")
            if isinstance(candidate, dict)
            else f"invalid_candidate_{index}"
        )

        try:
            if not isinstance(candidate, dict):
                raise TypeError("Candidate record must be a dictionary")

            result = check_candidate(
                candidate,
                jd_text,
                resume_text=candidate.get("resume_text"),
            )

            if not isinstance(result, dict):
                raise TypeError("check_candidate must return a dictionary")

            # Keep downstream ranker inputs explicit and predictable.
            result = dict(result)
            result.setdefault("candidate_id", candidate_id)

            if "qualified" not in result or "final_score" not in result:
                raise ValueError(
                    "Screening result must contain qualified and final_score"
                )

            screening_results.append(result)

        except Exception as error:
            message = (
                f"{candidate_id}: {type(error).__name__}: {error}"
            )
            screening_errors.append(message)
            print("Candidate screening failed:", message)

    state["screened_candidates"] = screening_results
    state["screening_completed"] = True
    state["last_screening_error"] = "\n".join(screening_errors)
    state["last_agent"] = "SCREENING"

    if candidates and not screening_results:
        state["workflow_complete"] = True
        state["stop_reason"] = "SCREENING_FAILED"
    elif screening_errors:
        if not state.get("stop_reason"):
            state["stop_reason"] = "SCREENING_PARTIAL_FAILURE"
    elif state.get("stop_reason") == "SCREENING_PARTIAL_FAILURE":
        state["stop_reason"] = ""

    print("Candidates screened successfully:", len(screening_results))
    print("Candidate screening errors:", len(screening_errors))

    return state


# =========================================================
# Matching and Shortlisting Agent
# =========================================================

def matching_agent_node(state: MultiAgentState) -> MultiAgentState:
    """Rank screened candidates and stop safely if ranking fails."""

    print("\nMATCHING AGENT")

    try:
        ranked_candidates = rank_candidates(
            state.get("screened_candidates", [])
        )

        if not isinstance(ranked_candidates, list):
            raise TypeError("rank_candidates must return a list")

        for candidate in ranked_candidates:
            if not isinstance(candidate, dict):
                raise TypeError("Ranked candidate must be a dictionary")
            if "qualified" not in candidate or "final_score" not in candidate:
                raise ValueError(
                    "Ranked candidate must contain qualified and final_score"
                )

        qualified_candidates = [
            candidate
            for candidate in ranked_candidates
            if candidate.get("qualified") is True
        ]

        target_count = max(0, state.get("target_count", 2))

        state["matched_candidates"] = ranked_candidates
        state["shortlisted_candidates"] = qualified_candidates[:target_count]
        state["matching_completed"] = True
        state["last_matching_error"] = ""
        state["last_agent"] = "MATCHING"

        if state.get("stop_reason") == "MATCHING_FAILED":
            state["stop_reason"] = ""

        print("Candidates ranked:", len(ranked_candidates))
        print("Qualified candidates:", len(qualified_candidates))
        print("Shortlisted candidates:", len(state["shortlisted_candidates"]))

    except Exception as error:
        state["matched_candidates"] = []
        state["shortlisted_candidates"] = []
        state["matching_completed"] = False
        state["last_matching_error"] = (
            f"{type(error).__name__}: {error}"
        )
        state["workflow_complete"] = True
        state["stop_reason"] = "MATCHING_FAILED"
        state["last_agent"] = "MATCHING"

        print("Matching failed:", state["last_matching_error"])

    return state


# =========================================================
# Matching and Shortlisting Agent


# =========================================================

def build_multi_agent_graph():
    workflow = StateGraph(MultiAgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("search", search_agent_node)
    workflow.add_node("screening", screening_agent_node)
    workflow.add_node("matching", matching_agent_node)

    workflow.set_entry_point("supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_from_supervisor,
        {
            "search": "search",
            "screening": "screening",
            "matching": "matching",
            "end": END,
        },
    )

    workflow.add_edge("search", "supervisor")
    workflow.add_edge("screening", "supervisor")
    workflow.add_edge("matching", "supervisor")

    return workflow.compile()


# =========================================================
# Run Workflow
# =========================================================

if __name__ == "__main__":
    graph = build_multi_agent_graph()

    initial_state: MultiAgentState = {
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
        "shortlisted_candidates": [],
        "next_agent": "",
        "workflow_complete": False,
        "stop_reason": "",
        "search_attempts": 0,
        "max_search_attempts": 3,
        "last_search_error": "",
        "screening_completed": False,
        "matching_completed": False,
        "last_screening_error": "",
        "last_matching_error": "",
    }

    final_state = graph.invoke(initial_state)

    print("\n================================")
    print("FINAL MULTI-AGENT RESULTS")
    print("================================")

    print("Retrieved:", len(final_state["candidates"]))
    print("Screened:", len(final_state["screened_candidates"]))
    print("Ranked:", len(final_state["matched_candidates"]))

    print("\nQUALIFIED SHORTLIST")

    for position, candidate in enumerate(
        final_state["shortlisted_candidates"],
        start=1,
    ):
        print(f"\n{position}. {candidate['name']}")
        print("Qualified:", candidate["qualified"])
        print("Recommendation:", candidate["recommendation"])
        print("Final score:", candidate["final_score"])
        print("Reasons:", candidate["reasons"])

    print(
        "\nWorkflow complete:",
        final_state["workflow_complete"],
    )
    print("Stop reason:", final_state["stop_reason"])