# AI-SOC Platform

An AI-Powered Cybersecurity Operations Platform for educational purposes.

## Overview
This platform uses synthetic security logs, detects suspicious activity, correlates alerts into incidents, uses AI/RAG to investigate incidents, and displays findings in a web dashboard.

## Services
- `apps/web`: Next.js Frontend
- `apps/api`: FastAPI Backend
- `services/ingestion`: Log ingestion
- `services/detection`: Threat detection
- `services/correlation`: Alert correlation
- `services/ai-investigator`: AI/RAG investigator

## Setup
1. Copy `.env.example` to `.env`
2. Run `docker-compose up -d` to start the database
3. Run the backend and frontend (see DEVELOPMENT_PLAN.md)
