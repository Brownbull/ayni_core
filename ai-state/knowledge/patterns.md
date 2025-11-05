# AYNI Core - Design Patterns & Best Practices

## Architectural Patterns

### 1. Microservices Pattern
- **Frontend**: Independent React app on Render
- **Backend**: Django API on Railway
- **Processing**: Celery workers as separate services
- **Benefits**: Independent scaling, deployment, and development

### 2. Repository Pattern
- **Implementation**: Django models abstract database operations
- **Purpose**: Decouple business logic from data access
- **Example**:
```python
class CompanyRepository:
    def get_by_user(self, user_id):
        return Company.objects.filter(users__id=user_id)

    def get_with_metrics(self, company_id):
        return Company.objects.prefetch_related('features').get(id=company_id)
```

### 3. Event-Driven Architecture
- **Events**: Upload started, processing complete, metrics calculated
- **Implementation**: Celery tasks + Django signals + WebSockets
- **Benefits**: Loose coupling, async processing, real-time updates

## Django Patterns

### 1. Django Project Structure
```
backend/
├── config/             # Settings, URLs, WSGI
├── apps/
│   ├── authentication/ # User auth
│   ├── companies/      # Company management
│   ├── analytics/      # Analytics engine
│   ├── processing/     # Data processing
│   └── api/           # API endpoints
├── core/              # Shared utilities
└── tests/             # Test suite
```

### 2. Django Model Pattern
```python
class BaseModel(models.Model):
    """Abstract base with common fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Company(BaseModel):
    name = models.CharField(max_length=255)
    rut = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name_plural = "Companies"
```

### 3. Django Serializer Pattern
```python
class CompanySerializer(serializers.ModelSerializer):
    metrics = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = ['id', 'name', 'rut', 'metrics']

    def get_metrics(self, obj):
        return obj.get_latest_metrics()
```

## Data Processing Patterns

### 1. Celery Task Pattern
```python
@shared_task(bind=True, max_retries=3)
def process_csv_task(self, upload_id):
    try:
        upload = Upload.objects.get(id=upload_id)
        # Process the CSV
        process_data(upload.file.path)
        upload.status = 'completed'
        upload.save()
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
```

### 2. GabeDA Integration Pattern
```python
class FeatureProcessor:
    def __init__(self, feature_store):
        self.feature_store = feature_store

    def process(self, dataframe, company_id):
        # Load model configuration
        model = self.feature_store.load_model(company_id)

        # Execute feature pipeline
        results = self.execute_pipeline(dataframe, model)

        # Store results
        self.store_results(results, company_id)
```

## Frontend Patterns (React + TypeScript)

### 1. Component Structure Pattern
```typescript
interface DashboardProps {
  companyId: string;
  role: UserRole;
}

export const Dashboard: React.FC<DashboardProps> = ({ companyId, role }) => {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics(companyId).then(setMetrics).finally(() => setLoading(false));
  }, [companyId]);

  if (loading) return <Spinner />;
  if (!metrics) return <ErrorMessage />;

  return <MetricsDisplay metrics={metrics} role={role} />;
};
```

### 2. API Service Pattern
```typescript
class APIService {
  private baseURL = process.env.REACT_APP_API_URL;

  async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) throw new APIError(response);
    return response.json();
  }

  getCompanyMetrics(id: string) {
    return this.request<Metrics>(`/api/companies/${id}/metrics`);
  }
}
```

### 3. State Management Pattern
```typescript
// Using Context for global state
interface AppState {
  user: User | null;
  company: Company | null;
  theme: Theme;
}

const AppContext = createContext<AppState | undefined>(undefined);

export const useAppState = () => {
  const context = useContext(AppContext);
  if (!context) throw new Error('useAppState must be within AppProvider');
  return context;
};
```

## Database Patterns

### 1. PostgreSQL Schema Design
```sql
-- Company features table with JSONB for flexibility
CREATE TABLE features (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    upload_id INTEGER REFERENCES uploads(id),
    feature_name VARCHAR(255),
    feature_value JSONB,
    calculated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_company_features (company_id, feature_name)
);

-- Benchmark aggregations
CREATE TABLE benchmarks (
    id SERIAL PRIMARY KEY,
    industry VARCHAR(100),
    metric_name VARCHAR(255),
    period DATE,
    value DECIMAL(20,4),
    sample_size INTEGER CHECK (sample_size >= 10),
    percentiles JSONB,
    UNIQUE(industry, metric_name, period)
);
```

