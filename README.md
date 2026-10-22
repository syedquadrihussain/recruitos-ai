# RecruitOS AI

**AI-Powered Resume Screening and Candidate Ranking System**

RecruitOS AI is an AI-powered recruitment screening system designed to help recruiters evaluate resumes against job descriptions more efficiently.

The project combines **semantic search, embeddings, vector retrieval, deterministic screening rules, reranking, candidate scoring, and agentic search workflows** to identify candidates who are most relevant to a job description.

> **Problem first. User first. Technology second.**

---

## The Problem

Recruiters often need to review large numbers of resumes against job descriptions.

Traditional keyword-based screening can be time-consuming and may miss relevant candidates when a resume and job description use different wording for the same skill or experience.

RecruitOS AI approaches the problem differently:

> Instead of starting with "Which AI technology should I use?", it starts with "What problem is the recruiter trying to solve, and where can technology genuinely help?"

The goal is to use AI where it provides meaningful value and deterministic rules where predictable, transparent decisions are important.

---

## Current MVP

The current MVP focuses on resume processing, semantic retrieval, candidate screening, scoring, ranking, and agentic search.

Current capabilities include:

- Extracting text from resumes
- Processing PDF and DOCX resumes
- Chunking resume content
- Generating text embeddings
- Storing and searching vectors using FAISS
- Retrieving relevant candidates
- Reranking candidates based on matching skills
- Checking must-have skills
- Comparing required and candidate experience
- Calculating candidate match scores
- Calculating experience closeness
- Ranking candidates based on screening results
- Returning the closest candidates when no exact match exists
- Orchestrating search, screening, and matching through a supervisor-based multi-agent workflow
- Applying bounded search attempts and loop-termination safeguards
- Handling search workflow failures to reduce uncontrolled retries

The project remains under active development. Capabilities and behavior may evolve as the system is tested and improved.

---

## Architecture

The core retrieval and screening workflow:

```text
                    Job Description
                           |
                           v
                       JD Parsing
                           |
                           v
Resume --> Text Extraction --> Chunking
                           |
                           v
                       Embeddings
                           |
                           v
                    FAISS Vector Store
                           |
                           v
                   Candidate Retrieval
                           |
                           v
                        Reranker
                           |
                           v
                  Candidate Screening
                  /                \
                 v                  v
          Must-Have Skills     Experience
                  \                /
                   v              v
                     Match Scoring
                           |
                           v
                   Candidate Ranking
                           |
                           v
                  Closest Candidates
```

### Agentic Search and Multi-Agent Workflow

RecruitOS AI includes a supervisor-based workflow for coordinating search, screening, and candidate matching.

```text
                    User Request
                         |
                         v
                    Supervisor
                         |
                         v
                   Search Agent
                         |
                         v
                 Candidate Retrieval
                         |
                         v
                  Screening Agent
                         |
                         v
                  Matching / Ranking
                         |
                         v
                  Workflow Decision
                    /          \
              Continue        Finish
                  |              |
                  v              v
             Bounded Search    Results
                  |
                  v
          Loop-Safety Checks
```

The supervisor coordinates the workflow, while loop-safety controls help prevent uncontrolled repeated searches. Search attempts are bounded, and workflow termination is handled through explicit state and routing decisions.

---

## Screening Approach

RecruitOS AI combines multiple signals when evaluating candidates:

```text
Semantic Relevance
        +
Required Skills
        +
Required Experience
        +
Nice-to-Have Skills
        |
        v
Candidate Screening
        |
        v
Match Scoring
        |
        v
Candidate Ranking
```

Semantic search helps identify candidates whose resumes are relevant to a job description even when the wording differs.

Deterministic rules are used for requirements such as must-have skills and experience because these requirements should be predictable, transparent, and easier to audit.

Candidate scores support recruiter decision-making; they should not be treated as a substitute for human review.

---

## Example Screening

Consider a job description requiring:

```text
Must Have:
- Python: 5 years
- FastAPI: 3 years

Nice to Have:
- RAG
- Docker
```

The system evaluates relevant candidate information through retrieval, screening, experience comparison, scoring, and ranking.

```text
                    Job Description
                           |
                           v
                  Semantic Relevance
                           |
                           v
                     Required Skills
                           |
                           v
                  Required Experience
                           |
                           v
                  Nice-to-Have Skills
                           |
                           v
                     Match Scoring
                           |
                           v
                   Candidate Ranking
```

Experience closeness can help rank candidates when no candidate completely satisfies every requirement. Final hiring decisions remain with the recruiter.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.x | Core application |
| FastAPI | Backend API |
| PyMuPDF | PDF text extraction |
| python-docx | DOCX processing |
| Sentence Transformers | Text embeddings |
| all-MiniLM-L6-v2 | Embedding model |
| FAISS | Vector similarity search |
| NumPy | Vector processing |
| Groq | LLM API integration |
| LangChain | LLM application components |
| LangGraph | Workflow and agent orchestration |

