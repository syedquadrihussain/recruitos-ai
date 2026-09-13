import json
import os

from dotenv import load_dotenv
from groq import Groq

from app.services.candidate_tools import (
    search_candidates,
    score_candidate
)

from app.services.human_approval import (
    get_recruiter_approval
)


load_dotenv(
    r"C:\RecruitOS-AI\agent_learning\.env"
)


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


tools = [
    {
        "type": "function",
        "function": {
            "name": "search_candidates",
            "description": (
                "Search real uploaded resumes based on a skill. "
                "Returns candidates whose extracted skills contain "
                "the requested skill."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "skill": {
                        "type": "string",
                        "description": (
                            "The skill to search for."
                        )
                    }
                },
                "required": [
                    "skill"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "score_candidate",
            "description": (
                "Score a specific candidate against a job description. "
                "Returns qualification status, recommendation, "
                "matched skills, experience matching, semantic score, "
                "and final score."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": (
                            "The exact candidate name returned "
                            "by search_candidates."
                        )
                    },
                    "job_description": {
                        "type": "string",
                        "description": (
                            "The complete job description used "
                            "to evaluate the candidate."
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
]


def run_agent(user_request):

    messages = [
        {
            "role": "system",
            "content": (
                "You are RecruitOS AI, an AI recruiting assistant.\n\n"

                "GROUNDING RULES:\n"

                "1. Tool results are the source of truth.\n"

                "2. Never invent candidate skills, experience, "
                "companies, responsibilities, achievements, "
                "qualifications, or work history.\n"

                "3. Only report information explicitly present "
                "in the tool results or the user's request.\n"

                "4. Do not turn a skill into a claim about "
                "performance or achievement.\n"

                "5. Do not use phrases such as 'proven track record', "
                "'hands-on experience', 'extensive experience', "
                "'strong background', 'successfully managed', "
                "or similar claims unless the tool result explicitly "
                "contains that information.\n"

                "6. Do not infer responsibilities from a job title.\n"

                "7. Do not infer years of experience unless the "
                "tool result explicitly provides those years.\n"

                "8. If information is not available, say: "
                "'Not available in the candidate data.'\n"

                "9. When score_candidate returns final_score, "
                "qualified, or recommendation, report those values "
                "exactly.\n"

                "10. Never change, round, reinterpret, or estimate "
                "numerical scores returned by the tool.\n"

                "11. Recruiter decisions are human decisions. "
                "Report the recruiter decision exactly as returned "
                "by the human approval step.\n"

                "12. Do not make a new hiring decision after the "
                "recruiter has made a decision.\n"

                "13. Keep the final answer concise and factual.\n\n"

                "FINAL ANSWER FORMAT:\n"

                "Candidate: <candidate name>\n"
                "Final Score: <exact score>\n"
                "Qualified: <exact value>\n"
                "AI Recommendation: <exact recommendation>\n"
                "Recruiter Decision: <exact recruiter decision>\n\n"

                "Then list only the matched skills and explicitly "
                "available experience information."
            )
        },
        {
            "role": "user",
            "content": user_request
        }
    ]

    while True:

        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            parallel_tool_calls=False,
            temperature=0
        )

        message = response.choices[0].message

        if message.tool_calls:

            messages.append(message)

            for tool_call in message.tool_calls:

                tool_name = tool_call.function.name

                arguments = json.loads(
                    tool_call.function.arguments
                )

                if tool_name == "search_candidates":

                    tool_result = search_candidates(
                        arguments["skill"]
                    )

                elif tool_name == "score_candidate":

                    tool_result = score_candidate(
                        arguments["name"],
                        arguments["job_description"]
                    )

                    approval_result = get_recruiter_approval(
                        tool_result
                    )

                    tool_result["recruiter_decision"] = (
                        approval_result["recruiter_decision"]
                    )

                else:

                    tool_result = {
                        "error": "Unknown tool."
                    }

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(
                            tool_result
                        )
                    }
                )

            continue

        return message.content