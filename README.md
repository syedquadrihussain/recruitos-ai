# RecruitOS AI

**AI-Powered Resume Screening and Candidate Ranking System**

RecruitOS AI is an AI-powered recruitment screening system designed to help recruiters evaluate resumes against job descriptions more efficiently.

The project combines **semantic search, embeddings, vector retrieval, deterministic screening rules, reranking, and candidate scoring** to identify candidates who are most relevant to a given job description.

> **Problem first. User first. Technology second.**

---

## The Problem

Recruiters often need to review large numbers of resumes against job descriptions.

Traditional keyword-based screening can be time-consuming and may miss relevant candidates when a resume and job description use different wording for the same skill or experience.

RecruitOS AI approaches the problem differently:

> **Instead of starting with "Which AI technology should I use?", it starts with "What problem is the recruiter trying to solve, and where can technology genuinely help?"**

The goal is to build a recruitment screening system where AI techniques are used where they provide meaningful value, while deterministic rules are used where predictable and transparent decisions are important.

---

## Current MVP

The current MVP focuses on resume processing, semantic retrieval, candidate screening, scoring, and ranking.

The system can:

* Extract text from resumes
* Process PDF and DOCX resumes
* Chunk resume content
* Generate text embeddings
* Store and search vectors using FAISS
* Retrieve relevant candidates
* Rerank candidates based on matching skills
* Check must-have skills
* Compare required and candidate experience
* Calculate candidate match scores
* Calculate experience closeness
* Rank candidates based on screening results
* Return the closest candidates when no exact match exists

---

## Architecture

```text
                    Job Description
                           │
                           ▼
                      JD Parsing
                           │
                           │
                           │
Resume ──► Text Extraction ──► Chunking
                           │
                           ▼
                       Embeddings
                           │
                           ▼
                     FAISS Vector Store
                           │
                           ▼
                  Candidate Retrieval
                           │
                           ▼
                       Reranker
                           │
                           ▼
                  Candidate Screening
                  ┌────────┴─────────┐
                  │                  │
             Must-Have Skills   Experience
                  │                  │
                  └────────┬─────────┘
                           ▼
                     Match Scoring
                           │
                           ▼
                  Candidate Ranking
                           │
                           ▼
                 Closest Candidates
```

---

## Screening Approach

RecruitOS AI combines multiple signals when evaluating candidates.

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
Match Scoring
        ↓
Candidate Ranking
```

Semantic search helps identify candidates whose resumes are relevant to the job description even when the wording is different.

Deterministic rules are used for requirements such as years of experience and must-have skills because these requirements should be predictable, transparent, and easier to audit.

---

## Example Screening

Consider a job description requiring:

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
                    Job Description
                           │
                           ▼
                 Semantic Relevance
                           │
                           ▼
                    Required Skills
                           │
                           ▼
                 Required Experience
                           │
                           ▼
                 Nice-to-Have Skills
                           │
                           ▼
                    Match Scoring
                           │
                           ▼
                  Candidate Ranking
```

The system can also use **experience closeness** to rank candidates when no candidate completely satisfies all must-have requirements.

---

## Technology Stack

| Technology            | Purpose                  |
| --------------------- | ------------------------ |
| Python 3.x            | Core application         |
| FastAPI               | Backend API              |
| PyMuPDF               | PDF text extraction      |
| python-docx           | DOCX processing          |
| Sentence Transformers | Text embeddings          |
| all-MiniLM-L6-v2      | Current embedding model  |
| FAISS                 | Vector similarity search |
| NumPy                 | Vector processing        |

---

## Why These Technologies?

Technology is selected **after understanding the problem, not before it**.

For example, finding resumes that are semantically relevant to a job description requires more than simple keyword matching.

Therefore, RecruitOS AI uses:

**Sentence Transformers + FAISS**

to support semantic vector search and candidate retrieval.

For requirements such as years of experience and must-have skills, deterministic rules are preferred because they provide predictable and transparent results.

Newer AI techniques will be adopted only when they provide a meaningful and stable improvement over the existing solution.

---

## Project Structure

```text
recruitos-ai/
│
├── app/
│   ├── main.py
│   ├── routers/
│   └── services/
│
├── uploads/
│
├── requirements.txt
├── README.md
└── LICENSE
```

> The project structure will evolve as additional modules are implemented.

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

#### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the FastAPI application

```bash
uvicorn app.main:app --reload
```

### 6. Open the API documentation

Open:

```text
http://127.0.0.1:8000/docs
```

---

## Development Philosophy

RecruitOS AI follows a simple development philosophy:

> **Problem First. User First. Technology Second.**

The project is developed incrementally using:

```text
Build
  ↓
Test
  ↓
Evaluate
  ↓
Improve
  ↓
Document
  ↓
Deploy
```

The goal is not to add AI technologies simply because they are available.

Each technology should have a clear purpose within the recruitment workflow.

---

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

### Future Direction

Longer-term capabilities may include:

* Agentic recruitment workflows
* Role-based access control (RBAC)
* Multimodal candidate screening
* Multi-agent architecture
* Additional recruitment workflow automation

These capabilities will be introduced as they move from concept into active development and provide genuine value to the system.

---

## Status

**Working MVP — Active Development**

RecruitOS AI is being developed incrementally from a real recruitment workflow toward a production-oriented AI solution.

The current focus is on building a reliable foundation for:

```text
Resume Processing
       ↓
Semantic Retrieval
       ↓
Candidate Screening
       ↓
Candidate Scoring
       ↓
Candidate Ranking
```

---

## Contact

Built by **Syed Hussain Quadri**

Feedback and suggestions are welcome through GitHub issues and discussions.

---

## License

MIT License — see [`LICENSE`](LICENSE) for details.
