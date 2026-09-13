import sys
import json
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import (
    StateGraph,
    START,
    END
)


# ============================================================
# 1. PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


# ============================================================
# 2. LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(
    PROJECT_ROOT / "agent_learning" / ".env"
)


# ============================================================
# 3. IMPORT REAL RECRUITOS TOOLS
# ============================================================

from app.services.candidate_tools import (
    search_candidates as recruitos_search_candidates,
    score_candidate as recruitos_score_candidate
)


# ============================================================
# 4. LANGGRAPH STATE
# ============================================================

class RecruitOSState(TypedDict, total=False):

    # --------------------------------------------------------
    # USER GOAL
    # --------------------------------------------------------

    user_request: str

    goal: str

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    skill: str

    attempted_queries: list

    search_history: list

    # --------------------------------------------------------
    # ENDPOINT
    # --------------------------------------------------------

    target_candidate_count: int

    minimum_score: float

    # --------------------------------------------------------
    # CANDIDATES
    # --------------------------------------------------------

    candidates: list

    qualified_candidates: list

    selected_candidate: str

    # --------------------------------------------------------
    # JOB DESCRIPTION / SCORING
    # --------------------------------------------------------

    job_description: str

    score_result: dict

    # --------------------------------------------------------
    # LOOP CONTROL
    # --------------------------------------------------------

    status: str

    stop_reason: str

    # --------------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------------

    final_answer: str


# ============================================================
# 5. CREATE LLM
# ============================================================

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)


# ============================================================
# 6. NODE — SEARCH CANDIDATES
# ============================================================

def search_candidates_node(
    state: RecruitOSState
):

    print("\n--- SEARCH CANDIDATES NODE ---")

    skill = state["skill"]

    attempted_queries = state.get(
        "attempted_queries",
        []
    )

    search_history = state.get(
        "search_history",
        []
    )

    # --------------------------------------------------------
    # PREVENT DUPLICATE SEARCHES
    # --------------------------------------------------------

    if skill in attempted_queries:

        print(
            f"Search already attempted for: {skill}"
        )

        print(
            "No new search will be performed."
        )

        return {
            "candidates": [],
            "status": "NO_PROGRESS"
        }

    # --------------------------------------------------------
    # RECORD QUERY
    # --------------------------------------------------------

    attempted_queries = (
        attempted_queries + [skill]
    )

    print(
        f"Searching for: {skill}"
    )

    # --------------------------------------------------------
    # CALL REAL RECRUITOS SEARCH TOOL
    # --------------------------------------------------------

    candidates = recruitos_search_candidates(
        skill
    )

    print(
        f"Candidates found: {len(candidates)}"
    )

    # --------------------------------------------------------
    # RECORD SEARCH HISTORY
    # --------------------------------------------------------

    search_history = search_history + [
        {
            "query": skill,
            "candidates_found": len(candidates)
        }
    ]

    return {
        "candidates": candidates,
        "attempted_queries": attempted_queries,
        "search_history": search_history,
        "status": "SEARCH_COMPLETED"
    }


# ============================================================
# 7. NODE — EVALUATE CANDIDATES
# ============================================================

def evaluate_candidates_node(
    state: RecruitOSState
):

    print("\n--- EVALUATE CANDIDATES NODE ---")

    candidates = state.get(
        "candidates",
        []
    )

    minimum_score = state.get(
        "minimum_score",
        75
    )

    job_description = state.get(
        "job_description",
        ""
    )

    qualified_candidates = state.get(
        "qualified_candidates",
        []
    )

    # --------------------------------------------------------
    # NO CANDIDATES
    # --------------------------------------------------------

    if not candidates:

        print(
            "No candidates returned by search."
        )

        return {
            "qualified_candidates":
                qualified_candidates
        }

    # --------------------------------------------------------
    # SCORE EACH CANDIDATE
    # --------------------------------------------------------

    for candidate in candidates:

        candidate_name = candidate["name"]

        # ----------------------------------------------------
        # PREVENT DUPLICATE CANDIDATES
        # ----------------------------------------------------

        already_added = any(
            existing["name"] == candidate_name
            for existing in qualified_candidates
        )

        if already_added:

            print(
                f"Already evaluated: {candidate_name}"
            )

            continue

        print(
            f"Evaluating: {candidate_name}"
        )

        result = recruitos_score_candidate(
            candidate_name,
            job_description
        )

        # ----------------------------------------------------
        # SCORE RESULT
        # ----------------------------------------------------

        if result.get("error"):

            print(
                f"Scoring error for {candidate_name}"
            )

            continue

        final_score = result.get(
            "final_score",
            0
        )

        qualified = result.get(
            "qualified",
            False
        )

        print(
            f"Score: {final_score}"
        )

        print(
            f"Qualified by scoring engine: {qualified}"
        )

        # ----------------------------------------------------
        # ENDPOINT QUALIFICATION
        # ----------------------------------------------------

        if (
            qualified
            and final_score >= minimum_score
        ):

            print(
                f"QUALIFIED: {candidate_name}"
            )

            qualified_candidates.append(
                {
                    "name": candidate_name,
                    "score": final_score,
                    "result": result
                }
            )

        else:

            print(
                f"NOT QUALIFIED: {candidate_name}"
            )

    return {
        "qualified_candidates":
            qualified_candidates
    }