### 2. Query Optimization Pattern
```python
# Django ORM optimization
companies = Company.objects.filter(
    industry='retail'
).select_related(
    'owner'  # JOIN in single query
).prefetch_related(
    'features',  # Separate optimized query
    'uploads'
).annotate(
    total_revenue=Sum('features__value',
                     filter=Q(features__name='revenue'))
)
```

## Security Patterns

### 1. Authentication Middleware
```python
class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if token:
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                request.user_id = payload['user_id']
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Invalid token'}, status=401)

        return self.get_response(request)
```

### 2. Data Isolation Pattern
```python
class CompanyDataMixin:
    """Ensure users only access their company's data"""

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(company__users=self.request.user)
```

## Testing Patterns

### 1. Django Test Pattern
```python
class CSVProcessingTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test@example.com')
        self.company = Company.objects.create(name='Test Co', rut='12345678-9')
        self.client.force_authenticate(user=self.user)

    @patch('processing.tasks.process_csv_task.delay')
    def test_csv_upload_triggers_processing(self, mock_task):
        with open('test_data.csv', 'rb') as f:
            response = self.client.post('/api/uploads/', {'file': f})

        self.assertEqual(response.status_code, 201)
        mock_task.assert_called_once()
```

### 2. React Testing Pattern
```typescript
describe('Dashboard Component', () => {
  it('displays metrics after loading', async () => {
    const mockMetrics = { revenue: 100000, customers: 50 };
    jest.spyOn(api, 'getMetrics').mockResolvedValue(mockMetrics);

    render(<Dashboard companyId="123" role="owner" />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/revenue/i)).toBeInTheDocument();
      expect(screen.getByText(/100000/)).toBeInTheDocument();
    });
  });
});
```

## Performance Patterns

### 1. Caching Strategy
```python
# Redis caching for expensive queries
from django.core.cache import cache

def get_company_benchmarks(company_id):
    cache_key = f'benchmarks:{company_id}'
    benchmarks = cache.get(cache_key)

    if not benchmarks:
        benchmarks = calculate_benchmarks(company_id)
        cache.set(cache_key, benchmarks, timeout=3600)  # 1 hour

    return benchmarks
```

### 2. Async Processing Pattern
```python
class CSVUploadView(APIView):
    def post(self, request):
        # Quick validation and storage
        serializer = UploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        upload = serializer.save()

        # Async heavy processing
        process_csv_task.delay(upload.id)

        # Immediate response
        return Response({
            'id': upload.id,
            'status': 'processing',
            'status_url': f'/api/uploads/{upload.id}/status'
        }, status=201)
```

## Error Handling Patterns

### 1. Graceful Degradation
```python
def get_macro_indicators(company):
    """Get macro indicators with fallback"""
    try:
        # Try external API
        return fetch_external_indicators(company.industry)
    except ExternalAPIError:
        # Fall back to cached data
        return get_cached_indicators(company.industry)
    except Exception:
        # Ultimate fallback
        return get_default_indicators()
```

### 2. User-Friendly Errors
```typescript
const ErrorBoundary: React.FC = ({ children }) => {
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    const handleError = (error: ErrorEvent) => {
      console.error('Error caught:', error);
      setHasError(true);
      // Send to error tracking service
      trackError(error);
    };

    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  if (hasError) {
    return <FriendlyErrorMessage />;
  }

  return <>{children}</>;
};
```

## DevOps Patterns

### 1. Environment Configuration
```python
# settings/base.py
class Settings:
    DEBUG = env.bool('DEBUG', default=False)
    DATABASE_URL = env.str('DATABASE_URL')
    REDIS_URL = env.str('REDIS_URL')

    @property
    def DATABASES(self):
        return {
            'default': dj_database_url.parse(self.DATABASE_URL)
        }

# settings/production.py
class ProductionSettings(Settings):
    DEBUG = False
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
```

### 2. CI/CD Pipeline Pattern
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          python manage.py test
          npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Railway
        run: railway up
```

---

## Task Completion Documentation Pattern

**CRITICAL**: After completing ANY task, create BOTH documents:

1. **Evaluation** → `ai-state/evaluations/task-XXX-evaluation.md`
   - 8 metric scores (component architecture, state management, etc.)
   - Test results (8 test types)
   - Quality checklist

2. **Implementation Report** → `ai-state/reports/task-XXX-implementation-report.md`
   - Executive summary
   - Technical implementation details
   - Usage examples
   - Lessons learned
   - Integration points
   - See task-005 or task-006 reports as templates

**Both files are mandatory. Missing either = incomplete task.**

---

**Last Updated**: 2025-11-05
**Version**: 1.1
**Purpose**: Standard patterns for consistent implementation across AYNI platform