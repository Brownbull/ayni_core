# Environment Management Scripts

**Purpose:** Living documentation for local environment initialization and cleanup scripts
**Status:** 🔄 LIVING DOCUMENT (Updated with each task that adds services)
**Last Updated:** 2025-11-05T08:15:00Z
**Current Phase:** Task 008 Complete (Backend + Celery + Flower)

---

## Overview

This document tracks the **living scripts** that must exist in the `tests/` folders for both frontend and backend. These scripts are maintained in sync with the project status and updated as new services are added.

**Key Principle:** Scripts reflect the **current state** of implemented features only. Services are added to scripts **only after** their implementation task is completed.

---

## Backend Scripts

**Location:** `C:/Projects/play/ayni_be/tests/`

### Script 1: `start_backend_local.sh` (or `.bat` for Windows)

**Purpose:** Initialize all backend services in local development environment

**Current Components (as of Task 008):**
- ✅ PostgreSQL database (Task 001)
- ✅ Redis (cache & message broker) (Task 001)
- ✅ Django backend server (Task 001)
- ✅ Celery worker (Task 008)
- ✅ Celery beat (Task 008)
- ✅ Flower monitoring dashboard (Task 008)

**Script Content:**

```bash
#!/bin/bash
# start_backend_local.sh
# Initialize AYNI Backend Local Environment
# Last Updated: 2025-11-05 (Task 008)
# Services: PostgreSQL, Redis, Django, Celery, Flower

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 Starting AYNI Backend Local Environment..."
echo "================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Navigate to project root
cd "$PROJECT_ROOT"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Copying from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env from .env.example"
    else
        echo "❌ Error: .env.example not found. Cannot proceed."
        exit 1
    fi
fi

echo ""
echo "📦 Starting services with Docker Compose..."
echo "Services: db, redis, backend, celery, celery-beat, flower"
echo ""

# Start all backend services
docker-compose up -d db redis backend celery celery-beat flower

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be healthy..."
echo ""

# Wait for PostgreSQL
echo "  Checking PostgreSQL..."
timeout 30 bash -c 'until docker-compose exec -T db pg_isready -U ayni_user > /dev/null 2>&1; do sleep 1; done' || {
    echo "❌ PostgreSQL failed to start"
    exit 1
}
echo "  ✅ PostgreSQL ready"

# Wait for Redis
echo "  Checking Redis..."
timeout 30 bash -c 'until docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; do sleep 1; done' || {
    echo "❌ Redis failed to start"
    exit 1
}
echo "  ✅ Redis ready"

# Wait for Django (check if port 8000 is responding)
echo "  Checking Django..."
timeout 60 bash -c 'until curl -s http://localhost:8000/admin/ > /dev/null 2>&1; do sleep 2; done' || {
    echo "❌ Django failed to start"
    exit 1
}
echo "  ✅ Django ready"

# Wait for Flower (check if port 5555 is responding)
echo "  Checking Flower..."
timeout 30 bash -c 'until curl -s http://localhost:5555 > /dev/null 2>&1; do sleep 2; done' || {
    echo "❌ Flower failed to start"
    exit 1
}
echo "  ✅ Flower ready"

# Check Celery worker is running
echo "  Checking Celery worker..."
if docker-compose ps celery | grep -q "Up"; then
    echo "  ✅ Celery worker running"
else
    echo "  ⚠️  Warning: Celery worker may not be running"
fi

echo ""
echo "================================================"
echo "✅ All backend services started successfully!"
echo "================================================"
echo ""
echo "🌐 Access Points:"
echo "  - Django API:     http://localhost:8000"
echo "  - Django Admin:   http://localhost:8000/admin/"
echo "  - API Docs:       http://localhost:8000/api/docs/"
echo "  - Flower:         http://localhost:5555"
echo ""
echo "📊 Service Status:"
docker-compose ps
echo ""
echo "📝 View logs:"
echo "  - All services:   docker-compose logs -f"
echo "  - Django:         docker-compose logs -f backend"
echo "  - Celery:         docker-compose logs -f celery"
echo "  - Flower:         docker-compose logs -f flower"
echo ""
echo "🛑 Stop services:  ./tests/stop_backend_local.sh"
echo ""
```