# ============================================================
# 8. NODE — CHECK ENDPOINT
# ============================================================

def check_endpoint_node(
    state: RecruitOSState
):

    print("\n--- CHECK ENDPOINT NODE ---")

    qualified_candidates = state.get(
        "qualified_candidates",
        []
    )

    target_candidate_count = state.get(
        "target_candidate_count",
        1
    )

    current_count = len(
        qualified_candidates
    )

    print(
        f"Qualified candidates: "
        f"{current_count}"
    )

    print(
        f"Target candidates: "
        f"{target_candidate_count}"
    )

    # --------------------------------------------------------
    # BUSINESS ENDPOINT REACHED
    # --------------------------------------------------------

    if current_count >= target_candidate_count:

        print(
            "\n--- ENDPOINT REACHED ---"
        )

        print(
            "RecruitOS has reached the "
            "requested candidate target."
        )

        return {
            "status": "GOAL_REACHED",
            "stop_reason":
                "Target number of qualified "
                "candidates reached."
        }

    # --------------------------------------------------------
    # ENDPOINT NOT REACHED
    # --------------------------------------------------------

    print(
        "\n--- ENDPOINT NOT REACHED ---"
    )

    remaining = (
        target_candidate_count
        - current_count
    )

    print(
        f"Candidates still needed: {remaining}"
    )

    return {
        "status": "CONTINUE_SEARCH"
    }


# ============================================================
# 9. CONDITIONAL ROUTING — AFTER ENDPOINT CHECK
# ============================================================

def route_after_endpoint(
    state: RecruitOSState
):

    status = state.get(
        "status",
        ""
    )

    # --------------------------------------------------------
    # GOAL REACHED
    # --------------------------------------------------------

    if status == "GOAL_REACHED":

        print(
            "\n--- ROUTING: GOAL REACHED ---"
        )

        return "goal_reached"

    # --------------------------------------------------------
    # CONTINUE SEARCH
    # --------------------------------------------------------

    print(
        "\n--- ROUTING: CONTINUE SEARCH ---"
    )

    return "continue_search"


# ============================================================
# 10. NODE — LLM-POWERED SEARCH ADJUSTMENT
# ============================================================

def improve_search_node(
    state: RecruitOSState
):

    print(
        "\n--- LLM SEARCH ADJUSTMENT NODE ---"
    )

    goal = state.get(
        "goal",
        ""
    )

    current_skill = state.get(
        "skill",
        ""
    )

    attempted_queries = state.get(
        "attempted_queries",
        []
    )

    search_history = state.get(
        "search_history",
        []
    )

    qualified_candidates = state.get(
        "qualified_candidates",
        []
    )

    target_candidate_count = state.get(
        "target_candidate_count",
        1
    )

    minimum_score = state.get(
        "minimum_score",
        75
    )

    remaining_candidates = (
        target_candidate_count
        - len(qualified_candidates)
    )

    print(
        f"Current search: {current_skill}"
    )

    print(
        f"Qualified candidates found: "
        f"{len(qualified_candidates)}"
    )

    print(
        f"Candidates still needed: "
        f"{remaining_candidates}"
    )

    # --------------------------------------------------------
    # LLM PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are the Search Adjustment component of RecruitOS AI.

