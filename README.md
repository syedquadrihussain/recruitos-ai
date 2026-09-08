# RecruitOS AI

AI-powered recruitment screening and candidate ranking system.

## The Problem

Recruiters often need to review large numbers of resumes against job descriptions. Traditional keyword-based screening is time-consuming and can miss relevant candidates when the resume and job description use different wording for the same skill or experience.

RecruitOS AI starts from a different question than **"which AI technology should I use?"** — it starts from **"what problem is the recruiter trying to solve, and where does technology genuinely help?"**

## Quick Start

Clone the repository:

```bash
git clone https://github.com/syedquadrihussain/recruitos-ai.git
cd recruitos-ai
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI application:

```bash
uvicorn app.main:app --reload
```

Open the API documentation:

```text
http://127.0.0.1:8000/docs
```

## Architecture

```text
                    Job Description                    Resume
                          │                               │
                          ▼                               ▼
                     JD Parser                     Text Extraction
                          │                               │
                          │                          Chunking
                          │                               │
                          │                          Embeddings
                          │                               │
                          │                        FAISS Vector Store
                          │                               │
                          └──────────────┬────────────────┘
                                         ▼
                               Candidate Retrieval
                                         │
                                         ▼
                                     Reranker
                                         │
                                         ▼
                              Candidate Screening
                          (must-have skills, experience)
                                         │
                                         ▼
                                Match Scoring
                                         │
                                         ▼
                              Final Candidate Rank
```

## Current MVP

The system can:

* Extract and chunk resume content
* Generate embeddings and store/search vectors using FAISS
* Retrieve relevant candidates
* Rerank candidates based on matching skills
* Check must-have skills and compare required vs. candidate experience
* Calculate match scores and experience closeness
* Rank candidates
* Return the closest candidates when no exact match exists, using experience closeness to rank candidates who do not meet all must-have requirements

## Technology Stack

| Technology            | Purpose                  |
| --------------------- | ------------------------ |
| Python 3.x            | Core application         |
| FastAPI               | Backend API              |
| PyMuPDF               | PDF processing           |
| python-docx           | DOCX processing          |
| Sentence Transformers | Text embeddings          |
| all-MiniLM-L6-v2      | Current embedding model  |
| FAISS                 | Vector similarity search |
| NumPy                 | Vector processing        |

## Why These Technologies

Technology is selected **after the problem is understood, not the other way around.**

**Example:** Finding resumes that are semantically relevant to a job description calls for semantic vector search, so the project uses **Sentence Transformers + FAISS**.

Requirements such as years of experience are evaluated using deterministic rules because they should be predictable, transparent, and easy to audit.

Newer AI techniques will be adopted only when they provide a meaningful and stable improvement over what is already working.

## Example Screening

For a job description requiring:

```text
Must Have:
Python - 5 years
FastAPI - 3 years

Nice to Have:
RAG
Docker
```

Candidates are evaluated using:

```text
Semantic Relevance
       +
Required Skills
       +
Required Experience
       +
Nice-to-Have Skills
       ↓
Candidate Screening
       ↓
Candidate Ranking
```

## Roadmap

### Completed

* Resume text extraction
* Resume chunking
* Embeddings
* FAISS retrieval
* Candidate retrieval
* Basic reranking
* Candidate screening
* Match scoring
* Experience closeness scoring
* Final candidate ranking
* Fallback ranking when no exact match exists

### In Progress

* Improved scoring engine
* Automatic candidate profile extraction
* Complete FastAPI screening workflow
* Improved reranking
* LLM-based candidate explanations

### Next Up

* Evaluation framework for candidate ranking quality
* Recruitment chatbot with memory
* Live deployment

Longer-term plans such as agentic workflows, RBAC, multimodal screening, and multi-agent architecture will be added as they move from concept to active development.

## Development Philosophy

**Problem first. User first. Technology second.**

```text
Build → Test → Evaluate → Improve → Document → Deploy
```

## Status

**Working MVP — Active Development**

RecruitOS AI is being developed incrementally from a real recruitment workflow toward a production-oriented AI solution.

## Contact

Built by **Syed Hussain Quadri**

Feedback and suggestions are welcome through GitHub issues and discussions.

## License

MIT License — see `LICENSE` for details.
