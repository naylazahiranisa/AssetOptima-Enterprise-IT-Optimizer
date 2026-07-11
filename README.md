<div align="center">

# AssetOptima

**Enterprise IT Asset & License Optimizer with AI**

Full-stack platform for IT asset management, software license optimization, and AI-powered analytics.

![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi)
![Flutter](https://img.shields.io/badge/Flutter-3.44-02569B?logo=flutter)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?logo=postgresql)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)

</div>

---

## Architecture

```
┌──────────────────────┐
│   Next.js Web UI     │   frontend/        → http://localhost:3000
│   Flutter Mobile App │   assetoptima_field/ → http://localhost:8081
└──────────┬───────────┘
           │ REST + JWT
┌──────────▼───────────┐
│   FastAPI Backend    │   backend/         → http://localhost:8000
│   PostgreSQL         │   port 5432
│   ChromaDB           │   ./chroma_data/
└──────────┬───────────┘
           │
     ┌─────┴─────┬──────────────┐
     │           │              │
  ┌──▼──┐   ┌───▼────┐   ┌────▼─────┐
  │ Auth│   │ CRUD   │   │ AI / RAG │
  │ JWT │   │ 20+ API│   │ ChatBot  │
  │ RBAC│   │ Routes │   │ Predict  │
  └─────┘   └────────┘   │ Anomaly  │
                         └──────────┘
```

## Tech Stack

| Layer | Technology | Description |
|-------|-----------|-------------|
| **Frontend** | Next.js 16, React 19, Tailwind CSS 4 | Web command center dashboard |
| **Backend** | FastAPI, SQLAlchemy, Alembic | REST API with JWT auth & RBAC |
| **Database** | PostgreSQL 17 | Asset & license data storage |
| **AI / RAG** | ChromaDB, Sentence-Transformers | Local vector search, chatbot, anomaly detection |
| **Mobile** | Flutter 3.44, Riverpod, GoRouter | Field app for IT support (QR scan, asset lookup) |

## Project Structure

```
AssetOptima/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── main.py             # App entry point
│   │   ├── config/             # Settings & env vars
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── api/                # API route handlers
│   │   ├── services/           # Business logic
│   │   ├── ai/                 # AI platform (RAG, chatbot, anomaly, prediction)
│   │   └── auth/               # JWT authentication & RBAC
│   ├── scripts/                # Data import scripts
│   ├── tests/                  # Test suite
│   └── .env                    # Environment config (gitignored)
│
├── frontend/                   # Next.js web dashboard
│   ├── src/
│   │   ├── app/                # App router pages
│   │   ├── components/         # UI components
│   │   ├── features/           # Feature modules (assets, AI, etc.)
│   │   └── services/           # API client
│   └── package.json
│
├── assetoptima_field/          # Flutter mobile app
│   ├── lib/
│   │   ├── core/               # Config, theme, router, network
│   │   └── features/           # Auth, dashboard, assets, QR scanner, settings
│   └── pubspec.yaml
│
├── database/
│   └── schema/                 # SQL schema files
│
└── datasets/                   # CSV data for seeding
    ├── raw/                    # Raw CSV files
    └── processed/              # Processed CSV files
```

## Prerequisites

- **Python 3.12+**
- **Node.js 20+**
- **PostgreSQL 17+** (running on port `5432`)
- **Flutter 3.44+** (for mobile app, optional)

## Setup

### 1. Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env          # Windows
# cp .env.example .env          # macOS/Linux
# Edit .env — set POSTGRES_PASSWORD, SECRET_KEY, etc.

# Create database & import schema
psql -U postgres -c "CREATE DATABASE assetoptima;"
psql -U postgres -d assetoptima -f ../database/schema/schema.sql

# Import CSV datasets (optional)
python scripts/import_datasets.py

# Start the server
uvicorn app.main:app --reload --port 8000
```

Backend runs at **http://localhost:8000**. API docs at **http://localhost:8000/docs**.

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs at **http://localhost:3000**.

### 3. Mobile App (Optional)

```bash
cd assetoptima_field

# Get dependencies
flutter pub get

# Run on Chrome (web)
flutter run -d chrome --web-port=8081

# Run on Android emulator
flutter run

# Run on physical device
flutter run
```

> **Note:** Mobile app connects to `http://localhost:8000` by default. When running on Android emulator, the backend URL is automatically set to `http://10.0.2.2:8000`.

## Default Credentials

| Email | Password | Role |
|-------|----------|------|
| `admin@assetoptima.com` | `Admin@12345` | Super Admin |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `change-me-to-a-random-secret-key` | JWT signing key |
| `POSTGRES_HOST` | `localhost` | Database host |
| `POSTGRES_PORT` | `5432` | Database port |
| `POSTGRES_DB` | `assetoptima` | Database name |
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | `postgres` | Database password |
| `OPENAI_API_KEY` | _(empty)_ | Optional — enables OpenAI-powered chat |
| `CHROMA_PERSIST_DIR` | `./chroma_data` | ChromaDB storage path |
| `RAG_EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Embedding model (runs locally) |

## Features

### Dashboard
- Real-time asset overview (total, assigned, available, maintenance)
- KPI charts & analytics
- Quick action buttons

### Asset Management
- Full CRUD for IT assets (laptops, monitors, peripherals, etc.)
- Asset assignment & return tracking
- QR code scanning for quick lookup
- Search with filters (status, category, department)

### AI Assistant (RAG-Powered)
- Chat with your IT asset data in natural language
- Document upload & knowledge base (PDF, DOCX, TXT, CSV)
- Local embeddings via Sentence-Transformers (no API key needed)
- Optional OpenAI integration for enhanced responses

### Anomaly Detection
- License wastage detection (unused software seats)
- Dormant account identification
- Cost savings recommendations

### Predictive Analytics
- License demand forecasting
- Renewal predictions
- Utilization rate analysis

## Testing

```bash
cd backend
pytest -v -x
```

## License

This project was built as a university assignment (UAS - Universitas).
