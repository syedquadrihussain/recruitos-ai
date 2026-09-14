from langgraph.graph import StateGraph, END

from app.services.search_state import SearchState
from app.services.search_planner import choose_search_strategy
from app.services.search_observer import observe_search_results


# ---------------------------------------------------------
# Controlled test data
# ---------------------------------------------------------

MOCK_SEARCH_RESULTS = {

    "EXACT_SKILL": [
        {
            "name": "Ahmed",
            "skills": [
                "Python",
                "RAG",
                "FastAPI"
            ]
        },
        {
            "name": "Sara",
            "skills": [
                "Python",
                "RAG"
            ]
        }
    ],

    "RELATED_SKILL": [
        {
            "name": "Sara",
            "skills": [
                "Python",
                "RAG"
            ]
        },
        {
            "name": "John",
            "skills": [
                "Python",
                "FastAPI"
            ]
        }
    ],

    "ROLE": [
        {
            "name": "John",
            "skills": [
                "Python",
                "FastAPI"
            ]
        },
        {
            "name": "Priya",
            "skills": [
                "Python",
                "RAG",
                "FastAPI"
            ]
        }
    ],

    "DOMAIN": [
        {
            "name": "Priya",
            "skills": [
                "Python",
                "RAG",
                "FastAPI"
            ]
        }
    ],

    "SEMANTIC_SEARCH": [
        {
            "name": "David",
            "skills": [
                "Python",
                "Generative AI"
            ]
        }
    ],

    "HYBRID_SEARCH": [
        {
            "name": "Michael",
            "skills": [
                "Python",
                "RAG"
            ]
        }
    ],

    "SOURCE_SEARCH": [
        {
            "name": "Aisha",
            "skills": [
                "Python",
                "RAG",
                "FastAPI"
            ]
        }
    ]
}


# ---------------------------------------------------------
# Planner Node
# ---------------------------------------------------------

def planner_node(
    state: SearchState
) -> SearchState:

    strategy = choose_search_strategy(
        state
    )

    state["current_strategy"] = (
        strategy.value
    )

    state["attempt"] += 1

    print(
        f"\nPlanner selected: "
        f"{strategy.value}"
    )

    return state


# ---------------------------------------------------------
# Search Node
# ---------------------------------------------------------

def search_node(
    state: SearchState
) -> SearchState:

    strategy = state["current_strategy"]

    search_results = MOCK_SEARCH_RESULTS.get(
        strategy,
        []
    )

    print(
        f"Search strategy: "
        f"{strategy}"
    )

    print(
        f"Candidates found: "
        f"{len(search_results)}"
    )

    qualified_results = [
        candidate
        for candidate in search_results
        if "RAG" in candidate["skills"]
    ]

    state["current_query"] = (
        f"{strategy} search for "
        f"{state['goal']}"
    )

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
# Endpoint Check
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

    if qualified_count >= target_count:

        print(
            "\nEndpoint reached."
            " Stopping loop."
        )

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

    initial_state = {

        "goal": (
            "Find Python RAG candidates"
        ),

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