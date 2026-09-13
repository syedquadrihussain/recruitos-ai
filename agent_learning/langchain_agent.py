import sys
import json
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain.tools import tool


# --------------------------------------------------
# 1. Add RecruitOS project root to Python path
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


# --------------------------------------------------
# 2. Import real RecruitOS tools
# --------------------------------------------------

from app.services.candidate_tools import (
    search_candidates as recruitos_search_candidates,
    score_candidate as recruitos_score_candidate
)


# --------------------------------------------------
# 3. Load environment variables
# --------------------------------------------------

load_dotenv()


# --------------------------------------------------
# 4. RecruitOS Candidate Search Tool
# --------------------------------------------------

@tool
def search_candidates(skill: str) -> str:
    """
    Search real RecruitOS candidates who have a
    specific skill.
    """

    candidates = recruitos_search_candidates(skill)

    if not candidates:
        return f"No candidates found with {skill}."

    return json.dumps(
        candidates,
        indent=2
    )


# --------------------------------------------------
# 5. RecruitOS Candidate Scoring Tool
# --------------------------------------------------

@tool
def score_candidate(
    name: str,
    job_description: str
) -> str:
    """
    Score a real RecruitOS candidate against a
    job description.
    """

    result = recruitos_score_candidate(
        name,
        job_description
    )

    return json.dumps(
        result,
        indent=2
    )


# --------------------------------------------------
# 6. Create the Groq LLM
# --------------------------------------------------

model = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)


# --------------------------------------------------
# 7. Create the LangChain Agent
# --------------------------------------------------

agent = create_agent(
    model=model,
    tools=[
        search_candidates,
        score_candidate
    ],
    system_prompt="""
You are RecruitOS AI, an AI recruiting assistant.

You have two tools:

1. search_candidates
   Finds candidates from the real RecruitOS
   candidate data.

2. score_candidate
   Scores a candidate against a job description
   using the RecruitOS scoring engine.


==================================================
GROUNDING RULES
==================================================

Tool results are the ONLY source of truth.

Never invent or assume candidate information.

Do NOT add information that is not explicitly
returned by the tools.

Do NOT claim:

- proven track record
- revenue generation
- cultural fit
- performance
- achievements
- responsibilities
- years of experience
- skills
- technologies
- leadership experience

unless the tool result explicitly provides that
information.


==================================================
SCORING RULES
==================================================

The score returned by score_candidate is the
official RecruitOS score.

Never calculate another score.

Never change the score.

Never round the score differently.

Use the exact:

- final_score
- qualified
- recommendation
- matched_skills
- experience information

returned by the scoring tool.


==================================================
CANDIDATE SELECTION
==================================================

When asked to find and evaluate candidates:

1. Search using search_candidates.

2. Review the returned candidates.

3. Select the most relevant candidate based ONLY
   on the returned information.

4. Send that candidate to score_candidate.

5. Use the scoring result as the final source
   of truth.


==================================================
FINAL ANSWER
==================================================

Keep the answer concise and evidence-based.

Use this format:

Candidate:
<name>

Overall Experience:
<exact value returned by tool>

Final Score:
<exact score returned by tool>

Qualified:
<exact value returned by tool>

AI Recommendation:
<exact recommendation returned by tool>

Evidence:
- Only list information explicitly returned
  by the tools.

Do not add unsupported conclusions.

Do not recommend an interview unless the recruiter
asks for a recommendation about next steps.

The AI recommendation is NOT the recruiter's final
decision.
"""
)


# --------------------------------------------------
# 8. Run the Agent
# --------------------------------------------------

if __name__ == "__main__":

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

    user_request = f"""
    Find candidates with IT Recruitment experience
    and evaluate the most relevant candidate for
    this Business Development Manager position.

    Job Description:
    {job_description}
    """

    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_request
                }
            ]
        }
    )

    print("\nFinal Answer:\n")

    print(
        response["messages"][-1].content
    )