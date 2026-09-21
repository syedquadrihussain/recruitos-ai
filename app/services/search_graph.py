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
    get_stop_reason
)

from app.services.jd_parser import (
    get_required_skill_experience
)

from app.services.jd_qualification import (
    qualify_candidates_with_experience
)

from app.services.search_strategies import (
    SearchStrategy
)


# =========================================================
# Prepare Job Description
# =========================================================

def prepare_jd_node(
    state: SearchState
) -> SearchState:

    print("\nPreparing Job Description...")

    required_skill_experience = (
        get_required_skill_experience(
            state["jd_text"]
        )
    )

    required_skills = list(
        required_skill_experience.keys()
    )

    state["required_skill_experience"] = (
        required_skill_experience
    )

    state["required_skills"] = (
        required_skills
    )

    print(
        "\nRequired skill experience:",
        required_skill_experience
    )

    print(
        "\nRequired skills:",
        required_skills
    )

    return state


# =========================================================
# Validate Search Strategy
# =========================================================

def validate_strategy(
    strategy: SearchStrategy,
    attempted_strategies: list
) -> SearchStrategy:

    if strategy.value not in attempted_strategies:
        return strategy

    print(
        f"\nLLM selected an already attempted "
        f"strategy: {strategy.value}"
    )

    print(
        "Validating strategy against "
        "application rules..."
    )

    for available_strategy in SearchStrategy:

        if (
            available_strategy.value
            not in attempted_strategies
        ):

            print(
                "Using unused strategy instead:",
                available_strategy.value
            )

            return available_strategy

    print(
        "\nAll search strategies "
        "have been attempted."
    )

    print(
        "Keeping the LLM-selected strategy."
    )

    return strategy


# =========================================================
# Planner Node
# =========================================================

def planner_node(
    state: SearchState
) -> SearchState:

    attempted_strategies = (
        state.get(
            "attempted_strategies",
            []
        )
    )

    try:

        strategy = (
            choose_strategy_with_llm(
                state
            )
        )

        print(
            f"\nLLM Planner suggested: "
            f"{strategy.value}"
        )

    except Exception as error:

        print(
            "\nLLM Planner failed."
        )

        print(
            f"Reason: {error}"
        )

        print(
            "Using deterministic planner fallback."
        )

        strategy = (
            choose_search_strategy(
                state
            )
        )

        print(
            f"Fallback strategy: "
            f"{strategy.value}"
        )

    strategy = validate_strategy(
        strategy,
        attempted_strategies
    )

    state["current_strategy"] = (
        strategy.value
    )

    if (
        strategy.value
        not in state["attempted_strategies"]
    ):

        state["attempted_strategies"].append(
            strategy.value
        )

    state["attempt"] += 1

    print(
        f"\nFinal strategy selected by RecruitOS: "
        f"{strategy.value}"
    )

    print(
        f"Search attempt number: "
        f"{state['attempt']}"
    )

    return state


# =========================================================
# Search Node
# =========================================================

def search_node(
    state: SearchState
) -> SearchState:

    print(
        f"\nSearch strategy: "
        f"{state['current_strategy']}"
    )

    search_results = search_recruitos(
        query=state["current_query"],
        strategy=state["current_strategy"],
        required_skills=state["required_skills"]
    )

    state["current_search_results"] = (
        search_results
    )

    print(
        f"Candidates found: "
        f"{len(search_results)}"
    )

    return state


# =========================================================
# Qualification Node
# =========================================================

def qualification_node(
    state: SearchState
) -> SearchState:

    qualified_results = (
        qualify_candidates_with_experience(
            state["current_search_results"],
            state["required_skill_experience"]
        )
    )

    state["current_qualified_results"] = (
        qualified_results
    )

    print(
        "\nRequired skill experience:",
        state["required_skill_experience"]
    )

    print(
        f"Qualified from current search: "
        f"{len(qualified_results)}"
    )

    return state


# =========================================================
# Observer Node
# =========================================================

def observer_node(
    state: SearchState
) -> SearchState:

    state = observe_search_results(
        state,
        state["current_search_results"],
        state["current_qualified_results"]
    )

    print(
        f"\nQualified candidates: "
        f"{len(state['qualified_candidates'])}"
        f"/{state['target_count']}"
    )

    # -----------------------------------------------------
    # Target reached
    # -----------------------------------------------------

    if (
        len(state["qualified_candidates"])
        >= state["target_count"]
    ):

        state["stop_reason"] = (
            "TARGET_REACHED"
        )

        print(
            "\nTarget candidate count achieved."
        )

        return state

    # -----------------------------------------------------
    # Check loop safety
    # -----------------------------------------------------

    stop_reason = get_stop_reason(
        state
    )

    if stop_reason:

        state["stop_reason"] = (
            stop_reason
        )

    return state