The specific components used by each workflow may evolve as the project develops.

---

## Why These Technologies?

Technology is selected **after understanding the problem, not before it**.

Finding resumes that are semantically relevant to a job description requires more than simple keyword matching. Sentence Transformers and FAISS support semantic vector search and candidate retrieval.

For requirements such as years of experience and must-have skills, deterministic rules can provide predictable and explainable results.

LangGraph supports explicit workflow state and routing for multi-step agent orchestration. Search limits and termination controls help keep iterative workflows bounded.

New AI techniques will be adopted only when they provide meaningful improvements in quality, reliability, cost, or maintainability.

---

## Project Structure

The project is organized around the application, services, and tests. The structure may evolve as additional capabilities are implemented.

```text
recruitos-ai/
|
├── app/
│   ├── main.py
│   ├── routers/
│   └── services/
|
├── tests/
├── agent_learning/
├── uploads/
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
```

This is a simplified overview rather than an exhaustive listing of every file.

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/syedquadrihussain/recruitos-ai.git
cd recruitos-ai
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 5. Configure environment variables

Create a local `.env` file using `.env.example` as a reference.

Add your own Groq API key:

```text
GROQ_API_KEY=your_groq_api_key_here
```

Keep actual API keys and secrets in `.env`. Do not commit real credentials to Git.

Some workflows may require an API key, while other components may run without an LLM call.

### 6. Start the FastAPI application

```powershell
uvicorn app.main:app --reload
```

### 7. Open the API documentation

Visit:

```text
http://127.0.0.1:8000/docs
```

This opens the FastAPI interactive API documentation.

---

## Testing and Validation

Run the project's test suite from the repository root with the virtual environment activated:

```powershell
python -m pytest -q
```

To check Python syntax across the application and test code:

```powershell
python -m compileall -q app tests
```

Test results depend on the current code, environment configuration, and available dependencies. Passing automated tests does not by itself establish production readiness.

---

## Development Philosophy

RecruitOS AI follows a simple development philosophy:

> **Problem First. User First. Technology Second.**

The development process is iterative:

```text
Build
  |
  v
Test
  |
  v
Evaluate
  |
  v
Improve
  |
  v
Document
  |
  v
Deploy
```

The goal is not to add AI technologies simply because they are available. Each technology should have a clear purpose within the recruitment workflow.

---

## Roadmap

### Completed / Implemented

- Resume text extraction
- PDF and DOCX processing
- Resume chunking
- Text embeddings
- FAISS vector retrieval
- Candidate retrieval
- Basic reranking
- Candidate screening
- Match scoring
- Experience closeness scoring
- Candidate ranking
- Fallback ranking when no exact match exists
- Agentic search workflow foundation
- Supervisor-based multi-agent orchestration
- Search-loop safety and bounded retry behavior
- Workflow state and termination safeguards

### In Progress

- Further improvements to the scoring engine
- Automatic candidate profile extraction
- End-to-end screening workflow improvements
- Improved reranking and relevance evaluation
- LLM-based candidate explanations
- Expanded agentic search capabilities
- More comprehensive workflow and failure-case testing

### Next Up

- Boolean search
- Visa filtering
- Location filtering
- Evaluation framework for candidate ranking quality
- Recruitment chatbot with memory
- Live deployment

### Future Direction

Longer-term capabilities may include:

- MCP-based enterprise integrations
- ATS/VMS integrations
- Human-in-the-loop recruitment workflows
- Role-based access control (RBAC)
- Multimodal candidate screening
- Additional recruitment workflow automation
- Fine-tuning where evaluation demonstrates a genuine need

These capabilities will be introduced as they move from concept into active development and provide genuine value to the system.

---

## Status

**Working MVP — Active Development**

RecruitOS AI is being developed incrementally from real recruitment workflows toward a production-oriented AI solution.

The current foundation brings together:

```text
Resume Processing
       |
       v
Semantic Retrieval
       |
       v
Candidate Screening
       |
       v
Candidate Scoring
       |
       v
Candidate Ranking
       |
       v
Agentic Search
       |
       v
Supervisor-Based Multi-Agent Workflow
```

The project is not presented as production-ready. Security, reliability, ranking evaluation, deployment, and enterprise integration require continued implementation and validation.

---

## Contact

Built by **Syed Hussain Quadri**

For professional inquiries, collaboration, feedback, or opportunities:

**Email:** [quadrissh@gmail.com](mailto:quadrissh@gmail.com)

**GitHub:** https://github.com/syedquadrihussain

---

## License

RecruitOS AI is proprietary software.

The source code is publicly available for viewing and evaluation purposes.

No permission is granted to copy, modify, distribute, sublicense, publish, or commercially use this software without prior written permission from the copyright holder.

For licensing or commercial use inquiries:

**Email:** [quadrissh@gmail.com](mailto:quadrissh@gmail.com)