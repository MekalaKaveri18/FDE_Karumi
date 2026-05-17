# Quick Reference Guide - Karumi Toolkit

## Installation
```bash
pip install -r requirements.txt
playwright install
```

## Core Modules

### 1. Validators (`src/validators/`)
**Purpose**: Validate SaaS applications for agent compatibility

```python
from src.validators import ConfigurationValidator

validator = ConfigurationValidator()
report = await validator.validate_app("https://example.com")
```

**CLI Usage**:
```bash
python -m src.validators.cli validate https://example.com \
  --username user@example.com --password pass --output report.json
```

### 2. Testing (`src/testing/`)
**Purpose**: Run end-to-end test scenarios with retry logic

```python
from src.testing import TestingHarness, ActionStep

harness = TestingHarness(page)
result = await harness.run_scenario("Test Name", steps)
```

**Key Methods**:
- `navigate(url)` - Go to URL
- `click_element(selector)` - Click element
- `fill_input(selector, text)` - Fill input
- `wait_for_element(selector)` - Wait for visibility
- `extract_text(selector)` - Get text content

### 3. Monitoring (`src/monitoring/`)
**Purpose**: Real-time event tracking and metrics

```python
from src.monitoring import get_dashboard, EventType, Severity

session = dashboard.create_session("session_001")
session.log_event(EventType.CLICK, "Clicked button", Severity.INFO)
```

**Dashboard**:
```bash
streamlit run src/monitoring/dashboard.py
```

**API**:
```bash
python -m src.monitoring.api
# http://localhost:8000/api/summary
# http://localhost:8000/api/sessions
```

### 4. Automation (`src/automation/`)
**Purpose**: Customer environment setup and workflow adapters

```python
from src.automation import CustomerEnvironmentAdapter, AuthMethod

adapter = CustomerEnvironmentAdapter(page)
await adapter.configure_auth(AuthMethod.BASIC, username="...", password="...")
```

## Event Types
```python
EventType.NAVIGATION    # Navigation to URL
EventType.CLICK        # Element click
EventType.INPUT        # Text input
EventType.WAIT         # Waiting for element
EventType.ERROR        # Error occurred
EventType.SCREENSHOT   # Screenshot taken
EventType.CONVERSATION # Agent/user message
```

## Severity Levels
```python
Severity.INFO      # Informational
Severity.WARNING   # Warning
Severity.ERROR     # Error
Severity.CRITICAL  # Critical issue
```

## Authentication Methods
```python
AuthMethod.BASIC    # Username/password
AuthMethod.OAUTH2   # OAuth2 flow
AuthMethod.SAML     # SAML SSO
AuthMethod.API_KEY  # API key header
```

## Common Workflows

### Validate App + Test + Monitor
```python
# 1. Validate
validator = ConfigurationValidator()
report = await validator.validate_app("https://example.com")

# 2. Test
harness = TestingHarness(page)
result = await harness.run_scenario("Test", steps)

# 3. Monitor
session = dashboard.create_session("test_001")
session.log_event(EventType.CLICK, "User clicked", Severity.INFO)
```

### Multi-Environment Deployment
```python
setup = BulkEnvironmentSetup()
await setup.register_environment("prod", "https://prod.com", AuthMethod.BASIC, ...)
await setup.register_environment("staging", "https://staging.com", AuthMethod.OAUTH2, ...)
results = await setup.deploy_to_all(config)
```

### Language Support
```python
from src.automation import LanguageCode

adapter = CustomerEnvironmentAdapter(page)
await adapter.set_language(LanguageCode.ES)  # Spanish
await adapter.set_language(LanguageCode.FR)  # French
await adapter.set_language(LanguageCode.DE)  # German
```

## Docker Commands

```bash
# Build image
docker build -f docker/Dockerfile -t karumi:latest .

# Run single service
docker run -p 8000:8000 karumi:latest

# Run all services
docker-compose -f docker/docker-compose.yml up

# Stop containers
docker-compose -f docker/docker-compose.yml down
```

## Make Commands

```bash
make install         # Install dependencies
make dev             # Setup development
make test            # Run tests
make lint            # Check code style
make format          # Format code
make examples        # Run all examples
make run-dashboard   # Start dashboard
make docker-up       # Start Docker services
```

## Configuration (.env)

```bash
HEADLESS=true                    # Run in headless mode
BROWSER_TIMEOUT=30000            # ms to wait for elements
SCREENSHOT_ON_FAILURE=true       # Save screenshots on errors
MAX_RETRIES=3                    # Number of retries
RETRY_DELAY=2                    # Delay between retries
LOG_LEVEL=INFO                   # Logging level
DASHBOARD_PORT=8501              # Streamlit port
API_PORT=8000                    # FastAPI port
```

## API Endpoints

```
GET  /                           # API info
GET  /api/summary                # Dashboard summary
GET  /api/sessions               # List sessions
GET  /api/sessions/{id}          # Session data
GET  /api/sessions/{id}/events   # Session events
GET  /api/sessions/{id}/metrics  # Session metrics
GET  /api/sessions/{id}/errors   # Session errors
```

## File Locations

| Type | Location |
|------|----------|
| Source Code | `src/` |
| Examples | `examples/` |
| Tests | `tests/` |
| Docker | `docker/` |
| Docs | `.md` files |
| Config | `.env`, `.env.example` |

## Troubleshooting

**Playwright not found**
```bash
playwright install
playwright install-deps  # For Linux
```

**Module import errors**
```bash
pip install -r requirements.txt
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Timeout issues**
```bash
# Increase timeout in .env
BROWSER_TIMEOUT=60000
TEST_TIMEOUT=120
```

**Dashboard connection refused**
```bash
# Start API first
python -m src.monitoring.api

# Then start dashboard
streamlit run src/monitoring/dashboard.py
```

## Performance Tips

1. Use headless mode (default)
2. Increase retries for flaky sites
3. Use parallel testing with pytest-xdist
4. Cache login/authentication
5. Use screenshot comparison sparingly

## Best Practices

1. **Always use try/except** for browser operations
2. **Set explicit timeouts** for elements
3. **Log important events** for debugging
4. **Use meaningful test names** for clarity
5. **Review edge cases** before production
6. **Test with real browsers** (not just headless)
7. **Monitor resource usage** in production
8. **Rotate credentials** in shared environments

## Examples Location

```bash
# Run individual examples
python examples/example_1_onboarding_flow.py
python examples/example_2_e2e_testing.py
python examples/example_3_monitoring.py

# Or all together
make examples
```

## Getting Help

- 📖 README.md - Full documentation
- 📚 GETTING_STARTED.md - Setup guide
- 🤝 CONTRIBUTING.md - Contribution guidelines
- 💬 GitHub Issues - Report bugs
- 📧 support@example.com - Contact

## Links

- **GitHub**: https://github.com/yourusername/karumi-toolkit
- **Documentation**: https://github.com/yourusername/karumi-toolkit#readme
- **Issues**: https://github.com/yourusername/karumi-toolkit/issues
- **PyPI**: https://pypi.org/project/karumi-toolkit/

---

**For detailed information, see README.md**

Last Updated: 2024
