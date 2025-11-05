# AYNI Platform - Live Endpoints Registry

## Purpose
**LIVE ENDPOINTS ONLY** - This file tracks currently working, tested endpoints that are IN USE.
Only add endpoints after they have been implemented and verified.

---

## Local Development Ports

### Backend (Django)
- **Port**: 8000
- **URL**: http://localhost:8000
- **Status**: ✅ ACTIVE
- **Command**: `cd C:/Projects/play/ayni_be && python manage.py runserver`

### Frontend (React)
- **Port**: 3000
- **URL**: http://localhost:3000
- **Status**: ⏳ NOT YET RUNNING
- **Command**: `cd C:/Projects/play/ayni_fe && npm run dev`

### Database (PostgreSQL)
- **Port**: 5432
- **URL**: postgresql://localhost:5432/ayni_dev
- **Status**: ✅ ACTIVE

---

## Live API Endpoints

### Django Admin (✅ ACTIVE)
Base URL: `http://localhost:8000/admin/`

- **GET**    `/admin/` - Admin login page
- **POST**   `/admin/login/` - Admin authentication
- **GET**    `/admin/authentication/user/` - User management
- **GET**    `/admin/companies/company/` - Company management
- **GET**    `/admin/processing/upload/` - Upload management
- **GET**    `/admin/analytics/*` - Analytics models

**Auth**: Django session-based
**Credentials**: admin@ayni.cl / gabe123123
**Implemented**: Task 002

---

### Authentication API (✅ ACTIVE)
Base URL: `http://localhost:8000/api/auth/`

#### User Registration
- **POST** `/api/auth/register/`
  ```json
  Request: {
    "email": "user@example.com",
    "username": "username",
    "password": "password123",
    "password_confirm": "password123"
  }
  Response: {
    "user": {...},
    "tokens": {
      "access": "...",
      "refresh": "..."
    }
  }
  ```

#### User Login
- **POST** `/api/auth/login/`
  ```json
  Request: {
    "email": "user@example.com",
    "password": "password123"
  }
  Response: {
    "user": {...},
    "tokens": {
      "access": "...",
      "refresh": "..."
    }
  }
  ```

#### User Logout
- **POST** `/api/auth/logout/`
  - **Auth**: JWT Bearer token required
  - **Body**: `{"refresh": "refresh_token_here"}`
  - **Effect**: Blacklists refresh token

#### Token Refresh
- **POST** `/api/auth/token/refresh/`
  ```json
  Request: {
    "refresh": "refresh_token_here"
  }
  Response: {
    "access": "new_access_token",
    "refresh": "new_refresh_token"
  }
  ```

#### User Profile
- **GET** `/api/auth/profile/`
  - **Auth**: JWT Bearer token required
  - **Returns**: Full user profile

- **PATCH** `/api/auth/profile/`
  - **Auth**: JWT Bearer token required
  - **Body**: `{"username": "newname"}` (partial update)

#### Password Change
- **POST** `/api/auth/change-password/`
  - **Auth**: JWT Bearer token required
  ```json
  Request: {
    "old_password": "current",
    "new_password": "new123",
    "new_password_confirm": "new123"
  }
  ```

**Test User**: admin@ayni.cl / gabe123123
**Implemented**: Task 003

---

### Companies API (✅ ACTIVE)
Base URL: `http://localhost:8000/api/companies/`

#### Company CRUD

- **GET** `/api/companies/`
  - **Auth**: JWT Bearer token required
  - **Returns**: List of companies user has access to
  ```json
  Response: [
    {
      "id": 1,
      "name": "Mi PYME",
      "rut": "12.345.678-9",
      "industry": "retail",
      "size": "micro",
      "user_role": "owner",
      "user_permissions": {...}
    }
  ]
  ```

- **POST** `/api/companies/`
  - **Auth**: JWT Bearer token required
  - **Effect**: Creates company and assigns user as owner
  ```json
  Request: {
    "name": "Company Name",
    "rut": "12.345.678-9",
    "industry": "retail",
    "size": "micro"
  }
  ```

- **GET** `/api/companies/{id}/`
  - **Auth**: JWT Bearer token required
  - **Permission**: Must have company access
  - **Returns**: Company details with user role/permissions

- **PATCH** `/api/companies/{id}/`
  - **Auth**: JWT Bearer token required
  - **Permission**: `can_manage_company`
  - **Body**: Partial company update

