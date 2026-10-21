# Day 3 CI/CD: Build / Test / Deploy Pipeline

## Repository
`Study_Assistant_RAG` — AI-powered study assistant (FastAPI + React + MySQL + Pinecone)

## Pipeline Overview
GitHub Actions CI/CD for FastAPI + React application with RAG pipeline.

### Trigger
- Push/Pull Request to `main`
- Manual workflow dispatch

### Stages

#### 1. Lint & Format
- Backend: Ruff/Black (Python)
- Frontend: ESLint + Prettier (TypeScript/React)

#### 2. Typecheck
- Backend: `mypy` (Python strict mode)
- Frontend: `tsc --noEmit` (TypeScript)

#### 3. Test
- Backend: `pytest` (unit + integration)
- Backend: `python test_rag_pipeline.py` (RAG pipeline test)
- Backend: `python test_pinecone_data.py` (Pinecone data verification)
- Frontend: `npm test` (Vitest)
- Coverage: pytest-cov + frontend coverage

#### 4. Build
- Backend: `pip install -r requirements.txt`
- Backend: Docker image
- Frontend: `npm ci` + `npm run build` (Vite)
- Pinecone index migration: `python migrate_pinecone_index.py`

#### 5. Security Scan
- `pip audit` / `safety` (Python dependencies)
- `npm audit` (frontend dependencies)
- Secret detection (no `PINECONE_API_KEY`, no `GEMINI_API_KEY`, no `SECRET_KEY` committed)
- No `.env` files committed

#### 6. Deploy (on merge to `main`)
- Build and push Docker images
- Deploy with `docker-compose up -d` (MySQL + backend + frontend)
- Run database schema: `mysql -u root -p study_assistant < database_schema.sql`
- Initialize Pinecone index
- Health check: `GET /` (backend API)

### Quality Gates
- All tests pass (backend + frontend)
- RAG pipeline test passes
- Pinecone data verification passes
- TypeScript strict mode clean
- `mypy` clean
- No secrets committed (API keys must be in `.env`, not committed)

### Artifacts
- Docker images (backend + frontend)
- Test reports
- Coverage reports
- Pinecone index configuration
- Deployment URL

## Day 3 Outcome
CI/CD pipeline documented. No code changes. 0 PRs. Ready for Day 4 (project restructuring).
<!-- Feature branch commit for PR -->