**Windows Version (`start_backend_local.bat`):**

```batch
@echo off
REM start_backend_local.bat
REM Initialize AYNI Backend Local Environment
REM Last Updated: 2025-11-05 (Task 008)
REM Services: PostgreSQL, Redis, Django, Celery, Flower

echo 🚀 Starting AYNI Backend Local Environment...
echo ================================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker is not running. Please start Docker Desktop.
    exit /b 1
)

REM Navigate to project root
cd /d "%~dp0.."

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  Warning: .env file not found. Copying from .env.example...
    if exist ".env.example" (
        copy .env.example .env
        echo ✅ Created .env from .env.example
    ) else (
        echo ❌ Error: .env.example not found. Cannot proceed.
        exit /b 1
    )
)

echo.
echo 📦 Starting services with Docker Compose...
echo Services: db, redis, backend, celery, celery-beat, flower
echo.

REM Start all backend services
docker-compose up -d db redis backend celery celery-beat flower

echo.
echo ⏳ Waiting for services to be healthy...
echo.

REM Wait for services (simplified for Windows)
timeout /t 15 /nobreak >nul

echo.
echo ================================================
echo ✅ All backend services started!
echo ================================================
echo.
echo 🌐 Access Points:
echo   - Django API:     http://localhost:8000
echo   - Django Admin:   http://localhost:8000/admin/
echo   - API Docs:       http://localhost:8000/api/docs/
echo   - Flower:         http://localhost:5555
echo.
echo 📊 Service Status:
docker-compose ps
echo.
echo 🛑 Stop services:  tests\stop_backend_local.bat
echo.
```

---

### Script 2: `stop_backend_local.sh` (or `.bat` for Windows)

**Purpose:** Stop and cleanup all running backend services

**Script Content:**

```bash
#!/bin/bash
# stop_backend_local.sh
# Stop AYNI Backend Local Environment
# Last Updated: 2025-11-05 (Task 008)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🛑 Stopping AYNI Backend Local Environment..."
echo "================================================"

cd "$PROJECT_ROOT"

# Stop all services
echo "Stopping services: db, redis, backend, celery, celery-beat, flower"
docker-compose stop db redis backend celery celery-beat flower

# Optional: Remove containers (uncomment if needed)
# docker-compose down

echo ""
echo "✅ All backend services stopped"
echo ""
echo "📊 Remaining containers:"
docker-compose ps
echo ""
echo "💡 To completely remove containers and volumes:"
echo "   docker-compose down -v"
echo ""
```

**Windows Version (`stop_backend_local.bat`):**

```batch
@echo off
REM stop_backend_local.bat
REM Stop AYNI Backend Local Environment
REM Last Updated: 2025-11-05 (Task 008)

echo 🛑 Stopping AYNI Backend Local Environment...
echo ================================================

cd /d "%~dp0.."

echo Stopping services: db, redis, backend, celery, celery-beat, flower
docker-compose stop db redis backend celery celery-beat flower

echo.
echo ✅ All backend services stopped
echo.
echo 📊 Remaining containers:
docker-compose ps
echo.
echo 💡 To completely remove containers and volumes:
echo    docker-compose down -v
echo.
```

---

## Frontend Scripts

**Location:** `C:/Projects/play/ayni_fe/tests/`

### Script 1: `start_frontend_local.sh` (or `.bat` for Windows)

**Purpose:** Initialize frontend development server

**Current Components (as of Task 008):**
- ⏳ React development server (NOT YET IMPLEMENTED - Task 013+)
- ⏳ Vite dev server (NOT YET IMPLEMENTED - Task 013+)

**Script Content (Placeholder - will be updated when frontend tasks complete):**

