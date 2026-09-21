from groq import Groq
from dotenv import load_dotenv
import os

from app.services.search_state import SearchState
from app.services.search_strategies import SearchStrategy


# =========================================================
# Environment
# =========================================================

load_dotenv()


# =========================================================
# Groq Client
# =========================================================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# =========================================================
# Allowed Search Strategies
# =========================================================

ALLOWED_STRATEGIES = [
    strategy.value
    for strategy in SearchStrategy
]


# =========================================================
# Supervisor / Planner Instructions
# =========================================================

SYSTEM_PROMPT = """
You are the Intelligent Search Planner for RecruitOS AI.

Your job is to recommend the NEXT search strategy
for finding qualified candidates.

You may ONLY choose one of these strategies:

EXACT_SKILL
RELATED_SKILL
ROLE
DOMAIN
SEMANTIC_SEARCH
HYBRID_SEARCH
SOURCE_SEARCH

Rules:

1. Use the complete search state and previous results.

2. If enough qualified candidates have already been found,
   return EXACT_SKILL.

3. If the previous strategy produced no new qualified
   candidates, choose a different and broader strategy.

4. If several consecutive searches produced no new
   qualified candidates, strongly prefer changing
   the search strategy.

5. Avoid repeatedly recommending a strategy that has
   already failed to produce useful candidates.

6. Review the list of strategies already attempted.

7. Prefer a strategy that has not already been attempted
   when the current search is not producing progress.

8. Prefer broader search strategies when exact searches
   are not producing qualified candidates.

9. Do not decide candidate qualification yourself.

10. Candidate qualification is handled by RecruitOS AI's
    deterministic qualification logic.

11. Return ONLY the strategy name.

12. Do not return explanations.

13. Do not invent a new strategy.
"""


# =========================================================
# LLM Search Planner
# =========================================================

def choose_strategy_with_llm(
    state: SearchState
) -> SearchStrategy:

    # -----------------------------------------------------
    # Read strategy history safely
    # -----------------------------------------------------

    attempted_strategies = state.get(
        "attempted_strategies",
        []
    )

    # -----------------------------------------------------
    # Read loop progress safely
    # -----------------------------------------------------

    no_progress_count = state.get(
        "no_progress_count",
        0
    )

    # -----------------------------------------------------
    # Read search metrics safely
    # -----------------------------------------------------

    last_search_candidates = state.get(
        "last_search_candidates",
        0
    )

    last_search_qualified = state.get(
        "last_search_qualified",
        0
    )

    last_search_duplicates = state.get(
        "last_search_duplicates",
        0
    )

    current_strategy = state.get(
        "current_strategy",
        ""
    )

    current_query = state.get(
        "current_query",
        ""
    )

    # -----------------------------------------------------
    # Build planner prompt
    # -----------------------------------------------------

    user_prompt = f"""
Recruiter goal:
{state["goal"]}

Target qualified candidates:
{state["target_count"]}

Qualified candidates so far:
{len(state["qualified_candidates"])}

Total candidates found so far:
{len(state["candidates"])}

Current strategy:
{current_strategy}

Strategies already attempted:
{attempted_strategies}

Last search candidates:
{last_search_candidates}

Last search qualified:
{last_search_qualified}

Last search duplicates:
{last_search_duplicates}

Consecutive searches with no new qualified candidates:
{no_progress_count}

Previous search query:
{current_query}

Based on the complete search state,
choose the NEXT search strategy.

If the current strategy is not producing
new qualified candidates, change the strategy.

Prefer a strategy that has not already been attempted.

Return ONLY one allowed strategy name.
"""

    # -----------------------------------------------------
    # Call Groq LLM
    # -----------------------------------------------------

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0
    )

    # -----------------------------------------------------
    # Read LLM response
    # -----------------------------------------------------

    raw_strategy = (
        response
        .choices[0]
        .message
        .content
        .strip()
        .upper()
    )

    # -----------------------------------------------------
    # Validate strategy
    # -----------------------------------------------------

    if raw_strategy not in ALLOWED_STRATEGIES:

        raise ValueError(
            f"LLM returned invalid strategy: "
            f"{raw_strategy}"
        )

    # -----------------------------------------------------
    # Return enum
    # -----------------------------------------------------

    return SearchStrategy(
        raw_strategy
    )