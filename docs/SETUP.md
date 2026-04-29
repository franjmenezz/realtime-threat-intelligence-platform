# Setup Guide — Windows 11

This guide walks you through running the full stack on Windows 11 with Docker Desktop.

## Prerequisites

### 1. Docker Desktop
Download and install [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/).

During installation, enable **WSL 2 backend** (recommended for better performance).

Minimum resources to allocate in Docker Desktop settings:
- **CPUs**: 4
- **Memory**: 8 GB (Kafka + Spark are memory-hungry)
- **Disk**: 20 GB

### 2. Git
Install [Git for Windows](https://git-scm.com/download/win).

---

## Quick Start

Open a terminal (PowerShell or Windows Terminal) and run:

```powershell
# Clone the project
git clone https://github.com/YOUR_USERNAME/threat-intel-pipeline.git
cd threat-intel-pipeline

# Create environment file
copy .env.example .env

# Launch everything
docker-compose up -d

# Watch logs
docker-compose logs -f
```

Wait approximately 60–90 seconds for all services to initialize.  
Open your browser at **http://localhost:3000**.

---

## Services and Ports

| Service        | Container       | Port  | Description                  |
|---------------|-----------------|-------|------------------------------|
| Next.js        | tip-frontend    | 3000  | Dashboard UI                 |
| FastAPI        | tip-backend     | 8000  | REST API + Swagger            |
| PostgreSQL     | tip-postgres    | 5432  | Database                     |
| Kafka          | tip-kafka       | 9092  | Message broker               |
| Zookeeper      | tip-zookeeper   | 2181  | Kafka coordinator            |

---

## Development Mode

To enable hot-reload for local development without Docker:

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Start only infra services
docker-compose up -d kafka postgres zookeeper

# Run FastAPI with hot reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### Mock IoC Feed

```powershell
cd backend
python -m ingestion.mocks.feed_generator
```

---

## Useful Commands

```powershell
# Stop all services
docker-compose down

# Stop and remove data volumes (full reset)
docker-compose down -v

# Restart a specific service
docker-compose restart backend

# View Spark processor logs
docker-compose logs -f spark-processor

# Access PostgreSQL
docker-compose exec postgres psql -U threatintel -d threatintel

# Start mock feed (dev profile)
docker-compose --profile dev up -d mock-feed
```

---

## API Keys (Optional)

The system runs fully with mock data. To connect real OSINT sources:

1. **AbuseIPDB** — Register free at https://www.abuseipdb.com/register (1,000 queries/day free)
2. **VirusTotal** — Register at https://www.virustotal.com/gui/sign-in (500 queries/day free)
3. **AlienVault OTX** — Register at https://otx.alienvault.com/ (unlimited)

Add keys to your `.env` file and restart the backend:
```powershell
docker-compose restart backend spark-processor
```

---

## Troubleshooting

### Kafka fails to start
Increase Docker Desktop memory to 8 GB minimum.

### Port already in use
```powershell
# Find what's using port 9092
netstat -ano | findstr :9092
```

### Spark OutOfMemoryError
Reduce Spark memory in `.env`:
```
SPARK_DRIVER_MEMORY=1g
SPARK_EXECUTOR_MEMORY=1g
```