Your job is to suggest ONE new search query that can
help RecruitOS find additional qualified candidates.

Recruiter goal:
{goal}

Current search query:
{current_skill}

Target candidate count:
{target_candidate_count}

Minimum candidate score:
{minimum_score}

Qualified candidates found:
{len(qualified_candidates)}

Candidates still needed:
{remaining_candidates}

Search history:
{json.dumps(search_history, indent=2)}

Queries already attempted:
{json.dumps(attempted_queries, indent=2)}

Important rules:

1. Suggest only ONE new search query.
2. The query must be relevant to the recruiter goal.
3. Do not return a query that already appears in the
   attempted queries.
4. Do not invent candidate information.
5. Do not return explanations.
6. Return ONLY the search query text.
"""

    # --------------------------------------------------------
    # ASK LLM FOR NEXT SEARCH
    # --------------------------------------------------------

    response = llm.invoke(
        prompt
    )

    proposed_query = (
        response.content.strip()
    )

    # --------------------------------------------------------
    # CLEAN POSSIBLE QUOTES
    # --------------------------------------------------------

    proposed_query = (
        proposed_query
        .replace('"', "")
        .replace("'", "")
        .strip()
    )

    print(
        f"LLM proposed search: {proposed_query}"
    )

    # --------------------------------------------------------
    # EMPTY RESPONSE
    # --------------------------------------------------------

    if not proposed_query:

        print(
            "LLM did not provide a search query."
        )

        return {
            "status": "NO_PROGRESS",
            "stop_reason":
                "LLM did not provide a new "
                "search query."
        }

    # --------------------------------------------------------
    # PREVENT DUPLICATE QUERY
    # --------------------------------------------------------

    if proposed_query.lower() in [
        query.lower()
        for query in attempted_queries
    ]:

        print(
            "LLM proposed a query that was "
            "already attempted."
        )

        return {
            "status": "NO_PROGRESS",
            "stop_reason":
                "LLM proposed a duplicate "
                "search query."
        }

    # --------------------------------------------------------
    # ACCEPT NEW QUERY
    # --------------------------------------------------------

    print(
        f"New search query accepted: "
        f"{proposed_query}"
    )

    return {
        "skill": proposed_query,
        "status": "SEARCH_ADJUSTED"
    }


# ============================================================
# 11. CONDITIONAL ROUTING — AFTER SEARCH IMPROVEMENT
# ============================================================

def route_after_improvement(
    state: RecruitOSState
):

    status = state.get(
        "status",
        ""
    )

    # --------------------------------------------------------
    # NO PROGRESS
    # --------------------------------------------------------

    if status == "NO_PROGRESS":

        print(
            "\n--- ROUTING: NO PROGRESS ---"
        )

        return "no_progress"

    # --------------------------------------------------------
    # CONTINUE
    # --------------------------------------------------------

    print(
        "\n--- ROUTING: NEW SEARCH AVAILABLE ---"
    )

    return "search_again"


# ============================================================
# 12. NODE — FINAL ANSWER
# ============================================================

def final_answer_node(
    state: RecruitOSState
):

    print("\n--- FINAL ANSWER NODE ---")

    goal = state.get(
        "goal",
        ""
    )

    qualified_candidates = state.get(
        "qualified_candidates",
        []
    )

    target_candidate_count = state.get(
        "target_candidate_count",
        0
    )

    minimum_score = state.get(
        "minimum_score",
        0
    )

    stop_reason = state.get(
        "stop_reason",
        "Unknown"
    )

    # --------------------------------------------------------
    # NO QUALIFIED CANDIDATES
    # --------------------------------------------------------

    if not qualified_candidates:

        final_answer = f"""
RecruitOS Loop Result

Goal:
{goal}

Target Candidates:
{target_candidate_count}

Minimum Score:
{minimum_score}

Qualified Candidates Found:
0

Status:
{state.get("status")}

Stop Reason:
{stop_reason}
"""

        return {
            "final_answer": final_answer.strip()
        }

    # --------------------------------------------------------
    # BUILD CANDIDATE RESULTS
    # --------------------------------------------------------

    candidate_lines = []

    for index, candidate in enumerate(
        qualified_candidates,
        start=1
    ):

        candidate_lines.append(
            f"{index}. "
            f"{candidate['name']} "
            f"(Score: {candidate['score']})"
        )

    candidate_text = "\n".join(
        candidate_lines
    )

    # --------------------------------------------------------
    # SUCCESSFUL RESULT
    # --------------------------------------------------------

    final_answer = f"""
