# /review-data-flow Command

Analyze and document end-to-end data flow through the entire system to catch missing dependencies and naming mismatches early.

## Usage
```
/review-data-flow [feature-name]
/review-data-flow
```

## What it does
1. Analyzes the system architecture comprehensively
2. Traces data flow from entry points to outputs
3. Identifies all data transformations and dependencies
4. Validates naming consistency across layers
5. Detects missing connections or broken flows
6. Documents the complete data journey
7. Saves flow diagram to `ai-state/human-docs/data-flow-[feature].md`

## Philosophy

**"Review The Flow, Not Just The Code"**

The AI might write perfect functions that don't connect logically. This command asks:
- "Explain end-to-end how data flows through the system"
- "What happens when a user performs action X?"
- "How does data transform from input to output?"
- "Are all dependencies properly connected?"

This catches:
- ❌ Missing dependencies
- ❌ Naming mismatches between layers
- ❌ Broken data pipelines
- ❌ Orphaned functions
- ❌ Circular dependencies
- ❌ Type mismatches
- ❌ Logic gaps

## Parameters
- **feature-name** (optional): Focus analysis on specific feature (e.g., "authentication", "file-upload")
- If omitted, analyzes entire system

## Data Flow Analysis

The command traces data through:

### 1. Entry Points
- API endpoints (HTTP requests)
- WebSocket connections
- Background jobs (Celery tasks)
- CLI commands
- Scheduled jobs

### 2. Request Processing
- Input validation
- Authentication/authorization
- Data deserialization
- Business logic invocation

### 3. Business Logic Layer
- Service functions
- Domain models
- State transitions
- Calculations/transformations

### 4. Data Persistence
- Database writes
- File storage
- Cache updates
- External API calls

### 5. Response Generation
- Data serialization
- Response formatting
- WebSocket broadcasts
- Background job triggers

### 6. Error Handling
- Exception paths
- Error propagation
- Rollback mechanisms
- User feedback

## Output Document Structure

The generated flow document includes:

```markdown
# Data Flow: [Feature Name]

## Overview
High-level description of what this flow accomplishes

## Entry Point
- **Endpoint**: POST /api/v1/upload
- **Trigger**: User uploads CSV file
- **Input Schema**: { file: File, company_id: int }

## Flow Diagram
1. Frontend → Backend API
2. API → File Storage
3. API → Celery Task Queue
4. Celery → Gabeda Processing
5. Gabeda → Database Update
6. Database → WebSocket Notification
7. WebSocket → Frontend Update

## Detailed Flow

### Step 1: File Upload (Frontend → Backend)
- **Location**: src/components/Upload.tsx → apps/processing/views.py
- **Input**: FormData with CSV file
- **Validation**: File size, type, company ownership
- **Output**: { upload_id, status: "queued" }
- **Error Cases**: File too large, invalid format, unauthorized

### Step 2: Storage (Backend → File Storage)
- **Location**: apps/processing/views.py → file_storage.py
- **Input**: File object, company_id
- **Transformation**: Save to company-specific folder
- **Output**: file_path string
- **Dependencies**: AWS S3 credentials, boto3 library

### Step 3: Task Queuing (Backend → Celery)
- **Location**: apps/processing/views.py → tasks.py
- **Input**: { file_path, company_id, upload_id }
- **Task**: process_gabeda_upload.delay()
- **Output**: task_id
- **Dependencies**: Redis, Celery worker

[... continues for each step ...]

## Data Transformations

### Input Format
```json
{
  "file": "customers.csv",
  "company_id": 123
}
```

### After Parsing (Step 4)
```python
{
  "rows": [{"name": "John", "email": "john@example.com"}],
  "mapping": {"name": "customer_name", "email": "contact_email"}
}
```

### After Processing (Step 5)
```python
{
  "customers": [
    {"customer_name": "John", "contact_email": "john@example.com", "company_id": 123}
  ],
  "stats": {"total": 1, "new": 1, "updated": 0}
}
```

### Final Output (Step 7)
```json
{
  "status": "completed",
  "rows_processed": 1,
  "rows_new": 1,
  "rows_updated": 0
}
```

## Dependencies Map

### External Services
- AWS S3: File storage
- Gabeda API: Data processing
- Redis: Task queue
- PostgreSQL: Data persistence

### Internal Services
- authentication: User verification
- companies: Company ownership validation
- endpoints: Endpoint registry
- processing: File processing logic

### Libraries
- pandas: CSV parsing
- celery: Background tasks
- channels: WebSocket
- boto3: S3 integration

## Naming Consistency Check

| Layer | Variable Name | Type | Notes |
|-------|---------------|------|-------|
| Frontend | uploadId | string | ✅ Consistent |
| API | upload_id | int | ⚠️ Type mismatch (should be string) |
| Database | id | UUID | ❌ Naming mismatch |
| WebSocket | fileId | string | ❌ Different naming |

## Missing Connections Detected

1. ❌ **Missing rollback**: If Gabeda fails, uploaded file not deleted from S3
2. ❌ **Missing validation**: No check if company has active subscription
3. ⚠️ **Type mismatch**: upload_id is string in frontend, int in backend
4. ❌ **Orphaned function**: `calculate_diff()` in processing/utils.py never called

## Suggested Fixes

### Fix 1: Add rollback mechanism
```python
# In tasks.py
try:
    result = gabeda_client.process(file_path)
