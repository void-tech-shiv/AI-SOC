# Architecture

## High Level Architecture
- **Frontend**: Next.js app (React, TailwindCSS, TypeScript)
- **Backend API**: FastAPI (Python) serving REST endpoints
- **Database**: PostgreSQL (with pgvector for RAG in the future)
- **Microservices** (planned):
  - Ingestion Service
  - Detection Service
  - Correlation Service
  - AI Investigator Service

## Data Flow
1. Synthetic logs are generated and ingested.
2. Detection service analyzes logs for suspicious activity and creates alerts.
3. Correlation service groups alerts into incidents.
4. AI investigator provides RAG-based analysis on incidents.
5. Frontend fetches and displays the data via the Backend API.
