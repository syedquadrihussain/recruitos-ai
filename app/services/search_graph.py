from langgraph.graph import StateGraph, END

from app.services.search_state import SearchState

from app.services.search_planner import (
    choose_search_strategy
)

from app.services.llm_search_planner import (
    choose_strategy_with_llm
)

from app.services.search_observer import (
    observe_search_results
)

from app.services.recruitos_search import (
    search_recruitos
)

from app.services.loop_safety import (
    should_stop_search
)

from app.services.jd_qualification import (
    get_required_skill_experience,
    qualify_candidates_with_experience
)


# ---------------------------------------------------------
# Planner Node
# ---------------------------------------------------------

def planner_node(
    state: SearchState
) -> SearchState:

    try:

        strategy = choose_strategy_with_llm(
            state
        )

        print(
            f"\nLLM Planner selected: "
            f"{strategy.value}"
        )

    except Exception as error:

        print(
            "\nLLM Planner failed:"
        )

        print(error)

        print(
            "\nUsing deterministic "
            "planner fallback."
        )

        strategy = choose_search_strategy(
            state
        )

        print(
            f"Fallback Planner selected: "
            f"{strategy.value}"
        )

    state["current_strategy"] = (
        strategy.value
    )

    state["attempt"] += 1

    return state


# ---------------------------------------------------------
# Search Node
# ---------------------------------------------------------

def search_node(
    state: SearchState
) -> SearchState:

    strategy = state["current_strategy"]

    query = state["goal"]

    # -----------------------------------------------------
    # Extract required skills AND experience
    # from the actual Job Description
    # -----------------------------------------------------

    required_skill_experience = (
        get_required_skill_experience(
            state["jd_text"]
        )
    )

    required_skills = list(
        required_skill_experience.keys()
    )

    print(
        f"Required skill experience from JD: "
        f"{required_skill_experience}"
    )

    # -----------------------------------------------------
    # Search RecruitOS
    # -----------------------------------------------------

    search_results = search_recruitos(
        query=query,
        strategy=strategy,
        required_skills=required_skills,
        top_k=5
    )

    print(
        f"Search strategy: "
        f"{strategy}"
    )

    print(
        f"Candidates found: "
        f"{len(search_results)}"
    )

    # -----------------------------------------------------
    # Experience-aware JD qualification
    # -----------------------------------------------------

    qualified_results = (
        qualify_candidates_with_experience(
            search_results,
            required_skill_experience
        )
    )

    print(
        f"Qualified from current search: "
        f"{len(qualified_results)}"
    )

    # -----------------------------------------------------
    # Save current search information
    # -----------------------------------------------------

    state["current_query"] = query

    state["current_search_results"] = (
        search_results
    )

    state["current_qualified_results"] = (
        qualified_results
    )

    return state


# ---------------------------------------------------------
# Observation Node
# ---------------------------------------------------------

def observe_node(
    state: SearchState
) -> SearchState:

    return observe_search_results(
        state,
        state["current_search_results"],
        state["current_qualified_results"]
    )


# ---------------------------------------------------------
# Endpoint + Safety Check
# ---------------------------------------------------------

def endpoint_check(
    state: SearchState
) -> str:

    qualified_count = len(
        state["qualified_candidates"]
    )

    target_count = state["target_count"]

    print(
        f"Qualified candidates: "
        f"{qualified_count}/"
        f"{target_count}"
    )

    # -----------------------------------------------------
    # Business endpoint
    # -----------------------------------------------------

    if qualified_count >= target_count:

        print(
            "\nEndpoint reached."
            " Stopping loop."
        )

        return "stop"

    # -----------------------------------------------------
    # Safety endpoint
    # -----------------------------------------------------

    if should_stop_search(state):

        return "stop"

    print(
        "\nEndpoint not reached."
        " Continuing loop."
    )

    return "continue"


# ---------------------------------------------------------
# Build LangGraph
# ---------------------------------------------------------

def build_search_graph():

    workflow = StateGraph(
        SearchState
    )

    workflow.add_node(
        "planner",
        planner_node
    )

    workflow.add_node(
        "search",
        search_node
    )

    workflow.add_node(
        "observe",
        observe_node
    )

    workflow.set_entry_point(
        "planner"
    )

    workflow.add_edge(
        "planner",
        "search"
    )

    workflow.add_edge(
        "search",
        "observe"
    )

    workflow.add_conditional_edges(
        "observe",
        endpoint_check,
        {
            "continue": "planner",
            "stop": END
        }
    )

    return workflow.compile()


# ---------------------------------------------------------
# Run the workflow
# ---------------------------------------------------------

if __name__ == "__main__":

    search_graph = build_search_graph()

    # -----------------------------------------------------
    # Temporary sample JD
    # -----------------------------------------------------
    # Later this will come from the recruiter through
    # the FastAPI application.

    jd_text = """

    Job Title:
    Python RAG Developer

    Must Have:
    Python - 5 years
    RAG - 2 years
    FastAPI - 2 years

    Nice to Have:
    Docker
    AWS

    """

    initial_state = {

        "goal": (
            "Find candidates for "
            "Python RAG Developer"
        ),

        "jd_text": jd_text,

        "target_count": 3,

        "candidates": [],

        "qualified_candidates": [],

        "attempt": 0,

        "current_strategy": "",

        "current_query": "",

        "last_search_candidates": 0,

        "last_search_qualified": 0,

        "last_search_duplicates": 0,

        "current_search_results": [],

        "current_qualified_results": []
    }

    final_state = search_graph.invoke(
        initial_state
    )

    print(
        "\n=============================="
    )

    print(
        "FINAL RESULT"
    )

    print(
        "=============================="
    )

    print(
        "\nRequired skill experience:"
    )

    print(
        get_required_skill_experience(
            jd_text
        )
    )

    print(
        "\nQualified candidates:"
    )

    for candidate in final_state[
        "qualified_candidates"
    ]:

        print(
            f"- {candidate['name']}"
        )

    print(
        f"\nTotal attempts: "
        f"{final_state['attempt']}"
    )