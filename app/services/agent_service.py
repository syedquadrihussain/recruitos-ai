import os

from dotenv import load_dotenv
from groq import Groq

from app.services.candidate_tools import (
    search_candidates,
    score_candidate
)


# Load environment variables from .env
load_dotenv()


# Get Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY was not found. "
        "Please create a .env file in the project root "
        "and add GROQ_API_KEY=your_api_key"
    )


# Create Groq client
client = Groq(
    api_key=GROQ_API_KEY
)


# RecruitOS AI system instructions
SYSTEM_PROMPT = """
You are RecruitOS AI, an AI recruiting decision-support assistant.

Your job is to help recruiters search, evaluate, and understand
candidate information.

IMPORTANT RULES:

1. Candidate information must come from RecruitOS tools.

2. Tool results are the source of truth.

3. Never invent candidate skills.

4. Never invent candidate experience.

5. Never invent companies or job responsibilities.

6. Never infer years of experience that are not returned by the tool.

7. When scoring a candidate, use the exact score returned by
   the scoring tool.

8. When qualification is returned by the scoring tool, report
   that exact qualification result.

9. When a recommendation is returned by the scoring tool,
   report that exact recommendation.

10. Do not make unsupported claims such as:
    - "proven track record"
    - "excellent candidate"
    - "strong technical background"
    unless the tool results explicitly support them.

11. If the requested candidate or information is not available
    from the tools, clearly say that it was not found.

12. Do not fabricate information to satisfy the recruiter.

13. The recruiter remains the final decision maker.

RecruitOS AI assists the recruiter.
It does not replace the recruiter's final decision.
"""


def run_agent(
    user_request: str
):
    """
    Run the RecruitOS AI agent.

    This function receives a recruiter request,
    decides which RecruitOS tool should be used,
    executes the tool, and returns the result.
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_request
            }
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "search_candidates",
                    "description": (
                        "Search RecruitOS candidates by skill."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "skill": {
                                "type": "string",
                                "description": (
                                    "Skill to search for."
                                )
                            }
                        },
                        "required": ["skill"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "score_candidate",
                    "description": (
                        "Score a candidate against a "
                        "job description."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": (
                                    "Candidate name."
                                )
                            },
                            "job_description": {
                                "type": "string",
                                "description": (
                                    "Job description used "
                                    "for candidate scoring."
                                )
                            }
                        },
                        "required": [
                            "name",
                            "job_description"
                        ]
                    }
                }
            }
        ],
        tool_choice="auto"
    )

    message = response.choices[0].message

    # If the model does not request a tool,
    # return its normal response.
    if not message.tool_calls:
        return message.content

    tool_results = []

    for tool_call in message.tool_calls:

        function_name = tool_call.function.name

        arguments = tool_call.function.arguments

        import json

        arguments = json.loads(arguments)

        if function_name == "search_candidates":

            result = search_candidates(
                arguments["skill"]
            )

        elif function_name == "score_candidate":

            result = score_candidate(
                arguments["name"],
                arguments["job_description"]
            )

        else:

            result = {
                "error": (
                    f"Unknown tool: {function_name}"
                )
            }

        tool_results.append(
            {
                "tool_call_id": tool_call.id,
                "result": result
            }
        )

    # Send tool results back to the LLM
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_request
        },
        message
    ]

    for tool_result in tool_results:

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_result[
                    "tool_call_id"
                ],
                "content": json.dumps(
                    tool_result["result"]
                )
            }
        )

    final_response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        temperature=0,
        messages=messages
    )

    return final_response.choices[0].message.content