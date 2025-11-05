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

```
ayni_core/
├── backend/                 # Django project
│   ├── api/                # REST endpoints
│   ├── auth/              # Authentication
│   ├── companies/         # Company management
│   ├── analytics/         # Analytics logic
│   ├── processing/        # Data processing tasks
│   └── config/           # Django settings
├── frontend/               # React application
│   ├── src/
│   │   ├── components/   # UI components
│   │   ├── pages/       # Route pages
│   │   ├── services/    # API calls
│   │   ├── store/       # State management
│   │   └── utils/       # Helpers
│   └── public/
├── src/                    # Existing GabeDA engine
│   ├── core/              # Core functionality
│   ├── execution/         # Execution logic
│   ├── features/          # Feature engineering
│   └── export/           # Export utilities
├── database/              # Database scripts
│   ├── migrations/
│   └── seeds/
└── infrastructure/        # Deployment configs
    ├── docker/
    ├── kubernetes/
    └── terraform/
```

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

---

**Last Updated**: 2024-11-04
**Version**: 1.0
**Status**: Design Phase