```bash
#!/bin/bash
# start_frontend_local.sh
# Initialize AYNI Frontend Local Environment
# Last Updated: 2025-11-05 (Task 008)
# Status: ⏳ PLACEHOLDER - Frontend not yet implemented

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "⏳ Frontend not yet implemented"
echo "This script will be populated after Task 013 (Authentication UI)"
echo ""
echo "Planned services:"
echo "  - Vite dev server (port 3000)"
echo "  - React development mode"
echo ""
exit 1
```

**Windows Version (`start_frontend_local.bat`):**

```batch
@echo off
REM start_frontend_local.bat
REM Initialize AYNI Frontend Local Environment
REM Last Updated: 2025-11-05 (Task 008)
REM Status: ⏳ PLACEHOLDER - Frontend not yet implemented

echo ⏳ Frontend not yet implemented
echo This script will be populated after Task 013 (Authentication UI)
echo.
echo Planned services:
echo   - Vite dev server (port 3000)
echo   - React development mode
echo.
exit /b 1
```

---

### Script 2: `stop_frontend_local.sh` (or `.bat` for Windows)

**Purpose:** Stop frontend development server and kill any running instances

**Script Content (Placeholder):**

```bash
#!/bin/bash
# stop_frontend_local.sh
# Stop AYNI Frontend Local Environment
# Last Updated: 2025-11-05 (Task 008)
# Status: ⏳ PLACEHOLDER - Frontend not yet implemented

set -e

echo "⏳ Frontend not yet implemented"
echo "This script will be populated after Task 013 (Authentication UI)"
exit 1
```

**Windows Version (`stop_frontend_local.bat`):**

```batch
@echo off
REM stop_frontend_local.bat
REM Stop AYNI Frontend Local Environment
REM Last Updated: 2025-11-05 (Task 008)
REM Status: ⏳ PLACEHOLDER - Frontend not yet implemented

echo ⏳ Frontend not yet implemented
echo This script will be populated after Task 013 (Authentication UI)
exit /b 1
```

---

## Update History

### Task 008 (2025-11-05) - Celery & Flower Added
**Services Added:**
- ✅ Celery worker
- ✅ Celery beat
- ✅ Flower (port 5555)

**Backend Scripts Updated:**
- `start_backend_local.sh`: Added celery, celery-beat, flower services
- `stop_backend_local.sh`: Added celery, celery-beat, flower services

### Task 001 (2025-11-04) - Initial Project Setup
**Services Added:**
- ✅ PostgreSQL (port 5432)
- ✅ Redis (port 6379)
- ✅ Django backend (port 8000)

**Scripts Created:**
- Initial backend start/stop scripts
- Frontend placeholder scripts

---

## Future Updates

### Task 009 - GabeDA Integration
**Expected Changes:** None (no new services)

### Task 010 - WebSocket Progress
**Expected Changes:**
- May add Daphne/Channels worker if not using Django dev server
- Update health checks to include WebSocket connectivity

### Task 013 - Authentication UI (Frontend)
**Expected Changes:**
- **Frontend scripts will be fully implemented**
- Add Vite dev server startup
- Add npm/pnpm commands
- Add port 3000 health checks
- Add process killing for stuck frontend instances

### Task 015 - Upload Interface (Frontend)
**Expected Changes:** None (uses existing Vite server)

### Future Tasks
- Scripts will be updated only when tasks add new services
- Each update will increment version in script header
- Change log will be maintained in this document

---

## Script Maintenance Rules

### When to Update Scripts

✅ **DO UPDATE when:**
- New service added to docker-compose.yml
- New port opened for external access
- New dependency required for startup
- Health check requirements change