# =========================================================
# Endpoint Check
# =========================================================

def endpoint_check(
    state: SearchState
) -> str:

    # -----------------------------------------------------
    # Stop condition already determined
    # by the Observer node.
    # -----------------------------------------------------

    if state.get("stop_reason"):

        stop_reason = state[
            "stop_reason"
        ]

        if stop_reason == "TARGET_REACHED":

            print(
                "\nEndpoint reached. "
                "Target candidate count achieved."
            )

            print(
                "Stopping loop."
            )

        elif stop_reason == "MAX_ATTEMPTS":

            print(
                "\nMaximum search attempts reached."
            )

            print(
                "Stopping loop safely."
            )

        elif stop_reason == "NO_PROGRESS":

            print(
                "\nRepeated no-progress detected."
            )

            print(
                "The search is not discovering "
                "new qualified candidates."
            )

            print(
                "Stopping loop safely."
            )

        elif stop_reason == "DUPLICATE_RESULTS":

            print(
                "\nNo search progress detected."
            )

            print(
                "All returned candidates "
                "were already discovered."
            )

            print(
                "Stopping loop safely."
            )

        print(
            "\nSafety endpoint reached."
        )

        return "stop"

    # -----------------------------------------------------
    # Continue search
    # -----------------------------------------------------

    print(
        "\nTarget not reached."
    )

    print(
        "Sending state back to planner..."
    )

    return "continue"


# =========================================================
# Build Search Graph
# =========================================================

def build_search_graph():

    workflow = StateGraph(
        SearchState
    )

    workflow.add_node(
        "prepare_jd",
        prepare_jd_node
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
        "qualification",
        qualification_node
    )

    workflow.add_node(
        "observer",
        observer_node
    )

    workflow.set_entry_point(
        "prepare_jd"
    )

    workflow.add_edge(
        "prepare_jd",
        "planner"
    )

    workflow.add_edge(
        "planner",
        "search"
    )

    workflow.add_edge(
        "search",
        "qualification"
    )

    workflow.add_edge(
        "qualification",
        "observer"
    )

    workflow.add_conditional_edges(
        "observer",
        endpoint_check,
        {
            "continue": "planner",
            "stop": END
        }
    )

    return workflow.compile()


# =========================================================
# Run RecruitOS Search Graph
# =========================================================

if __name__ == "__main__":

    search_graph = build_search_graph()

    initial_state = {

        "goal":
            "Find qualified Python FastAPI RAG developers",

        "jd_text":
            """
            We are looking for a Python FastAPI
            RAG Developer.

            Required skills:

            Python - 5 years
            FastAPI - 2 years
            RAG - 2 years
            """,

        "target_count": 5,

        "candidates": [],

        "qualified_candidates": [],

        "attempt": 0,

        "current_strategy": "",

        "attempted_strategies": [],

        "current_query":
            "Python FastAPI RAG Developer",

        "last_search_candidates": 0,

        "last_search_qualified": 0,

        "last_search_duplicates": 0,

        "no_progress_count": 0,

        "current_search_results": [],

        "current_qualified_results": [],

        "required_skills": [],

        "required_skill_experience": {},

        "total_searches": 0,

        "total_duplicates": 0,

        "total_qualified": 0,

        "stop_reason": ""
    }

    final_state = (
        search_graph.invoke(
            initial_state
        )
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
        final_state.get(
            "required_skill_experience",
            {}
        )
    )

    print(
        "\nQualified candidates:"
    )

    for candidate in (
        final_state[
            "qualified_candidates"
        ]
    ):

        print(
            f"- {candidate['name']}"
        )

    print(
        "\nTotal attempts:",
        final_state["attempt"]
    )

    print(
        "\nStrategies attempted:"
    )

    print(
        final_state.get(
            "attempted_strategies",
            []
        )
    )

    print(
        "\nLoop metrics:"
    )

    print(
        "Total searches:",
        final_state.get(
            "total_searches",
            0
        )
    )

    print(
        "Total duplicates:",
        final_state.get(
            "total_duplicates",
            0
        )
    )

    print(
        "Total qualified:",
        final_state.get(
            "total_qualified",
            0
        )
    )

    print(
        "Stop reason:",
        final_state.get(
            "stop_reason",
            ""
        )
    )
