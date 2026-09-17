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

from app.services.search_strategies import (
    SearchStrategy
)


# =========================================================
# JD Preparation Node
# =========================================================

def prepare_jd_node(
    state: SearchState
) -> SearchState:

    print(
        "\nPreparing Job Description..."
    )

    required_skill_experience = (
        get_required_skill_experience(
            state["jd_text"]
        )
    )

    state["required_skill_experience"] = (
        required_skill_experience
    )

    state["required_skills"] = list(
        required_skill_experience.keys()
    )

    print(
        "\nRequired skill experience:",
        required_skill_experience
    )

    print(
        "\nRequired skills:",
        state["required_skills"]
    )

    return state


# =========================================================
# Strategy Validation
# =========================================================

def validate_strategy(
    strategy: SearchStrategy,
    attempted_strategies: list
) -> SearchStrategy:

    # -----------------------------------------------------
    # If the LLM selected an unused strategy, accept it.
    # -----------------------------------------------------

    if strategy.value not in attempted_strategies:

        return strategy

    # -----------------------------------------------------
    # The LLM selected a strategy that was already used.
    # RecruitOS must not blindly repeat it.
    # -----------------------------------------------------

    print(
        f"\nLLM selected an already attempted strategy:"
        f" {strategy.value}"
    )

    print(
        "Validating strategy against application rules..."
    )

    # -----------------------------------------------------
    # Find the first strategy that has not been attempted.
    # The order comes from the SearchStrategy enum.
    # -----------------------------------------------------

    for available_strategy in SearchStrategy:

        if (
            available_strategy.value
            not in attempted_strategies
        ):

            print(
                f"Using unused strategy instead:"
                f" {available_strategy.value}"
            )

            return available_strategy

    # -----------------------------------------------------
    # Normally this will not be reached because the loop
    # safety limit is lower than the total number of
    # available strategies.
    # -----------------------------------------------------

    print(
        "\nAll search strategies have been attempted."
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

    if "attempted_strategies" not in state:

        state["attempted_strategies"] = []

    attempted_strategies = (
        state["attempted_strategies"]
    )

    # -----------------------------------------------------
    # First ask the LLM for the next strategy.
    # -----------------------------------------------------

    try:

        strategy = choose_strategy_with_llm(
            state
        )

        print(
            f"\nLLM Planner suggested:"
            f" {strategy.value}"
        )

    except Exception as error:

        print(
            "\nLLM Planner failed:"
        )

        print(error)

        print(
            "\nUsing deterministic planner fallback."
        )

        strategy = choose_search_strategy(
            state
        )

        print(
            f"Fallback Planner selected:"
            f" {strategy.value}"
        )

    # -----------------------------------------------------
    # Application-level validation.
    #
    # The LLM can suggest a strategy, but RecruitOS
    # controls whether that strategy is allowed.
    # -----------------------------------------------------

    strategy = validate_strategy(
        strategy,
        attempted_strategies
    )

    print(
        f"\nFinal strategy selected by RecruitOS:"
        f" {strategy.value}"
    )

    # -----------------------------------------------------
    # Store the validated strategy.
    # -----------------------------------------------------

    state["current_strategy"] = (
        strategy.value
    )

    # -----------------------------------------------------
    # Record the strategy as attempted.
    # -----------------------------------------------------

    if (
        strategy.value
        not in state["attempted_strategies"]
    ):

        state["attempted_strategies"].append(
            strategy.value
        )

    # -----------------------------------------------------
    # Increase search attempt count.
    # -----------------------------------------------------

    state["attempt"] += 1

    print(
        f"Search attempt number:"
        f" {state['attempt']}"
    )

    return state


# =========================================================
# Search Node
# =========================================================

def search_node(
    state: SearchState
) -> SearchState:

    print(
        f"\nSearch strategy:"
        f" {state['current_strategy']}"
    )

    candidates = search_recruitos(
        query=state["current_query"],
        strategy=state["current_strategy"],
        required_skills=state.get(
            "required_skills",
            []
        ),
        top_k=5
    )

    print(
        f"Candidates found:"
        f" {len(candidates)}"
    )

    state["current_search_results"] = (
        candidates
    )

    return state


# =========================================================
# Qualification Node
# =========================================================

def qualification_node(
    state: SearchState
) -> SearchState:

    required_skill_experience = (
        state.get(
            "required_skill_experience",
            {}
        )
    )

    print(
        "\nRequired skill experience:",
        required_skill_experience
    )

    qualified_candidates = (
        qualify_candidates_with_experience(
            state["current_search_results"],
            required_skill_experience
        )
    )

    print(
        f"Qualified from current search:"
        f" {len(qualified_candidates)}"
    )

    state["current_qualified_results"] = (
        qualified_candidates
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
        f"Qualified candidates:"
        f" {len(state['qualified_candidates'])}/"
        f"{state['target_count']}"
    )

    return state


# =========================================================
# Endpoint Check
# =========================================================

def endpoint_check(
    state: SearchState
) -> str:

    # -----------------------------------------------------
    # Business endpoint
    # -----------------------------------------------------

    if (
        len(state["qualified_candidates"])
        >= state["target_count"]
    ):

        print(
            "\nEndpoint reached."
            " Target candidate count achieved."
        )

        print(
            "Stopping loop."
        )

        return "stop"

    # -----------------------------------------------------
    # Safety endpoints
    # -----------------------------------------------------

    if should_stop_search(state):

        print(
            "\nSafety endpoint reached."
        )

        return "stop"

    # -----------------------------------------------------
    # Continue the Agent Loop
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
# Main Test
# =========================================================

if __name__ == "__main__":

    search_graph = build_search_graph()

    initial_state = {

        "goal": (
            "Find qualified Python "
            "FastAPI RAG developers"
        ),

        "jd_text": """
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

        "current_query": (
            "Python FastAPI RAG Developer"
        ),

        "last_search_candidates": 0,

        "last_search_qualified": 0,

        "last_search_duplicates": 0,

        "no_progress_count": 0,

        "current_search_results": [],

        "current_qualified_results": [],

        "required_skills": [],

        "required_skill_experience": {}
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
        final_state.get(
            "required_skill_experience",
            {}
        )
    )

    print(
        "\nQualified candidates:"
    )

    for candidate in (
        final_state["qualified_candidates"]
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