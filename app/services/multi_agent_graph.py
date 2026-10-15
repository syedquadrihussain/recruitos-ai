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

    required_skills = list(
        get_required_skill_experience(jd_text).keys()
    )

    candidates = search_recruitos(
        query=query,
        strategy="HYBRID_SEARCH",
        required_skills=required_skills,
        top_k=5,
    )

    state["candidates"] = candidates
    state["last_agent"] = "SEARCH"

    print("Candidates retrieved:", len(candidates))

    candidates_with_evidence = sum(
        bool(candidate.get("resume_text", "").strip())
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
    """Evaluate candidates against the job description."""

    print("\nSCREENING AGENT")

    screening_results = []
    jd_text = state.get("jd_text", "")

    for candidate in state.get("candidates", []):

        # Use actual resume text when it is available.
        resume_text = candidate.get("resume_text")

        result = check_candidate(
            candidate,
            jd_text,
            resume_text=resume_text,
        )

        result["candidate_id"] = candidate["candidate_id"]

        screening_results.append(result)

    state["screened_candidates"] = screening_results
    state["last_agent"] = "SCREENING"

    print("Candidates screened:", len(screening_results))

    candidates_with_evidence = sum(
        bool(candidate.get("semantic_matches"))
        for candidate in screening_results
    )

    print(
        "Candidates with semantic matches:",
        candidates_with_evidence,
    )

    return state


# =========================================================
# Matching and Shortlisting Agent
# =========================================================

def matching_agent_node(state: MultiAgentState) -> MultiAgentState:
    """Rank candidates and create a qualified shortlist."""

    print("\nMATCHING AGENT")

    # Rank all screened candidates.
    ranked_candidates = rank_candidates(
        state.get("screened_candidates", [])
    )

    state["matched_candidates"] = ranked_candidates

    # Keep only candidates who passed mandatory requirements.
    qualified_candidates = [
        candidate
        for candidate in ranked_candidates
        if candidate.get("qualified") is True
    ]

    # Select up to the requested number of qualified candidates.
    target_count = state.get("target_count", 2)

    state["shortlisted_candidates"] = (
        qualified_candidates[:target_count]
    )

    state["last_agent"] = "MATCHING"

    print("Candidates ranked:", len(ranked_candidates))
    print("Qualified candidates:", len(qualified_candidates))
    print(
        "Shortlisted candidates:",
        len(state["shortlisted_candidates"]),
    )

    return state


# =========================================================
# Build Multi-Agent Graph
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