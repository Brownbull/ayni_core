# AYNI Core - System Architecture

## Overview
Multi-tier architecture for PYMEs analytics platform with separated frontend, backend, data processing, and infrastructure layers.

## System Layers

### 1. Presentation Layer (Frontend)
- **Technology**: React 18+ with TypeScript
- **Deployment**: Render.com
- **Components**:
  - Authentication UI (login/register/company selection)
  - Role-based dashboards (owner/operations/marketing/finance)
  - CSV upload interface
  - Process monitoring dashboard
  - Download center for processed files
  - Analytics visualizations (charts, KPIs)
  - AI query interface

### 2. Application Layer (Backend)
- **Technology**: Django 4.2+ with Django REST Framework
- **Deployment**: Railway
- **Components**:
  - REST API endpoints
  - Authentication & authorization (JWT)
  - Company management
  - File upload handling
  - Task queue management
  - WebSocket for real-time updates
  - Database ORM layer

### 3. Processing Layer (Data Pipeline)
- **Technology**: Python with Celery
- **Components**:
  - GabeDA Feature Engine (existing)
  - CSV validation & parsing
  - Feature calculation pipeline
  - Intermediate file generation
  - Database commit logic
  - Error handling & retry logic

### 4. Data Layer
- **Primary Database**: PostgreSQL (Railway)
- **Cache**: Redis (Railway)
- **File Storage**: Temporary local + S3 for persistence
- **Schema**:
  - Users & authentication
  - Companies & permissions
  - Raw transactional data
  - Computed features & metrics
  - Benchmark aggregations
  - Process tracking

### 5. Integration Layer
- **RAG System**: For document retrieval
- **LLM API**: OpenAI/Anthropic for queries
- **External APIs**: Macro economic indicators
- **Export APIs**: For third-party integrations

## Data Flow

```
1. User uploads CSV via React UI
2. Django receives file, validates, creates task
3. Celery worker picks up task
4. GabeDA processes data, generates features
5. Intermediate CSVs saved to storage
6. Results committed to PostgreSQL
7. WebSocket notifies frontend of completion
8. User views results in dashboard
```

## Directory Structure

### Multi-Repository Architecture
The AYNI platform uses a **three-repository** structure for clear separation of concerns:

```
C:\Projects\play\
├── ayni_core/              # Orchestration & shared resources
│   ├── .claude/           # AI orchestration framework
│   ├── ai-state/          # Task management, knowledge base
│   ├── src/               # Existing GabeDA engine
│   │   ├── core/         # Core functionality
│   │   ├── execution/    # Execution logic
│   │   ├── features/     # Feature engineering
│   │   └── export/       # Export utilities
│   └── orchestration.config.json
│
├── ayni_be/               # Backend repository (Django)
│   ├── apps/
│   │   ├── authentication/  # JWT auth
│   │   ├── companies/       # Company management
│   │   ├── analytics/       # Analytics API
│   │   ├── processing/      # CSV processing, Celery tasks
│   │   └── api/            # DRF endpoints
│   ├── config/             # Django settings
│   ├── requirements.txt
│   └── manage.py
│
└── ayni_fe/               # Frontend repository (React)
    ├── src/
    │   ├── components/    # Reusable UI components
    │   ├── pages/        # Route pages
    │   ├── services/     # API client
    │   ├── store/        # State management (Zustand/Redux)
    │   ├── hooks/        # Custom React hooks
    │   └── utils/        # Helpers
    ├── public/
    ├── package.json
    └── vite.config.ts
```

### Repository Responsibilities

**ayni_core**:
- Orchestration framework and AI task management
- GabeDA feature engine (shared by backend)
- Knowledge base and standards
- Cross-repo coordination

**ayni_be**:
- Django REST API
- Database models and migrations
- Celery task processing
- WebSocket server
- Imports GabeDA from ayni_core

**ayni_fe**:
- React UI components
- Client-side routing
- State management
- API integration
- Tailwind CSS styling

## Technology Decisions

### Backend: Django
- Mature ORM for complex queries
- Built-in admin interface
- Excellent PostgreSQL support
- Strong authentication system
- Good Celery integration

### Frontend: React
- Component reusability
- Rich ecosystem
- TypeScript support
- Modern state management
- Good chart libraries

### Database: PostgreSQL
- JSONB for flexible feature storage
- Excellent performance at scale
- Strong consistency guarantees
- Good analytical query support
- Railway managed service

### Queue: Celery + Redis
- Proven async processing
- Retry mechanisms
- Task monitoring
- Priority queues
- Result backend

## Security Architecture

### Authentication
- JWT tokens for API access
- Session-based for web UI
- MFA optional for enterprise

