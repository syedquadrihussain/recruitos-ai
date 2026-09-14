from groq import Groq
from dotenv import load_dotenv
import os

from app.services.search_state import SearchState
from app.services.search_strategies import SearchStrategy


load_dotenv()


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


ALLOWED_STRATEGIES = [
    strategy.value
    for strategy in SearchStrategy
]


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

1. Use the search state and previous results.
2. If the current strategy produced enough qualified
   candidates, recommend EXACT_SKILL.
3. If the current strategy produced few qualified
   candidates, recommend a broader strategy.
4. Avoid repeatedly recommending a strategy that has
   already failed.
5. Return ONLY the strategy name.
6. Do not return explanations.
7. Do not invent a new strategy.
"""


def choose_strategy_with_llm(
    state: SearchState
) -> SearchStrategy:

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

Last search candidates:
{state["last_search_candidates"]}

Last search qualified:
{state["last_search_qualified"]}

Last search duplicates:
{state["last_search_duplicates"]}

Previous search query:
{state["current_query"]}

Choose the next search strategy.
Return ONLY one allowed strategy name.
"""

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

    raw_strategy = (
        response.choices[0]
        .message
        .content
        .strip()
        .upper()
    )

    if raw_strategy not in ALLOWED_STRATEGIES:

        raise ValueError(
            f"LLM returned invalid strategy: "
            f"{raw_strategy}"
        )

    return SearchStrategy(raw_strategy)