# 🛡️ Realtime Threat Intelligence Platform

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PySpark](https://img.shields.io/badge/PySpark-3.5-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)
![Kafka](https://img.shields.io/badge/Apache_Kafka-3.7-231F20?style=for-the-badge&logo=apachekafka&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**A production-grade, real-time Threat Intelligence platform built on Apache Spark Structured Streaming.**

Ingests IoC feeds from multiple OSINT sources, enriches them with geolocation and reputation data, scores them with a weighted ML model, and exposes a full-stack SOC analyst dashboard with live event streaming.

[Features](#-features) · [Architecture](#-architecture) · [Tech Stack](#-tech-stack) · [Quick Start](#-quick-start) · [API Docs](#-api-reference) · [Roadmap](#-roadmap)

</div>

---

## 📌 Overview

This project mirrors the real workflows used inside Security Operations Centers (SOCs). The system continuously ingests **Indicators of Compromise (IoCs)** — malicious IPs, domains, file hashes and URLs — from public OSINT feeds, enriches each one with contextual metadata, assigns a **risk score** using ML, and surfaces actionable alerts through a modern dark-mode dashboard.

The entire data lifecycle is covered end-to-end:

```
Ingestion → Kafka → PySpark Streaming → Enrichment → ML Scoring → PostgreSQL → FastAPI → Next.js
```

> Built to demonstrate production-grade Big Data engineering combined with cybersecurity domain expertise.

---

## ✨ Features

### 🔄 Real-time Streaming Pipeline
- Multi-source IoC ingestion via **Apache Kafka** topics
- Sub-second processing with **PySpark Structured Streaming**
- Micro-batch architecture with 5-second trigger intervals
- Automatic checkpoint and fault recovery

### 🌍 OSINT Feed Integration
| Source | Type | Free Tier |
|--------|------|-----------|
| **AbuseIPDB** | IP reputation | 1,000 queries/day |
| **VirusTotal** | Hash & URL analysis | 500 queries/day |
| **AlienVault OTX** | Community feeds | Unlimited |
| **Mock Feed** | Development data | Always available |

### 🧠 ML-powered Risk Scoring
- Weighted scoring engine (0–100) using enrichment signals
- Features: AbuseIPDB score, VirusTotal detection ratio, Tor/VPN flags, source confidence
- Risk levels: `CRITICAL` · `HIGH` · `MEDIUM` · `LOW` · `INFO`
- Extensible to a trained PySpark MLlib Random Forest model

### 📊 Professional SOC Dashboard
- **Next.js 14** with App Router and dark mode
- Real-time IoC feed via **Server-Sent Events (SSE)**
- Interactive charts: area timeline, donut by type, bar by country
- IoC Explorer with filtering, search and pagination
- Alert management with severity filters
- JWT authentication

### 🐳 One-Command Deployment
- Full stack via `docker-compose up -d`
- Services: Kafka, Zookeeper, Spark, PostgreSQL, FastAPI, Next.js
- Health checks, auto-restart and graceful shutdown

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        OSINT DATA SOURCES                            │
│   AbuseIPDB    VirusTotal    AlienVault OTX    Mock Feed Generator   │
└───────────────────────────────┬──────────────────────────────────────┘
                                │ Python Kafka Producers
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         APACHE KAFKA                                 │
│         [iocs.raw]      [iocs.enriched]      [alerts.critical]       │
└───────────────────────────────┬──────────────────────────────────────┘
                                │ Structured Streaming
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    PYSPARK PROCESSING LAYER                          │
│   Kafka Source → Deserialization → Enrichment UDFs                   │
│                                 → ML Risk Scoring                    │
│                                 → Alert Rules Engine                 │
│                                 → foreachBatch → PostgreSQL          │
└───────────────────────────────┬──────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│   PostgreSQL 16 (hot storage)       Parquet (cold archive)           │
└───────────────────────────────┬──────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│              FASTAPI — REST + SSE — Swagger at /docs                 │
└───────────────────────────────┬──────────────────────────────────────┘
                                ▼
┌──────────────────────────────────────────────────────────────────────┐
│         NEXT.JS 14 — Dashboard · IoC Explorer · Alerts · Settings   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Stream Broker** | Apache Kafka | 3.7 | IoC event message queue |
| **Stream Processing** | PySpark Structured Streaming | 3.5 | Distributed real-time processing |
| **ML Engine** | PySpark MLlib | 3.5 | Risk scoring model |
| **API** | FastAPI + Uvicorn | 0.111 | REST endpoints + SSE live feed |
| **Database** | PostgreSQL | 16 | IoC and alert storage |
| **Frontend** | Next.js App Router | 14 | SOC analyst dashboard |
| **Charts** | Recharts | 2.12 | Data visualization |
| **Infra** | Docker Compose | — | Full stack orchestration |
| **CI/CD** | GitHub Actions | — | Automated tests and linting |

---

## 🚀 Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — 8 GB RAM minimum
- [Git](https://git-scm.com/)

### 1. Clone and configure

```bash
git clone https://github.com/YOUR_USERNAME/realtime-threat-intelligence-platform.git
cd realtime-threat-intelligence-platform
cp .env.example .env
```

### 2. Launch the full stack

```bash
docker-compose up -d
```

First run takes ~5 minutes to download all images. Subsequent starts take ~30 seconds.

### 3. Start the mock IoC feed

```bash
docker-compose --profile dev up -d mock-feed
```

### 4. Open the dashboard

| Service | URL | Credentials |
|---------|-----|-------------|
| **Dashboard** | http://localhost:3000 | admin@threatintel.local / changeme |
| **API Swagger** | http://localhost:8000/docs | — |
| **Health check** | http://localhost:8000/health | — |

---

## ⚙️ Configuration

All fields have working defaults. **API keys are optional** — the system uses realistic mock data without them.

```env
# OSINT API Keys (optional)
ABUSEIPDB_API_KEY=     # abuseipdb.com — free, 1000 req/day
VIRUSTOTAL_API_KEY=    # virustotal.com — free, 500 req/day
OTX_API_KEY=           # otx.alienvault.com — free, unlimited

# Auth
JWT_SECRET=change_this_to_a_strong_random_secret

# Mock feed
MOCK_FEED_INTERVAL_SECONDS=3
MOCK_FEED_BATCH_SIZE=5
```

---

## 📡 API Reference

Full interactive documentation at `http://localhost:8000/docs`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/login` | JWT authentication |
| `GET` | `/api/v1/iocs` | List IoCs with filters and pagination |
| `GET` | `/api/v1/iocs/{id}` | Single IoC detail |
| `POST` | `/api/v1/iocs/search` | Full-text IoC search |
| `GET` | `/api/v1/alerts` | Active alert list |
| `GET` | `/api/v1/stats/summary` | Dashboard metrics |
| `GET` | `/api/v1/stats/timeline` | 24h ingestion timeline |
| `GET` | `/api/v1/stats/by-country` | IoC volume by country |
| `GET` | `/api/v1/stream/iocs` | SSE real-time IoC feed |

---

## 🗺️ Roadmap

- [x] Full Docker Compose stack (6 services)
- [x] PySpark Structured Streaming pipeline
- [x] Kafka producer with mock IoC feed
- [x] Geo, ASN and reputation enrichment UDFs
- [x] Weighted ML risk scoring engine
- [x] FastAPI REST + SSE endpoints + Swagger
- [x] Next.js 14 dashboard — dark mode, charts, live feed
- [x] JWT authentication
- [x] GitHub Actions CI pipeline
- [ ] AbuseIPDB / VirusTotal / OTX live integration
- [ ] Trained PySpark MLlib Random Forest model
- [ ] Full unit and integration test suite
- [ ] Kubernetes deployment manifests

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.

---

<div align="center">

Built with ☕ and a healthy paranoia about network traffic.

</div>
