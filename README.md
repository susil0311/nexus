# 🏗️ NEXUS PM

<div align="center">

**Neural Execution eXtraction & Unified Scheduling Platform for Project Management**

> *From site voice to schedule truth — in under 15 minutes.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?logo=next.js)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Gemini](https://img.shields.io/badge/Gemini-1.5_Flash-4285F4?logo=google)](https://ai.google.dev)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com)

**SIH 2026 · PS No. SIH26122 · Oil India Limited · Smart Automation**

[Live Demo](#) · [API Docs](http://localhost:8000/docs) · [Blueprint](docs/blueprint.md)

</div>

---

## 🎬 Demo

> Drop a 3-page daily progress report → AI extracts 12 activities in 8 seconds → 11 auto-matched to Primavera nodes → 1 flagged for planner review → Schedule updated. All in under 15 minutes.

**Demo credentials:**
| Email | Password | Role |
|---|---|---|
| `supervisor1@demo.com` | `demo123` | Site Supervisor (Piping) |
| `planner1@demo.com` | `demo123` | Planning Engineer |
| `pm1@demo.com` | `demo123` | Project Manager |

---

## 🔴 The Problem

Infrastructure projects (oil & gas, EPC) have a fundamental data gap:
- **Planned schedules** live in Primavera P6 or MS Project (L1–L6 WBS)
- **Actual field progress** flows back through DPRs, Excel sheets, voice messages — each disconnected from plan activity IDs

The result:
- 🕐 **2–14 day reporting lag** — decisions made on stale data
- 🗑️ **Silent activity dropping** — unmatched updates lost forever
- 🧠 **Knowledge erosion** — project lessons never captured for future use

---

## ✅ Our Solution

NEXUS PM is an AI-powered **Planning-to-Execution Bridge** that:

1. **Ingests** daily reports, Excel sheets, and voice in any format — no rigid forms
2. **Extracts** structured activity events using Gemini 1.5 Flash LLM
3. **Matches** them semantically to L5/L6 Primavera nodes (MiniLM embeddings + FAISS)
4. **Updates** the schedule with confidence scores and an immutable audit trail
5. **Predicts** delays 2–4 weeks in advance using XGBoost ML
6. **Remembers** everything in an institutional memory (RAG) for future projects

---

## 🚀 Key Features

| Feature | Description |
|---|---|
| 🎙️ **TIME Agent** | Voice/chat interface — speak naturally to log activity progress |
| 🧲 **Semantic Linker** | `"spool erected on north flange"` → `Erect Line 24"-XX` (94% confidence) |
| 📄 **PolyGlot Ingestion** | PDF, Excel, CSV, plain text DPRs — all handled automatically |
| 🔮 **Delay Oracle** | ML-powered 2-4 week early warning on critical path slippage |
| 🧠 **Institutional Memory** | RAG over past projects: *"What's typical piping duration in monsoon?"* |
| 🚨 **Anomaly Sentinel** | Flags suspicious reports (100% progress with 0 manhours, etc.) |
| 📊 **Command Center** | Real-time SPI/CPI gauges + live submission feed |
| 🗺️ **GIS Map** | Activity heatmap by discipline zone |
| ✅ **Planner Review Queue** | Human-in-loop for low-confidence matches |
| 🔒 **Audit Trail** | Immutable SHA-256 hashed log of every update |

---

## 🤖 AI Features

| AI Feature | Model | Input | Output |
|---|---|---|---|
| NLP Activity Extraction | Gemini 1.5 Flash | Free text / PDF | Structured JSON events |
| Semantic Activity Matching | all-MiniLM-L6-v2 + FAISS | Field description | L5/L6 plan node + confidence |
| Delay Forecasting | XGBoost + ARIMA | SPI/CPI trends | Predicted finish + narrative |
| Institutional Memory RAG | ChromaDB + Gemini | Natural language question | Historical benchmarks |
| Anomaly Detection | Isolation Forest + Rules | Activity update | Anomaly flags |
| Voice Transcription | Whisper (local) | Audio | Text transcript |

---

## 🏗️ Architecture

```
Field Users (Supervisor / Planner / PM)
         ↓
Next.js 14 PWA (dark-mode SaaS UI)
         ↓ HTTPS
Nginx API Gateway (rate limiting, CORS)
         ↓
FastAPI Backend ────────→ Celery Workers (async AI tasks)
    ↓              ↓
PostgreSQL       Redis
(transactional)  (cache + queue)
         ↓
AI Service (FastAPI)
    ├── Gemini 1.5 Flash (NLP extraction, RAG synthesis)
    ├── all-MiniLM-L6-v2 (sentence embeddings)
    ├── ChromaDB (vector store: schedule nodes + memory)
    ├── XGBoost (delay forecasting)
    └── Isolation Forest (anomaly detection)
         ↓
MinIO (file storage) + Leaflet/OSM (GIS)
```

---

## 💻 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, TailwindCSS, ShadcnUI, ECharts, Leaflet |
| Backend | FastAPI, Python 3.11, SQLAlchemy, Alembic, Celery |
| Database | PostgreSQL 15, Redis 7 |
| AI/ML | Gemini 1.5 Flash, all-MiniLM-L6-v2, ChromaDB, XGBoost, Whisper |
| Storage | MinIO (S3-compatible) |
| DevOps | Docker, Docker Compose, GitHub Actions |
| Monitoring | Sentry, Prometheus + Grafana (production) |

---

## 🛠️ Installation

### Prerequisites
- [Docker Desktop](https://docker.com/products/docker-desktop) (includes Docker Compose)
- [Node.js 20+](https://nodejs.org)
- [Python 3.11+](https://python.org)
- [Gemini API Key](https://aistudio.google.com) (free)

### Quick Start (Docker — Recommended)

```bash
# 1. Clone
git clone https://github.com/yourteam/nexus-pm.git
cd nexus-pm

# 2. Configure
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 3. Run everything
docker compose up -d

# 4. Seed demo data
docker compose exec backend python scripts/seed_demo_data.py

# 5. Open
open http://localhost:3000
```

### Local Development (without Docker)

```bash
python scripts/setup_dev.py
```

This installs all dependencies, runs migrations, and seeds demo data.

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and configure:

```env
GEMINI_API_KEY=your_key_from_aistudio.google.com  # Required
JWT_SECRET=your_random_secret_key                  # Required
MOCK_AI_MODE=false                                  # Set true for offline demo
```

All other variables have sensible defaults for local development.

---

## 🔌 API Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Key endpoints:
```
POST /api/auth/login          — JWT authentication
POST /api/ingest/text         — Ingest free-text DPR
POST /api/ingest/file         — Ingest PDF/Excel file
POST /api/ingest/voice        — Ingest voice recording
GET  /api/matches/review-queue — Planner review queue
GET  /api/ai/forecast/{id}    — Delay Oracle forecast
POST /api/ai/query-memory     — RAG institutional memory
GET  /api/analytics/{id}/dashboard — SPI/CPI dashboard
```

---

## 🗄️ Database

Full schema: [`database/schema.sql`](database/schema.sql)

Key tables: `projects`, `schedule_nodes` (WBS), `field_submissions`, `extracted_events`, `activity_matches`, `actual_progress`, `institutional_memory`, `audit_trail`

Run migrations:
```bash
cd backend && alembic upgrade head
```

---

## 🚀 Deployment

### Free Tier Deployment
```
Frontend → Vercel (free)
Backend  → Railway.app (free $5 credit)
Database → Supabase PostgreSQL (free 500MB)
AI Model → Gemini 1.5 Flash API (free 15 RPM)
Vectors  → ChromaDB on Railway volume (free)
```

### Production
See [`docs/deployment.md`](docs/deployment.md) for AWS ECS/Fargate production architecture.

---

## 🧪 Testing

```bash
# Backend tests
cd backend && pytest tests/ -v

# Frontend tests  
cd frontend && npm run test

# AI pipeline test (3 input formats)
cd ai-service && python -m pytest tests/

# Full E2E
cd tests/e2e && npx playwright test
```

---

## 🗺️ Future Roadmap

- [ ] Native Primavera P6 REST API live sync
- [ ] iOS/Android native apps (React Native)
- [ ] Multi-tenant enterprise deployment
- [ ] Handwritten site diary OCR (PaddleOCR)
- [ ] BIM integration (IFC format)
- [ ] ONGC / HPCL / L&T expansion
- [ ] Offline-first with full sync (IndexedDB + service worker)
- [ ] Real-time WebSocket push for schedule updates

---

## 👥 Team

| Name | Role |
|---|---|
| [Your Name] | Full-Stack + AI Architect |
| [Team Member 2] | Backend + DevOps |
| [Team Member 3] | AI/ML Engineer |
| [Team Member 4] | Frontend + UI/UX |
| [Team Member 5] | Integration + Demo |

---

## 📄 License

[MIT License](LICENSE) — Built for SIH 2026

---

<div align="center">

*"Every project we run makes the next one smarter."*

**NEXUS PM — SIH26122 · Oil India Limited**

</div>
#   n e x u s  
 