❌ **DON'T UPDATE when:**
- Internal code changes (no new services)
- Database migrations (handled by Django)
- Configuration changes (handled by .env)
- Test additions (don't affect startup)

### Update Process

1. **Task completes** → New service implemented
2. **Identify script impact** → Does it add a runtime service?
3. **Update script** → Add service to start/stop commands
4. **Update version** → Increment "Last Updated" in script header
5. **Update this document** → Add entry to "Update History"
6. **Test locally** → Verify scripts work end-to-end

---

## Testing Scripts

### Backend Script Tests

```bash
# Test start script
cd C:/Projects/play/ayni_be
./tests/start_backend_local.sh

# Verify all services running
docker-compose ps
# Expected: All services "Up" status

# Test endpoints
curl http://localhost:8000/admin/  # Django
curl http://localhost:5555         # Flower

# Test stop script
./tests/stop_backend_local.sh

# Verify all services stopped
docker-compose ps
# Expected: All services "Exit 0" or not running
```

### Frontend Script Tests (After Task 013)

```bash
# Test start script
cd C:/Projects/play/ayni_fe
./tests/start_frontend_local.sh

# Verify server running
curl http://localhost:3000

# Test stop script
./tests/stop_frontend_local.sh

# Verify no processes on port 3000
lsof -i :3000  # Should show nothing
```

---

## Troubleshooting

### Backend Scripts

**Issue:** Docker not running
```bash
# Solution: Start Docker Desktop
# Windows: Launch Docker Desktop from Start Menu
# Mac: Launch Docker from Applications
# Linux: sudo systemctl start docker
```

**Issue:** Port already in use (8000, 5432, 6379, 5555)
```bash
# Solution: Stop existing services
docker-compose down

# Or kill specific port (example for 8000)
# Windows: netstat -ano | findstr :8000 && taskkill /PID <PID> /F
# Unix: lsof -ti:8000 | xargs kill -9
```

**Issue:** Services stuck in "starting" state
```bash
# Solution: Check logs
docker-compose logs backend
docker-compose logs celery

# Hard restart
docker-compose down
docker-compose up -d
```

### Frontend Scripts (Future)

**Issue:** Node modules not installed
```bash
# Solution: Install dependencies
npm install  # or pnpm install
```

**Issue:** Port 3000 already in use
```bash
# Solution: Kill existing process
# Windows: netstat -ano | findstr :3000 && taskkill /PID <PID> /F
# Unix: lsof -ti:3000 | xargs kill -9
```

---

## Platform-Specific Notes

### Windows (PowerShell Alternative)

For PowerShell users, create `start_backend_local.ps1`:

```powershell
# start_backend_local.ps1
# AYNI Backend - PowerShell Version

Write-Host "🚀 Starting AYNI Backend..." -ForegroundColor Green

# Check Docker
$dockerRunning = docker info 2>$null
if (-not $dockerRunning) {
    Write-Host "❌ Docker not running" -ForegroundColor Red
    exit 1
}

# Start services
docker-compose up -d db redis backend celery celery-beat flower

Write-Host "✅ Services started!" -ForegroundColor Green
```

### macOS/Linux

Scripts are bash-based and should work on both platforms with minor adjustments for:
- Path separators (handled by using $PWD)
- Docker socket location (auto-detected)
- Terminal colors (using ANSI codes)

---

## Integration with CI/CD

These scripts are **local development only**. For CI/CD:

- Use `docker-compose.ci.yml` for CI environments
- Use platform-specific deployment scripts (Railway, Render)
- See `ai-state/standards/devops-standard.md` for deployment

---

## Related Documentation

- **Docker Compose:** `C:/Projects/play/ayni_be/docker-compose.yml`
- **Endpoints Registry:** `ai-state/knowledge/endpoints.md`
- **Architecture:** `ai-state/knowledge/architecture.md`
- **DevOps Standard:** `ai-state/standards/devops-standard.md`

---

**Document Status:** 🔄 LIVING - Auto-updated with each task
**Maintainer:** DevOps Orchestrator
**Next Update:** Task 009 (GabeDA Integration) - No script changes expected
**Major Update Expected:** Task 013 (Frontend Authentication UI)