- **PUT** `/api/companies/{id}/`
  - **Auth**: JWT Bearer token required
  - **Permission**: `can_manage_company`
  - **Body**: Full company update

- **DELETE** `/api/companies/{id}/`
  - **Auth**: JWT Bearer token required
  - **Permission**: `owner` role only
  - **Effect**: Soft deletes company (sets is_active=false)

#### User Management

- **GET** `/api/companies/{company_id}/users/`
  - **Auth**: JWT Bearer token required
  - **Permission**: Must have company access
  - **Returns**: List of all users with access to company

- **POST** `/api/companies/{company_id}/users/`
  - **Auth**: JWT Bearer token required
  - **Permission**: `can_manage_users`
  ```json
  Request: {
    "user": 2,
    "role": "analyst"
  }
  ```

- **GET** `/api/companies/user-companies/{id}/`
  - **Auth**: JWT Bearer token required
  - **Permission**: `can_manage_users`
  - **Returns**: User-company relationship details

- **PATCH** `/api/companies/user-companies/{id}/`
  - **Auth**: JWT Bearer token required
  - **Permission**: `can_manage_users`
  - **Body**: Update role or permissions

- **DELETE** `/api/companies/user-companies/{id}/`
  - **Auth**: JWT Bearer token required
  - **Permission**: `can_manage_users`
  - **Effect**: Removes user from company (cannot remove last owner)

**Roles**: owner, admin, manager, analyst, viewer
**Implemented**: Task 004

---

## Authentication Details

### JWT Token Format
```
Authorization: Bearer <access_token>
```

### Token Lifetimes
- **Access Token**: 60 minutes
- **Refresh Token**: 7 days
- **Rotation**: Enabled (new refresh token on each refresh)
- **Blacklisting**: Enabled (on logout)

### Security Features
- Argon2 password hashing
- Account lockout (5 failed attempts = 15 min lockout)
- Token blacklisting on logout
- IP tracking for security audits

---

## Company Roles & Permissions

| Role | can_view | can_upload | can_export | can_manage_users | can_delete_data | can_manage_company |
|------|----------|------------|------------|------------------|-----------------|-------------------|
| **owner** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **admin** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **manager** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **analyst** | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **viewer** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## Quick Test Commands

### Test Authentication
```bash
# Register user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"test","password":"test123","password_confirm":"test123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@ayni.cl","password":"gabe123123"}'
```

### Test Companies
```bash
# Get access token first, then:

# List companies
curl -X GET http://localhost:8000/api/companies/ \
  -H "Authorization: Bearer <access_token>"

# Create company
curl -X POST http://localhost:8000/api/companies/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test PYME","rut":"12.345.678-9","industry":"retail","size":"micro"}'
```

---

## Industry Codes (for Companies)

Valid `industry` values:
- `retail` - Retail / Comercio
- `food` - Food & Beverage / Alimentos y Bebidas
- `manufacturing` - Manufacturing / Manufactura
- `services` - Services / Servicios
- `technology` - Technology / Tecnología
- `construction` - Construction / Construcción
- `agriculture` - Agriculture / Agricultura
- `healthcare` - Healthcare / Salud
- `education` - Education / Educación
- `other` - Other / Otro

---

## Company Size Codes

Valid `size` values:
- `micro` - Micro (1-9 employees)
- `small` - Small (10-49 employees)
- `medium` - Medium (50-249 employees)

---

## Chilean RUT Format

Valid format: `XX.XXX.XXX-X`

Examples:
- `12.345.678-9`
- `76.123.456-7`
- `9.876.543-K`

**Validation**: Check digit calculated using mod-11 algorithm

---

## Status Codes Reference

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET/PATCH/PUT |
| 201 | Created | Successful POST (resource created) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Missing/invalid auth token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist or no access |

---

## Environment Setup

### Backend .env (C:/Projects/play/ayni_be/.env)
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/ayni_dev
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Frontend .env (C:/Projects/play/ayni_fe/.env)
```env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
```

---

**Last Updated**: 2025-11-05
**Active Endpoints**: 17 (Admin: 6, Auth: 7, Companies: 10)
**Pending Implementation**: Uploads, Processing, Analytics, AI/ML
**Update Rule**: Only add endpoints after implementation + verification