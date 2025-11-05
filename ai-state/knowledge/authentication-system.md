# Authentication System - Knowledge Base

**Last Updated**: 2025-11-05
**Implemented In**: task-003-authentication-system
**Status**: Production Ready

---

## Overview

AYNI uses JWT-based authentication with Django REST Framework, providing secure user registration, login, logout, token management, and profile functionality with Argon2 password hashing.

---

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | Create new user account | No |
| POST | `/api/auth/login/` | Authenticate and get tokens | No |
| POST | `/api/auth/logout/` | Blacklist refresh token | Yes |
| POST | `/api/auth/token/refresh/` | Get new access token | No (refresh token) |
| GET | `/api/auth/profile/` | View user profile | Yes |
| PATCH | `/api/auth/profile/` | Update user profile | Yes |
| POST | `/api/auth/change-password/` | Change password | Yes |

---

## Security Features

### Password Security
- **Argon2** password hashing (strongest available)
- Django password validators (length, complexity, common passwords)
- Passwords never returned in API responses
- Secure password change flow with current password verification

### Token Security
- JWT access tokens (60-minute expiration, configurable)
- JWT refresh tokens (7-day expiration, configurable)
- Token rotation on refresh (new refresh token issued)
- Token blacklisting on logout
- Bearer token authentication

### Account Security
- Failed login attempt counter
- Account lockout after 5 failed attempts (15-minute coolout)
- Automatic failed attempt reset on successful login
- Last login IP tracking
- Email stored lowercase for consistency

---

## Authentication Flow

### Registration Flow
```
1. User submits email, username, password
2. System validates data (email format, password strength, uniqueness)
3. Password hashed with Argon2
4. User created in database
5. JWT tokens generated
6. Return user data + tokens
```

### Login Flow
```
1. User submits email, password
2. Check if account locked out (failed attempts)
3. Authenticate credentials
4. If success:
   - Reset failed attempts
   - Update last login timestamp + IP
   - Generate JWT tokens
   - Return user data + tokens
5. If failure:
   - Increment failed attempts
   - Lock account if threshold reached (5 attempts)
   - Return error with remaining attempts
```

### Token Refresh Flow
```
1. Client sends refresh token
2. Validate token (not expired, not blacklisted)
3. Generate new access token
4. If rotation enabled, generate new refresh token
5. Blacklist old refresh token
6. Return new tokens
```

### Logout Flow
```
1. Client sends refresh token
2. Add token to blacklist
3. Token cannot be reused
4. Client discards tokens
```

---

## Configuration

### JWT Settings (config/settings.py)
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # Configurable via env
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # Configurable via env
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

### Password Hashing (config/settings.py)
```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',  # Primary
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',  # Fallback
]
```

---

## Database Schema

### User Model
```python
class User(AbstractUser):
    email = EmailField(unique=True)  # Primary identifier
    username = CharField(unique=True)
    password = CharField()  # Argon2 hashed

    # Security fields
    failed_login_attempts = IntegerField(default=0)
    lockout_until = DateTimeField(null=True)
    last_login_ip = GenericIPAddressField(null=True)
    is_email_verified = BooleanField(default=False)

    # Timestamps
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
```

### Token Blacklist Tables
- `token_blacklist_outstandingtoken` - Track all issued refresh tokens
- `token_blacklist_blacklistedtoken` - Track revoked/blacklisted tokens

---

## Usage Examples

### Register (Frontend)
```javascript
const response = await fetch('/api/auth/register/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    email: 'user@ayni.cl',
    username: 'user',
    password: 'SecurePass123!',
    password_confirm: 'SecurePass123!',
  })
});

const data = await response.json();
// Store tokens: data.tokens.access, data.tokens.refresh
```

### Login (Frontend)
```javascript
const response = await fetch('/api/auth/login/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    email: 'user@ayni.cl',
    password: 'SecurePass123!'
  })
});

const data = await response.json();
// Store tokens: data.tokens.access, data.tokens.refresh
```

### Authenticated Request (Frontend)
```javascript
const response = await fetch('/api/auth/profile/', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});
```

### Token Refresh (Frontend)
```javascript
const response = await fetch('/api/auth/token/refresh/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    refresh: refreshToken
  })
});

const data = await response.json();
// Update access token: data.access
// Update refresh token if rotated: data.refresh
```

---

## Admin User

**Default admin account for testing/management:**
- Email: admin@ayni.cl
- Username: admin
- Password: gabe123123
- Access: Django admin panel at `/admin/`

**Security Note**: Change password in production!

---

## Integration Notes

### Frontend Integration
- Store JWT tokens in memory or secure storage (not localStorage for security)
- Include access token in Authorization header: `Bearer <token>`
- Refresh access token before expiration using refresh token
- Handle token expiration (401 responses)
- Clear tokens on logout

### Backend Integration
- Protected views use `permission_classes = [IsAuthenticated]`
- Access current user via `request.user`
- Check permissions via `request.user.has_perm()`

---

## Error Handling

### Common Error Responses

**400 Bad Request** - Validation error
```json
{
  "email": ["A user with that email already exists."],
  "password": ["This password is too common."]
}
```

**401 Unauthorized** - Authentication failed
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Account Locked**
```json
{
  "non_field_errors": [
    "Account is temporarily locked due to failed login attempts. Please try again in 12 minutes."
  ]
}
```

---

## Performance

- **Login**: ~250ms (Argon2 hashing overhead acceptable for security)
- **Token Refresh**: ~150ms
- **Profile GET**: ~50ms

---

## Future Enhancements (Post-MVP)

1. Email verification flow
2. Password reset via email
3. Social authentication (Google, GitHub)
4. Multi-factor authentication (MFA)
5. Session management UI
6. Login history tracking
7. Device management

---

## References

- **Implementation Report**: `ai-state/reports/task-003-implementation-report.md`
- **Evaluation**: `ai-state/evaluations/task-003-authentication-system.md`
- **Code**: `C:/Projects/play/ayni_be/apps/authentication/`
- **Tests**: `C:/Projects/play/ayni_be/apps/authentication/test_authentication.py`