### Authorization
- Role-based access control (RBAC)
- Company-level isolation
- Feature flags for gradual rollout

### Data Security
- Encryption at rest (database)
- Encryption in transit (HTTPS)
- File encryption for uploads
- Audit logging

## Scalability Plan

### Horizontal Scaling
- Multiple Django instances behind load balancer
- Multiple Celery workers for processing
- Read replicas for PostgreSQL
- Redis cluster for caching

### Performance Optimization
- Database query optimization
- Caching strategy (Redis)
- CDN for static assets
- Lazy loading in frontend

## Monitoring & Observability

### Application Monitoring
- Sentry for error tracking
- New Relic for performance
- Custom metrics dashboard

### Infrastructure Monitoring
- Railway metrics
- Database monitoring
- Queue length tracking
- Storage usage alerts

## Development Workflow

### Environments
1. **Local**: Docker Compose setup
2. **Staging**: Railway preview environments
3. **Production**: Railway main environment

### CI/CD Pipeline
1. GitHub Actions for testing
2. Automated deployments to staging
3. Manual promotion to production
4. Database migrations automated

## API Design

### RESTful Endpoints
```
POST   /api/auth/register
POST   /api/auth/login
GET    /api/companies
POST   /api/uploads
GET    /api/uploads/{id}/status
GET    /api/analytics/dashboard
GET    /api/analytics/benchmarks
POST   /api/ai/query
```

### WebSocket Events
```
upload.started
upload.progress
upload.completed
upload.failed
analytics.updated
```

## Database Schema (Enhanced for Multiple Aggregation Levels)

### Core Tables

#### users
- id, email, password_hash, created_at, updated_at
- **Admin User**: admin@ayni.cl / gabe123123 (pre-configured)

#### companies
- id, name, rut, industry, size, created_at

#### user_companies
- user_id, company_id, role, permissions

#### uploads
- id, company_id, filename, status, created_at
- original_rows, processed_rows, updated_rows (tracking changes)
- column_mappings (JSONB) - user-defined column mappings

#### column_mappings
- id, company_id, mapping_name
- mappings (JSONB) - stores user's column name mappings
- formats (JSONB) - date/number formats per column
- defaults (JSONB) - default values for missing data

### Transactional & Feature Tables (Multiple Aggregation Levels)

#### raw_transactions
- id, company_id, upload_id, data (JSONB), processed_at
- Based on COLUMN_SCHEMA from src/core/constants.py

#### daily_aggregations
- company_id, date, metrics (JSONB)

#### weekly_aggregations
- company_id, week_start, metrics (JSONB)

#### monthly_aggregations
- company_id, month, year, metrics (JSONB)

#### quarterly_aggregations
- company_id, quarter, year, metrics (JSONB)

#### yearly_aggregations
- company_id, year, metrics (JSONB)

#### product_aggregations
- company_id, product_id, period, metrics (JSONB)

#### customer_aggregations
- company_id, customer_id, period, metrics (JSONB)

#### category_aggregations
- company_id, category, period, metrics (JSONB)

### Tracking & Audit Tables

#### data_updates
- id, company_id, upload_id, period
- rows_before, rows_after, rows_updated
- timestamp, user_id

#### benchmarks
- id, industry, metric, value, period, sample_size (min 10)

## Integration Points

### Inbound
- CSV file uploads
- API data ingestion
- Macro indicator feeds

### Outbound
- Export APIs
- Webhook notifications
- Report generation

## Development Coordination Strategy

### Multi-Repo Workflow
Since the platform spans three repositories, development follows this pattern:

1. **Planning & Orchestration** (ayni_core):
   - All task planning happens here via `/brainstorm` and `/write-plan`
   - Tasks are assigned to specific repositories
   - Track progress across all repos in `ai-state/active/tasks.yaml`

2. **Backend Development** (ayni_be):
   - Tasks tagged with `context: backend`
   - Work directory: `C:\Projects\play\ayni_be`
   - Imports GabeDA from `../ayni_core/src`
   - Tests run independently

3. **Frontend Development** (ayni_fe):
   - Tasks tagged with `context: frontend`
   - Work directory: `C:\Projects\play\ayni_fe`
   - Connects to backend via API
   - Tests run independently

### Cross-Repository Dependencies
- Backend imports GabeDA: `sys.path.append('../ayni_core')`
- Frontend API endpoint registry synced from backend
- Shared TypeScript types generated from Django models
- Docker Compose orchestrates all services locally

### Deployment Architecture
- **ayni_core**: Not deployed (development orchestration only)
- **ayni_be**: Railway (backend + workers + database)
- **ayni_fe**: Render.com (static site or SSR)

---

**Last Updated**: 2025-11-04
**Version**: 1.1
**Status**: Multi-repo architecture documented