RecruitOS Loop Result

Goal:
{goal}

Target Candidates:
{target_candidate_count}

Minimum Score:
{minimum_score}

Qualified Candidates Found:
{len(qualified_candidates)}

Qualified Candidates:
{candidate_text}

Status:
{state.get("status")}

Stop Reason:
{stop_reason}
"""

    return {
        "final_answer": final_answer.strip()
    }


# ============================================================
# 13. CREATE LANGGRAPH STATE GRAPH
# ============================================================

builder = StateGraph(
    RecruitOSState
)


# ============================================================
# 14. ADD NODES
# ============================================================

builder.add_node(
    "search_candidates",
    search_candidates_node
)

builder.add_node(
    "evaluate_candidates",
    evaluate_candidates_node
)

builder.add_node(
    "check_endpoint",
    check_endpoint_node
)

builder.add_node(
    "improve_search",
    improve_search_node
)

builder.add_node(
    "final_answer",
    final_answer_node
)


# ============================================================
# 15. START → SEARCH
# ============================================================

builder.add_edge(
    START,
    "search_candidates"
)


# ============================================================
# 16. SEARCH → EVALUATE
# ============================================================

builder.add_edge(
    "search_candidates",
    "evaluate_candidates"
)


# ============================================================
# 17. EVALUATE → CHECK ENDPOINT
# ============================================================

builder.add_edge(
    "evaluate_candidates",
    "check_endpoint"
)


# ============================================================
# 18. CHECK ENDPOINT → CONDITIONAL ROUTING
# ============================================================

builder.add_conditional_edges(
    "check_endpoint",
    route_after_endpoint,
    {
        "goal_reached": "final_answer",
        "continue_search": "improve_search"
    }
)


# ============================================================
# 19. IMPROVE SEARCH → CONDITIONAL ROUTING
# ============================================================

builder.add_conditional_edges(
    "improve_search",
    route_after_improvement,
    {
        "search_again": "search_candidates",
        "no_progress": "final_answer"
    }
)


# ============================================================
# 20. FINAL ANSWER → END
# ============================================================

builder.add_edge(
    "final_answer",
    END
)


# ============================================================
# 21. COMPILE GRAPH
# ============================================================

graph = builder.compile()


# ============================================================
# 22. RUN RECRUITOS LOOP ENGINE
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # JOB DESCRIPTION
    # --------------------------------------------------------

    job_description = """
Business Development Manager

Must Have:
Business Development Manager - 3 years
Business Development
Client Relationship Management
Lead Generation
Contract Negotiation
Team Leadership

Nice to Have:
IT Recruitment
Talent Acquisition
ATS
VMS
MSP
"""

    # --------------------------------------------------------
    # RECRUITER GOAL
    # --------------------------------------------------------

    initial_state = {

        "user_request": (
            "Find qualified candidates with "
            "IT Recruitment experience."
        ),

        "goal": (
            "Find qualified candidates with "
            "IT Recruitment experience."
        ),

        "skill": "IT Recruitment",

        # ----------------------------------------------------
        # BUSINESS ENDPOINT
        # ----------------------------------------------------

        "target_candidate_count": 5,

        "minimum_score": 75,

        # ----------------------------------------------------
        # INITIAL LOOP STATE
        # ----------------------------------------------------

        "qualified_candidates": [],

        "attempted_queries": [],

        "search_history": [],

        "status": "STARTING",

        "stop_reason": "",

        # ----------------------------------------------------
        # JOB DESCRIPTION
        # ----------------------------------------------------

        "job_description": job_description
    }

    # --------------------------------------------------------
    # RUN GRAPH
    # --------------------------------------------------------

    result = graph.invoke(
        initial_state
    )

    # --------------------------------------------------------
    # DISPLAY FINAL RESULT
    # --------------------------------------------------------

    print("\n")

    print(
        "=" * 60
    )

    print(
        "FINAL RECRUITOS LOOP ENGINE RESULT"
    )

    print(
        "=" * 60
    )

    print(
        result["final_answer"]
    )