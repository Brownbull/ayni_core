# AYNI Core - Architectural Decisions Record (ADR)

## ADR-001: Django over Flask for Backend
**Date**: 2024-11-04
**Status**: Accepted
**Context:** Need to choose between Flask (currently in requirements) and Django for backend framework.
**Decision:** Use Django instead of Flask.
**Rationale:**
- Built-in ORM perfect for complex business metrics
- Admin interface for data management
- Better authentication system out-of-box
- Mature Celery integration for async processing
- Faster development for full-featured application
**Consequences:**
- (+) Rapid development with batteries included
- (+) Strong ecosystem for enterprise features
- (-) Need to migrate from Flask dependencies
- (-) More opinionated structure

---

## ADR-002: Separate Frontend and Backend Deployment
**Date**: 2024-11-04
**Status**: Accepted
**Context:** Choosing between monolithic deployment vs separated services.
**Decision:** Deploy frontend (React) on Render and backend (Django) on Railway separately.
**Rationale:**
- Independent scaling based on load patterns
- Better separation of concerns
- Modern development workflow for frontend team
- API-first enables future mobile apps
**Consequences:**
- (+) Independent scaling and deployment
- (+) Better team autonomy
- (-) Need CORS configuration
- (-) Additional complexity in local development

---

## ADR-003: PostgreSQL with JSONB for Features
**Date**: 2024-11-04
**Status**: Accepted
**Context:** Need flexible storage for varied business metrics and features.
**Decision:** Use PostgreSQL with JSONB columns for feature storage.
**Rationale:**
- JSONB allows flexible schema for different PYMEs
- Strong consistency for financial data
- Excellent query performance with proper indexing
- Railway managed service reduces operational burden
**Consequences:**
- (+) Flexible schema evolution
- (+) Strong ACID guarantees
- (-) Need careful index strategy
- (-) Schema validation at application level

---

## ADR-004: Integrate Existing GabeDA Engine
**Date**: 2024-11-04
**Status**: Accepted
**Context:** Existing feature calculation engine (GabeDA) is already built and tested.
**Decision:** Integrate GabeDA as core processing engine rather than rebuilding.
**Rationale:**
- Significant investment already made
- Tested and working code
- Maintains business logic continuity
- Team familiar with codebase
**Consequences:**
- (+) Faster time to market
- (+) Proven calculation logic
- (-) Need wrapper/adapter for Django
- (-) Potential technical debt

---

## ADR-005: Industry Benchmarking with Privacy
**Date**: 2024-11-04
**Status**: Accepted
**Context:** PYMEs want to compare performance but privacy is critical.
**Decision:** Aggregate metrics only when 10+ PYMEs contribute data.
**Rationale:**
- Prevents identifying individual businesses
- Statistical significance for benchmarks
- Builds trust with users
- Complies with privacy regulations
**Consequences:**
- (+) Strong privacy guarantees
- (+) Trust building with users
- (-) Need critical mass before activation
- (-) Complex aggregation logic

---

## ADR-006: Celery + Redis for Async Processing
**Date**: 2024-11-04
**Status**: Accepted
**Context:** CSV processing is CPU-intensive and time-consuming.
**Decision:** Use Celery with Redis as broker for async task processing.
**Rationale:**
- Proven solution for Python async processing
- Built-in retry mechanisms
- Task monitoring and management
- Priority queues for different processing types
**Consequences:**
- (+) Scalable processing pipeline
- (+) Robust error handling
- (-) Additional infrastructure components
- (-) Complex local development setup

---

## ADR-007: Role-Based Views Architecture
**Date**: 2024-11-04
**Status**: Accepted
**Context:** Different stakeholders need different views of same data.
**Decision:** Implement role-based dashboard system with predefined views.
**Rationale:**
- Owner needs strategic KPIs
- Operations needs efficiency metrics
- Marketing needs customer insights
- Reduces cognitive load for users
**Consequences:**
- (+) Tailored user experience
- (+) Clear information architecture
- (-) Multiple dashboard components
- (-) Complex permission management

---

## ADR-008: Phased Rollout Strategy
**Date**: 2024-11-04
**Status**: Accepted
**Context:** Platform has high complexity and ambitious features.
**Decision:** Three-phase rollout: MVP → Growth → Advanced.
**Phases:**
1. **MVP**: Auth, upload, basic dashboard, storage
2. **Growth**: Benchmarking, roles, macro context
3. **Advanced**: AI/ML, predictions, API
**Rationale:**
- Reduces initial complexity
- Faster user feedback
- Risk mitigation
- Learn and iterate approach
**Consequences:**
- (+) Manageable scope per phase
- (+) Early user validation
- (-) Feature flag complexity
- (-) User expectation management

---

## ADR-009: TypeScript for Frontend
**Date**: 2024-11-04
**Status**: Accepted
**Context:** Choosing between JavaScript and TypeScript for React frontend.
**Decision:** Use TypeScript for all frontend code.
**Rationale:**
- Type safety for complex business logic
- Better IDE support and refactoring
- Self-documenting interfaces
- Industry standard for enterprise React
**Consequences:**
- (+) Fewer runtime errors
- (+) Better developer experience
- (-) Additional build step
- (-) Learning curve for team

---

