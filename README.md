# RationSahayak

![RationSahayak CI](https://github.com/ruchadange1/Sanjivani-sj-14-rationsahayak/actions/workflows/ci.yml/badge.svg)

**AI-Powered Ration Assistance System for Maharashtra**

RationSahayak is an AI-powered ration assistance system designed to help users access ration-related information, understand their monthly foodgrain entitlements, and verify ration distribution.

## Live Application

| Service | URL |
|---|---|
| Streamlit Frontend | https://rationsahayak-ui.onrender.com |
| FastAPI Backend | https://rationsahayak-api.onrender.com |
| Swagger Documentation | https://rationsahayak-api.onrender.com/docs |
| API Health Check | https://rationsahayak-api.onrender.com/health |

## Key Features

### 1. AI Ration Assistant
- Answers questions related to ration cards, eligibility and government schemes.
- Uses Retrieval-Augmented Generation (RAG).
- Displays source citations to support generated answers.

### 2. User Feedback
- Allows users to mark AI responses as Helpful or Not Helpful.
- Stores feedback in `data/feedback.csv`.
- Records the question, answer, timestamp and feedback rating.

### 3. Monthly Ration Calculator
- Supports AAY and PHH ration cards.
- Calculates monthly foodgrain entitlement.
- AAY: 35 kg per household per month.
- PHH: 5 kg per person per month.

### 4. e-PoS Verification
- Compares calculated entitlement with the actual quantity received.
- Displays the difference between expected and received quantities.
- Helps users identify possible discrepancies.

### 5. Downloadable Ration Slip
- Generates a monthly ration slip.
- Includes card type, family size, expected grain, received grain and quantity difference.
- Allows users to download the slip.

## Day 8 – RAG Evaluation Results

Evaluated two RAG configurations using 15 test questions.

| Configuration | Chunk Size | Top-K | Total Chunks | Retrieval Accuracy | Citation Availability |
|---|---:|---:|---:|---:|---:|
| Config 1 (Winner) | 400 | 3 | 23 | 100% | 100% |
| Config 2 | 600 | 5 | 14 | 100% | 100% |

**Winner: Config 1**

Config 1 was selected because it achieved the same evaluation scores while retrieving fewer chunks per query.

*Note: Retrieval accuracy measures keyword matching in retrieved documents, not the correctness of generated answers. Citation availability measures whether source metadata was returned.*

## Day 10 – Application Improvements and Screenshots

### Application Screenshots

#### 1. Dashboard

![RationSahayak Dashboard](screenshots/Dashboard.png)

#### 2. AI Chatbot

![RationSahayak Chatbot](screenshots/Chatbot.png)

#### 3. Monthly Ration Calculator

![RationSahayak Ration Calculator](screenshots/Ration_Cal.png)

### Feedback Collection

User feedback is stored locally in `data/feedback.csv` for future analysis and improvement of the application.

### Note

The ration calculator provides an estimated entitlement based on the selected card type and family size. The e-PoS comparison is intended for verification and is not an official confirmation of ration distribution.

## Day 11 – Testing, Code Quality and Docker Deployment

### S1 – Testing and Code Quality

Created a `tests/` directory containing 15 pytest test cases.

Testing includes:

- Records loading and retrieval.
- Keyword search and search with no results.
- Record count by topic.
- FastAPI `/health` endpoint.
- FastAPI `/records` endpoint.
- FastAPI `/search` endpoint.
- FastAPI `/ask` endpoint using a fake LLM.
- AAY and PHH ration entitlement calculations.
- Invalid family size and invalid card type handling.
- LangGraph ration entitlement tool integration.

**Testing Results:**
- Pytest: 15 tests passed.
- Ruff: All checks passed.

### S2 – Docker Setup

Created the following Docker configuration files:

- `Dockerfile` – Defines the application image and dependencies.
- `.dockerignore` – Excludes unnecessary files and sensitive information from the Docker build context.
- `docker-compose.yml` – Runs the FastAPI backend and Streamlit frontend as separate services.

Both services communicate through Docker Compose networking.

### Run with Docker

**Prerequisites:**
- Docker Desktop installed and running.
- Docker Compose.
- Required environment variables configured in the `.env` file.

**Steps to run the application:**

1. Clone the repository:

```bash
git clone https://github.com/ruchadange1/Sanjivani-sj-14-rationsahayak.git
```

2. Navigate to the project directory:

```bash
cd Sanjivani-sj-14-rationsahayak
```

3. Create and configure the `.env` file with the required API credentials and environment variables.

4. Build and start the application:

```bash
docker compose up --build
```

### Local Application URLs

| Service | URL |
|---|---|
| Streamlit Frontend | http://localhost:8501 |
| FastAPI Backend | http://localhost:8000 |
| FastAPI Swagger Documentation | http://localhost:8000/docs |
| API Health Check | http://localhost:8000/health |

### Stop the Application

```bash
docker compose down
```

## Day 12 – GitHub Actions CI/CD

Implemented a GitHub Actions workflow for automated testing and code quality checks.

**Workflow file:** `.github/workflows/ci.yml`

### CI Pipeline

The pipeline performs:

1. Ruff code-quality checks.
2. Pytest automated testing.
3. Docker image build verification.

### CI Results

- Ruff checks: Passed.
- Pytest: 15 tests passed.
- Docker build: Successful.
- GitHub Actions: All required checks green.

### Pull Request Workflow

- Created a feature branch for the CI/CD implementation.
- Opened a pull request.
- Verified that CI checks passed.
- Merged the pull request into the `main` branch.

The GitHub Actions status badge at the top of this README displays the workflow status.

## Deployment – Render

Deployed RationSahayak using Render with separate frontend and backend services.

### Backend Deployment

- Platform: Render.
- Framework: FastAPI.
- Runtime: Docker.
- API health endpoint: `/health`.
- Automatic document indexing during application startup.
- Groq integration for LLM-based answer generation.

### Frontend Deployment

- Platform: Render.
- Framework: Streamlit.
- Runtime: Docker.
- Connected to the deployed FastAPI backend using the `API_URL` environment variable.

### Deployment Verification

Verified the following:

- Frontend loads successfully.
- Backend health endpoint returns a healthy response.
- RAG question answering works.
- Retrieved source citations are returned.
- Monthly ration calculator works.
- e-PoS verification identifies quantity differences.
- User feedback interaction works.

## Technologies Used

- **Programming Language:** Python
- **Backend:** FastAPI
- **Frontend:** Streamlit
- **LLM Provider:** Groq
- **AI Architecture:** Retrieval-Augmented Generation (RAG)
- **Agent Framework:** LangGraph
- **Vector Database:** ChromaDB
- **Embeddings:** FastEmbed
- **Testing:** Pytest
- **Code Quality:** Ruff
- **Containerization:** Docker and Docker Compose
- **CI/CD:** GitHub Actions
- **Deployment:** Render
- **Version Control:** Git and GitHub

## Project Repository

**GitHub:** https://github.com/ruchadange1/Sanjivani-sj-14-rationsahayak

**Live Application:** https://rationsahayak-ui.onrender.com

---

**Project:** RationSahayak – AI-Powered Ration Assistance System for Maharashtra