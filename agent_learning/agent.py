import json
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# -----------------------------
# TOOL 1: Search Candidates
# -----------------------------

def search_candidates(skill):

    candidates = [
        {
            "name": "Ahmed",
            "skills": ["Python", "RAG", "FastAPI"]
        },
        {
            "name": "John",
            "skills": ["Java", "Spring Boot"]
        },
        {
            "name": "Sarah",
            "skills": ["Python", "Machine Learning"]
        }
    ]

    matching_candidates = []

    for candidate in candidates:

        if skill.lower() in [
            candidate_skill.lower()
            for candidate_skill in candidate["skills"]
        ]:
            matching_candidates.append(candidate)

    return json.dumps(matching_candidates)


# -----------------------------
# TOOL 2: Score Candidate
# -----------------------------

def score_candidate(name):

    scores = {
        "Ahmed": 5,
        "John": 2,
        "Sarah": 4
    }

    return f"{name} has a candidate score of {scores.get(name, 0)} out of 5."


# -----------------------------
# TOOLS GIVEN TO LLM
# -----------------------------

tools = [

    {
        "type": "function",
        "function": {
            "name": "search_candidates",
            "description": "Search candidates based on a skill.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill": {
                        "type": "string",
                        "description": "The skill to search for."
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
            "description": "Get the score of a candidate.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The candidate name."
                    }
                },
                "required": ["name"]
            }
        }
    }

]


# -----------------------------
# USER REQUEST
# -----------------------------

messages = [
    {
        "role": "user",
        "content": "Find candidates who know Python and tell me their scores."
    }
]


# ==================================================
# AGENT LOOP
# ==================================================

while True:

    # Ask the LLM what to do
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    message = response.choices[0].message

    # ----------------------------------------------
    # LLM wants to use a tool
    # ----------------------------------------------

    if message.tool_calls:

        print("\nLLM wants to use a tool.")

        # Add LLM's tool request to conversation
        messages.append(message)

        # Execute each requested tool
        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            print("Tool:", tool_name)
            print("Arguments:", arguments)

            # Execute search_candidates
            if tool_name == "search_candidates":

                tool_result = search_candidates(
                    arguments["skill"]
                )

            # Execute score_candidate
            elif tool_name == "score_candidate":

                tool_result = score_candidate(
                    arguments["name"]
                )

            else:

                tool_result = "Unknown tool."

            print("Tool result:", tool_result)

            # Send tool result back to LLM
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                }
            )

        # Go back to the top of the loop
        continue


    # ----------------------------------------------
    # LLM does NOT want another tool
    # ----------------------------------------------

    else:

        print("\nFinal answer:")
        print(message.content)

        break