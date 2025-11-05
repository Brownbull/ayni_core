# AYNI Core - PYMEs Analytics Platform Design

## Executive Summary
Building a comprehensive analytics platform for Chilean PYMEs that processes transactional data, generates rich features, and provides AI-powered insights through role-based dashboards. Think "WarcraftLogs for business metrics" - comparing performance against aggregated industry benchmarks with macroeconomic context as "buffs/debuffs".

## Vision Statement
"I envision Ayni being the tool that many pymes lack in Chile and South America. Being able to track your business during time is not easy, and tools doing this come not cheap. With over 10 years of experience in enterprise data processing at the inflexion point of massive data operations, I bring expertise from mainframe to cloud, from raw data to complex models. This platform democratizes that enterprise-level analytics for PYMEs, making data insights a superpower for business growth."

## Problem Statement
Chilean and South American PYMEs face critical challenges:
- **Accessibility Gap**: Existing analytics tools are either too basic or too expensive
- **Expertise Barrier**: Most solutions require data analysts or scientists
- **Cultural Fit**: Latin American users need compact, high-value, visual information
- **Risk Aversion**: Chilean market is highly risk-averse, needs trusted insights
- **Time Sensitivity**: Less patient than US/EU markets, need quick value
- **No Middle Ground**: Nothing between basic Excel and enterprise BI tools

## Solution Architecture

### Core Flow
```
CSV Upload → Async Processing → Feature Generation → Database Storage → Analytics/ML → Web UI
     ↓              ↓                    ↓                ↓               ↓          ↓
   Queue       Intermediate         Feature Store     PostgreSQL      RAG/LLM    React App
              CSVs (downloadable)                                               (role-based views)
```

### Tech Stack Decision
- **Backend**: Django (Railway) - Better for rapid development than Flask
- **Frontend**: React (Render) - Modern, component-based UI
- **Database**: PostgreSQL (Railway) / SQLite (local dev)
- **Queue**: Redis + Celery for async processing
- **Core**: Existing GabeDA feature engine (Python)
- **Environments**: Local, Staging (Railway), Production (Railway)

## System Components

### 1. Data Ingestion Layer
- **CSV Upload Interface**: Web form for PYMEs to upload transactional data
- **Async Processing Pipeline**: Celery tasks for heavy computation
- **Validation & Cleaning**: Data quality checks before processing

### 2. Feature Engineering Core (Existing GabeDA)
- **Feature Store**: Generate business metrics from raw transactions
- **Execution Orchestrator**: Coordinate feature calculations
- **Intermediate Outputs**: CSVs available for download during processing

### 3. Database Layer
- **Transactional Data**: Raw uploads from PYMEs
- **Feature Tables**: Computed metrics and KPIs
- **Benchmark Tables**: Aggregated industry metrics (10+ PYMEs for anonymity)
- **Macro Indicators**: Economic context data

### 4. Analytics & ML Layer
- **RAG Integration**: Connect feature data to retrieval system
- **LLM Integration**: Natural language queries on business data
- **Benchmark Engine**: Compare against industry averages
- **Macro Context**: Apply economic "buffs/debuffs" to metrics

### 5. Web Application Layer
- **Authentication**: User registration/login
- **Company Management**: Create/select company context
- **Role-Based Dashboards**:
  - Owner View: High-level KPIs, strategic metrics
  - Operations View: Efficiency, inventory, logistics
  - Marketing View: Customer metrics, campaigns
  - Finance View: Revenue, costs, margins
- **Process Monitor**: Track CSV processing status
- **Download Center**: Access intermediate datasets

## Key Features

### MVP Features (Phase 1)
1. User authentication & company management
2. CSV upload with async processing
3. Basic dashboard with key metrics
4. Download processed datasets
5. Database storage of results

### Growth Features (Phase 2)
1. Industry benchmarking (anonymized)
2. Macroeconomic context overlay
3. Role-based views
4. Basic AI queries on data

### Advanced Features (Phase 3)
1. Full RAG/LLM integration
2. Predictive analytics
3. Automated recommendations
4. API for external integrations

## Data Privacy & Security
- **Anonymization**: Minimum 10 PYMEs for any aggregate metric
- **Data Isolation**: Strict company-level data separation
- **Encryption**: At rest and in transit
- **Compliance**: Chilean data protection regulations

## Technical Decisions

### Why Django over Flask?
- Built-in ORM for complex database operations
- Admin interface for data management
- Better authentication system out-of-box
- Celery integration is more mature
- Faster development for full-stack features

### Why Separate Frontend/Backend Deployment?
- Independent scaling
- Better separation of concerns
- Modern React development workflow
- API-first architecture enables future mobile apps

### Database Design Philosophy
- **Temporal**: Keep historical data for trend analysis
- **Normalized**: Prevent data duplication
- **Indexed**: Optimize for common query patterns
- **Partitioned**: By company and time period for performance

## Implementation Strategy

### Phase 1: Foundation (Weeks 1-4)
- Setup Django project with authentication
- Create company/user models
- Build CSV upload + Celery processing
- Integrate existing GabeDA engine
- Setup PostgreSQL schema
- Basic React dashboard

### Phase 2: Core Features (Weeks 5-8)
- Role-based views implementation
- Process monitoring UI
- Database commit logic
- Download center
- Testing & error handling

### Phase 3: Analytics (Weeks 9-12)
- Benchmarking engine
- Macro indicators integration
- Basic AI query interface
- Performance optimization

## Success Metrics
- Upload to insight time < 5 minutes
- 99.9% uptime for web platform
- Support 1000+ concurrent PYMEs
- Query response time < 2 seconds
- User satisfaction > 4.5/5

## Risk Mitigation
- **Data Quality**: Extensive validation before processing
- **Scale**: Design for horizontal scaling from day 1
- **Complexity**: Incremental rollout, MVP first
- **Adoption**: User-friendly onboarding flow

## Next Steps
1. Setup Django project structure
2. Create database models
3. Build authentication system
4. Integrate GabeDA engine
5. Create React frontend scaffold
6. Setup CI/CD pipeline

---

**Created**: 2024-11-04
**Status**: Ready for implementation planning
**Complexity**: High but manageable with phased approach
**Priority**: Foundation first, then iterate