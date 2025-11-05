# AYNI Project - Absolute Paths Reference

**Purpose**: Quick reference for all absolute paths across the multi-repo AYNI platform.

---

## Repository Root Paths

### Orchestration Repository (Current)
```
C:\Projects\play\ayni_core
```
- **Purpose**: AI orchestration, task management, GabeDA engine
- **Key Directories**:
  - `.claude/` - Orchestration framework
  - `ai-state/` - Task registry, knowledge base, standards
  - `src/` - GabeDA feature engine (shared by backend)
  - `data/`, `feature_store/`, `outputs/` - Data processing

### Backend Repository
```
C:\Projects\play\ayni_be
```
- **Purpose**: Django REST API, database, Celery workers
- **Expected Structure** (per task-001):
  - `apps/authentication/` - JWT auth system
  - `apps/companies/` - Company management
  - `apps/processing/` - CSV upload, Celery tasks
  - `apps/analytics/` - Analytics API
  - `config/` - Django settings, URLs, WSGI
  - `manage.py` - Django management script
  - `requirements.txt` - Python dependencies
  - `Dockerfile`, `docker-compose.yml` - Containerization

### Frontend Repository
```
C:\Projects\play\ayni_fe
```
- **Purpose**: React TypeScript UI
- **Expected Structure** (per task-001):
  - `src/components/` - Reusable UI components
  - `src/pages/` - Route pages
  - `src/services/` - API client
  - `src/store/` - State management
  - `src/hooks/` - Custom React hooks
  - `src/utils/` - Utility functions
  - `package.json` - npm dependencies
  - `vite.config.ts` - Vite configuration
  - `tailwind.config.js` - Tailwind CSS config

---

## Common Operations

### Navigation Commands

```bash
# Go to orchestration (planning/knowledge)
cd C:\Projects\play\ayni_core

# Go to backend (API development)
cd C:\Projects\play\ayni_be

# Go to frontend (UI development)
cd C:\Projects\play\ayni_fe
```

### Task Execution Context

When executing tasks:
- **Backend tasks** (`context: backend`): Work in `C:\Projects\play\ayni_be`
- **Frontend tasks** (`context: frontend`): Work in `C:\Projects\play\ayni_fe`
- **Data tasks** (`context: data`): Work in `C:\Projects\play\ayni_core/src`
- **DevOps tasks** (`context: devops`): Work across all three repos

---

## File Path Patterns in Task Definitions

### Backend Task Paths
```yaml
where: "C:/Projects/play/ayni_be/apps/authentication/"
```

### Frontend Task Paths
```yaml
where: "C:/Projects/play/ayni_fe/src/components/Upload/"
```

### Shared Data/GabeDA Paths
```yaml
where: "C:/Projects/play/ayni_core/src/features/"
```

---

## Import Relationships

### Backend imports GabeDA
```python
# In ayni_be files
import sys
sys.path.append('C:/Projects/play/ayni_core')
from src.core.constants import COLUMN_SCHEMA
from src.execution.engine import FeatureEngine
```

### Frontend API endpoint registry
```typescript
// Generated from backend
// C:/Projects/play/ayni_be/generate_api_types.py
// Output: C:/Projects/play/ayni_fe/src/types/api.ts
```

---

## Verification Commands

### Check if repos exist
```bash
# From ayni_core
ls C:/Projects/play/ayni_be/manage.py      # Should exist if backend created
ls C:/Projects/play/ayni_fe/package.json   # Should exist if frontend created
```

### Verify Django apps
```bash
cd C:/Projects/play/ayni_be
python manage.py showmigrations  # List all apps
```

### Verify React setup
```bash
cd C:/Projects/play/ayni_fe
npm list react  # Check React version
```

---

## Environment Variables

### Backend (.env location)
```
C:\Projects\play\ayni_be\.env
```

### Frontend (.env location)
```
C:\Projects\play\ayni_fe\.env
```

### Orchestration (.env location)
```
C:\Projects\play\ayni_core\.env
```

---

## Docker Compose

### Master compose file
```
C:\Projects\play\ayni_core\docker-compose.yml
```

### Backend compose file
```
C:\Projects\play\ayni_be\docker-compose.yml
```

### Runs all services together
```bash
cd C:\Projects\play\ayni_core
docker-compose up
```

---

## Endpoint Registry

**Central registry location**:
```
C:\Projects\play\ayni_core\ai-state\knowledge\endpoints.txt
```

This file is maintained across all repositories to track:
- API endpoint URLs
- Service ports
- WebSocket connections
- Database connection strings

---

**Last Updated**: 2025-11-05
**Status**: Multi-repo structure confirmed
**Windows Paths**: Using forward slashes for cross-platform compatibility
