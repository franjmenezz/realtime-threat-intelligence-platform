# 🛡️ Threat Intelligence Pipeline

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python&logoColor=white)
![PySpark](https://img.shields.io/badge/PySpark-3.5-orange?style=for-the-badge&logo=apachespark&logoColor=white)
![Apache Kafka](https://img.shields.io/badge/Apache_Kafka-3.7-black?style=for-the-badge&logo=apachekafka&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=nextdotjs&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)

**Real-time Threat Intelligence platform built on Apache Spark Structured Streaming.**  
Ingests IoC feeds from multiple OSINT sources, enriches them automatically, scores them with ML and exposes a full-stack dashboard for SOC analysts.

[Architecture](#architecture) · [Quick Start](#quick-start) · [API Docs](#api-reference) · [Roadmap](#roadmap)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**Threat Intelligence Pipeline** is an end-to-end Big Data platform designed to mirror the workflows used in real Security Operations Centers (SOCs). The system continuously ingests **Indicators of Compromise (IoCs)** — malicious IPs, domains, file hashes and URLs — from public OSINT feeds, enriches each one with contextual metadata, assigns a **risk score** using a trained ML model, and surfaces actionable alerts through a modern web dashboard.

This project demonstrates production-grade engineering across the full data lifecycle:

> Ingestion → Streaming → Enrichment → ML Scoring → Storage → Visualization

---

## Features

### 🔄 Real-time Streaming
- Ingests IoC feeds via **Apache Kafka** topics
- Processes streams with **PySpark Structured Streaming**
- Sub-second latency from source to dashboard

### 🧠 ML-powered Risk Scoring
- Trained classifier using **PySpark MLlib** (Random Forest)
- Features: reputation score, geolocation, ASN, port exposure, historical frequency
- Risk levels: `CRITICAL` · `HIGH` · `MEDIUM` · `LOW` · `INFO`

### 🌐 OSINT Feed Integration
- **AbuseIPDB** — IP reputation database
- **VirusTotal** — File hash and URL analysis
- **AlienVault OTX** — Community threat feeds
- **Mock feeds** included for development without API keys

### 📊 Professional Dashboard
- Next.js 14 with App Router
- Real-time updates via Server-Sent Events (SSE)
- Dark mode by default
- JWT authentication
- Interactive charts, IoC tables, alert timeline

### 🐳 Fully Containerized
- Single `docker-compose up` to run the full stack
- Services: Kafka, Zookeeper, Spark, PostgreSQL, FastAPI, Next.js
- Health checks and automatic restarts

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES (OSINT)                        │
│   AbuseIPDB API    VirusTotal API    AlienVault OTX    Mock Feeds   │
└────────────┬───────────────┬──────────────┬──────────────┬──────────┘
             │               │              │              │
             └───────────────┴──────────────┴──────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          INGESTION LAYER                            │
│              Python producers → Apache Kafka Topics                 │
│         [iocs.raw]  [iocs.enriched]  [alerts.critical]             │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PROCESSING LAYER (PySpark)                      │
│                                                                     │
│   Kafka Source → Structured Streaming → Enrichment UDFs             │
│                                      → ML Scoring (MLlib)           │
│                                      → Deduplication                │
│                                      → Alert Rules Engine           │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         STORAGE LAYER                               │
│          PostgreSQL (hot)          Delta Lake / Parquet (cold)      │
│          IoCs · Alerts · Stats     Historical archive               │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           API LAYER                                 │
│                    FastAPI (REST + SSE)                             │
│         /iocs   /alerts   /stats   /stream   /auth                 │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js 14)                        │
│     Dashboard · IoC Explorer · Alert Timeline · Settings · Auth    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Streaming** | Apache Kafka 3.7 | Message broker for IoC events |
| **Processing** | PySpark 3.5 (Structured Streaming) | Distributed real-time data processing |
| **ML** | PySpark MLlib | Risk scoring model |
| **API** | FastAPI + Uvicorn | REST API + SSE for live updates |
| **Database** | PostgreSQL 16 | Hot storage for IoCs and alerts |
| **Frontend** | Next.js 14 (App Router) | Full-stack dashboard |
| **Auth** | JWT + NextAuth.js | Authentication layer |
| **Charts** | Recharts | Data visualization |
| **Infra** | Docker Compose | Container orchestration |
| **CI/CD** | GitHub Actions | Automated testing and linting |

---

## Project Structure

```
threat-intel-pipeline/
│
├── 📁 backend/
│   ├── 📁 ingestion/          # Kafka producers & OSINT connectors
│   │   ├── 📁 sources/        # API clients (AbuseIPDB, VT, OTX)
│   │   ├── 📁 mocks/          # Mock data generators for development
│   │   └── producer.py        # Main Kafka producer entry point
│   │
│   ├── 📁 processing/         # PySpark Streaming jobs
│   │   ├── spark_session.py   # Spark session factory
│   │   ├── stream_processor.py # Main streaming pipeline
│   │   └── schemas.py         # Spark DataFrame schemas
│   │
│   ├── 📁 enrichment/         # IoC enrichment UDFs
│   │   ├── geo_enricher.py    # Geolocation lookup
│   │   ├── asn_enricher.py    # ASN / ISP resolution
│   │   └── reputation.py      # Reputation score aggregation
│   │
│   ├── 📁 scoring/            # ML risk scoring
│   │   ├── train_model.py     # Model training script
│   │   ├── scorer.py          # Inference pipeline
│   │   └── features.py        # Feature engineering
│   │
│   ├── 📁 api/                # FastAPI application
│   │   ├── main.py            # App entry point
│   │   ├── routes/            # Route handlers
│   │   └── models/            # Pydantic models
│   │
│   ├── 📁 config/             # Configuration management
│   │   └── settings.py        # Pydantic Settings
│   │
│   └── 📁 tests/              # Pytest test suite
│
├── 📁 frontend/               # Next.js 14 dashboard
│   └── src/
│       ├── 📁 app/            # App Router pages
│       ├── 📁 components/     # UI components
│       ├── 📁 hooks/          # Custom React hooks
│       ├── 📁 lib/            # API client, utilities
│       └── 📁 types/          # TypeScript types
│
├── 📁 docker/                 # Dockerfiles per service
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
│
├── 📁 docs/                   # Extended documentation
│   ├── SETUP.md
│   ├── API.md
│   └── ARCHITECTURE.md
│
├── 📁 .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI pipeline
│
├── docker-compose.yml         # Full stack orchestration
├── docker-compose.dev.yml     # Development overrides
├── .env.example               # Environment variables template
└── README.md
```

---

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows 11 ✅)
- [Git](https://git-scm.com/)
- 8 GB RAM minimum (Spark + Kafka)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/threat-intel-pipeline.git
cd threat-intel-pipeline
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your settings (API keys optional — mocks work by default)
```

### 3. Launch the full stack

```bash
docker-compose up -d
```

This starts:
- Zookeeper + Kafka (message broker)
- PySpark processing job (streaming)
- PostgreSQL (database)
- FastAPI backend (port 8000)
- Next.js dashboard (port 3000)

### 4. Open the dashboard

```
http://localhost:3000
```

Default credentials:
```
Email:    admin@threatintel.local
Password: changeme
```

### 5. Start the IoC mock feed (development)

```bash
docker-compose exec backend python -m ingestion.mocks.feed_generator
```

---

## Configuration

Copy `.env.example` to `.env` and configure:

```env
# ── Kafka ───────────────────────────────────────
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_TOPIC_RAW=iocs.raw
KAFKA_TOPIC_ENRICHED=iocs.enriched
KAFKA_TOPIC_ALERTS=alerts.critical

# ── PostgreSQL ──────────────────────────────────
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=threatintel
POSTGRES_USER=threatintel
POSTGRES_PASSWORD=changeme_in_production

# ── OSINT API Keys (optional) ───────────────────
ABUSEIPDB_API_KEY=your_key_here
VIRUSTOTAL_API_KEY=your_key_here
OTX_API_KEY=your_key_here

# ── Auth ────────────────────────────────────────
JWT_SECRET=your_super_secret_jwt_key
NEXTAUTH_SECRET=your_nextauth_secret
NEXTAUTH_URL=http://localhost:3000

# ── Spark ────────────────────────────────────────
SPARK_MASTER=local[*]
SPARK_APP_NAME=ThreatIntelPipeline
```

> **API Keys**: All external sources fall back to realistic mock data when keys are not provided. The system is fully functional without them.

---

## API Reference

Full API documentation available at `http://localhost:8000/docs` (Swagger UI).

### Key endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/iocs` | List IoCs with filters and pagination |
| `GET` | `/api/v1/iocs/{id}` | Get single IoC detail |
| `GET` | `/api/v1/alerts` | List active alerts |
| `GET` | `/api/v1/stats/summary` | Dashboard summary metrics |
| `GET` | `/api/v1/stream` | SSE endpoint for real-time updates |
| `POST` | `/api/v1/auth/login` | JWT authentication |
| `POST` | `/api/v1/iocs/search` | Advanced IoC search |

---

## Roadmap

- [x] Project scaffold and architecture
- [x] Docker Compose full stack
- [x] Mock IoC feed generator
- [ ] PySpark Structured Streaming pipeline
- [ ] ML risk scoring model (MLlib)
- [ ] FastAPI REST + SSE
- [ ] Next.js dashboard (dark mode, auth)
- [ ] AbuseIPDB integration
- [ ] VirusTotal integration
- [ ] AlienVault OTX integration
- [ ] GitHub Actions CI pipeline
- [ ] Unit and integration tests

---

## Contributing

Contributions are welcome. Please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/new-enricher`)
3. Commit your changes (`git commit -m 'feat: add ASN enricher'`)
4. Push to the branch (`git push origin feature/new-enricher`)
5. Open a Pull Request

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">
Built with ☕ and a healthy paranoia about network traffic.
</div>