## ADR-010: Macroeconomic Indicators as Gaming Metaphor
**Date**: 2024-11-04
**Status**: Accepted
**Context:** Need to contextualize PYME performance with economic conditions.
**Decision:** Present macro indicators as "buffs/debuffs" (gaming metaphor).
**Rationale:**
- Intuitive for users (like WarcraftLogs)
- Clear visual representation
- Simplifies complex economic relationships
- Differentiates from traditional BI tools
**Consequences:**
- (+) Engaging user experience
- (+) Simplified mental model
- (-) Need economic data sources
- (-) User education required

---

## ADR-011: AI Orchestration Framework Integration
**Date**: 2024-11-04
**Status**: Accepted
**Context:** Need structured development approach for complex multi-context platform.
**Decision:** Use AI Orchestration Framework with domain orchestrators.
**Rationale:**
- Clear separation of concerns (frontend/backend/data/devops)
- Quality gates ensure 8.0/10 minimum standard
- Comprehensive test requirements (8 test types)
- Automated documentation generation
**Consequences:**
- (+) Structured development workflow
- (+) Consistent quality standards
- (-) Initial setup overhead
- (-) Learning curve for framework

---

## ADR-012: Local SQLite for Development
**Date**: 2024-11-04
**Status**: Accepted
**Context:** Need simple local development environment.
**Decision:** Use SQLite locally, PostgreSQL in staging/production.
**Rationale:**
- Zero-configuration database for developers
- Django ORM abstracts differences
- Faster onboarding for new developers
**Consequences:**
- (+) Simple local setup
- (+) Fast development cycles
- (-) Some PostgreSQL features unavailable
- (-) Need staging validation

---

## ADR-013: Column Mapping Interface
**Date**: 2024-11-04
**Status**: Accepted
**Context:** Users upload CSVs with varying column names and formats.
**Decision:** Provide visual column mapping interface during upload.
**Rationale:**
- Different PYMEs use different naming conventions
- Based on COLUMN_SCHEMA in src/core/constants.py
- User-friendly mapping reduces errors
- Save mappings for future uploads
**Consequences:**
- (+) Flexible data ingestion
- (+) Reduced support requests
- (-) Additional UI complexity
- (-) Need mapping validation logic

---

## ADR-014: Multi-Level Aggregation Storage
**Date**: 2024-11-04
**Status**: Accepted
**Context:** Need to store data at multiple aggregation levels as shown in test datasets.
**Decision:** Create separate tables for each aggregation level (daily, weekly, monthly, etc).
**Rationale:**
- Faster query performance for different views
- Matches existing data structure in test_client datasets
- Enables quick temporal navigation
- Supports various business analysis needs
**Consequences:**
- (+) Optimized query performance
- (+) Flexible reporting
- (-) Increased storage requirements
- (-) Complex ETL pipeline

---

## ADR-015: Update Tracking System
**Date**: 2024-11-04
**Status**: Accepted
**Context:** Users need to know impact of data updates when re-uploading.
**Decision:** Track rows_before, rows_after, rows_updated for each upload.
**Rationale:**
- Transparency in data operations
- Audit trail for compliance
- User confidence in data integrity
- Critical for month-end reconciliation
**Consequences:**
- (+) Clear data lineage
- (+) User trust
- (-) Additional tracking overhead
- (-) Complex merge logic

---

## ADR-016: Tailwind Premium Templates
**Date**: 2024-11-04
**Status**: Accepted
**Context:** Have access to premium Tailwind templates in tailwind_templates folder.
**Decision:** Use premium Tailwind components for UI consistency.
**Rationale:**
- Professional design out of the box
- Consistent visual language
- Faster frontend development
- Already paid for resource
**Consequences:**
- (+) Beautiful UI quickly
- (+) Responsive by default
- (-) Need to customize for brand
- (-) Learning curve for team

---

## ADR-017: Mandatory Endpoint Tracking
**Date**: 2024-11-04
**Status**: Accepted
**Context:** Need to track all ports, URLs, and endpoints during development.
**Decision:** Maintain mandatory endpoints.txt file updated with every change.
**Rationale:**
- Avoid port conflicts
- Clear documentation for team
- Essential for debugging
- Required for deployment configuration
**Consequences:**
- (+) No port conflicts
- (+) Clear service map
- (-) Additional documentation burden
- (-) Must enforce compliance

---

## ADR-018: No Financial Advice Disclaimer
**Date**: 2024-11-04
**Status**: Accepted
**Context:** Platform provides business metrics but must avoid liability.
**Decision:** Clear disclaimers that system provides information only, not advice.
**Rationale:**
- Legal compliance requirement
- Chilean market is risk-averse
- Protect company from liability
- Build trust through transparency
**Consequences:**
- (+) Legal protection
- (+) Clear user expectations
- (-) May reduce perceived value
- (-) Requires careful UX copy

---

## Technology Stack Summary

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **React Query** for data fetching
- **React Router** for navigation
- **Chart.js** for visualizations

### Backend
- **Django 4.2+** with Django REST Framework
- **PostgreSQL** for primary database
- **Redis** for caching and queues
- **Celery** for async processing
- **Django Channels** for WebSocket

### Infrastructure
- **Railway** for backend hosting
- **Render** for frontend hosting
- **GitHub Actions** for CI/CD
- **Sentry** for error tracking

### Development
- **Docker Compose** for local environment
- **SQLite** for local database
- **Pytest** for Python testing
- **Jest** for JavaScript testing
- **Playwright** for E2E testing

---

**Document Status**: Living document, updated as decisions are made
**Review Frequency**: Monthly or as needed
**Last Updated**: 2024-11-04