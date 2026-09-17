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
# Allowed Strategies
# =========================================================

ALLOWED_STRATEGIES = [
    strategy.value
    for strategy in SearchStrategy
]


# =========================================================
# LLM System Prompt
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
# LLM Strategy Planner
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
{state["current_strategy"]}

Strategies already attempted:
{attempted_strategies}

Last search candidates:
{state["last_search_candidates"]}

Last search qualified:
{state["last_search_qualified"]}

Last search duplicates:
{state["last_search_duplicates"]}

Consecutive searches with no new qualified candidates:
{state["no_progress_count"]}

Previous search query:
{state["current_query"]}

Based on the complete search state,
choose the NEXT search strategy.

If the current strategy is not producing
new qualified candidates, change the strategy.

Prefer a strategy that has not already been attempted.

Return ONLY one allowed strategy name.
"""

    # -----------------------------------------------------
    # Call LLM
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
    # Extract response
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
    # Return SearchStrategy
    # -----------------------------------------------------

    return SearchStrategy(
        raw_strategy
    )