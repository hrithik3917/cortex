# Cortex

A production-grade backend service with AI capabilities, built incrementally 
across a 12-week learning roadmap.

## Current Stage
Month 1 — SDE Core: FastAPI + PostgreSQL + Authentication + redis

## Tech Stack
- FastAPI
- PostgreSQL + SQLAlchemy
- JWT Authentication
- Redis
- Docker (coming Week 4)

## Run Locally
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```