except GabedaError:
    file_storage.delete(file_path)  # Add this
    raise
```

### Fix 2: Standardize upload_id type
```python
# Change upload_id to UUID everywhere
upload_id: UUID = uuid.uuid4()
```

## Circular Dependencies

None detected ✅

## Performance Bottlenecks

1. ⚠️ **Step 4**: CSV parsing blocks worker (use chunking)
2. ⚠️ **Step 5**: Synchronous Gabeda call (timeout: 5min)

## Security Considerations

1. ✅ File upload validated for type and size
2. ✅ Company ownership verified
3. ❌ Missing: Virus scan before processing
4. ❌ Missing: Rate limiting on upload endpoint

---

**Generated:** 2025-11-05T16:30:00Z
**Scope:** file-upload feature
**Status:** Review complete
```

## Example Flow

### Review Entire System
```
User: /review-data-flow
System: Analyzing system architecture...
System: Tracing data flows from entry points...
System: Checking dependencies and naming consistency...
System:
System: Data Flow Analysis Complete
System: - Entry Points: 15
System: - Data Transformations: 47
System: - Dependencies: 23
System: - Naming Mismatches: 4
System: - Missing Connections: 2
System: - Circular Dependencies: 0
System:
System: Document saved to: ai-state/human-docs/data-flow-system.md
System:
System: ⚠️ Found 2 missing connections - review recommended
```

### Review Specific Feature
```
User: /review-data-flow authentication
System: Analyzing authentication flow...
System: Tracing login → token → session → access control...
System:
System: Data Flow Analysis: Authentication
System: - Entry Points: 3 (login, refresh, logout)
System: - Flow Steps: 8
System: - Dependencies: 5
System: - Issues: 1 (missing token expiry check in middleware)
System:
System: Document saved to: ai-state/human-docs/data-flow-authentication.md
```

## When to Use

Run data flow review:
- ✅ **Before running anything** - Catches issues early
- ✅ After implementing new features
- ✅ Before integration testing
- ✅ When debugging mysterious bugs
- ✅ During code reviews
- ✅ After refactoring
- ✅ When onboarding new developers

## Benefits

1. **Early Detection**: Catches missing dependencies before runtime
2. **Naming Consistency**: Identifies variable name mismatches across layers
3. **Logic Validation**: Ensures functions connect properly
4. **Documentation**: Creates living documentation of data flows
5. **Onboarding**: Helps new developers understand the system
6. **Debugging**: Provides map for tracing issues
7. **Architecture Review**: Validates system design decisions

## Next Steps

After reviewing data flow:
1. Read generated document in `ai-state/human-docs/`
2. Address missing connections identified
3. Fix naming mismatches across layers
4. Add missing error handling
5. Optimize identified bottlenecks
6. Update architecture documentation
7. Share with team for review
