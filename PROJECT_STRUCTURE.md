# Karumi Toolkit - Project Structure

## Directory Layout

```
karumi-toolkit/
├── src/                              # Main source code
│   ├── __init__.py
│   ├── config.py                    # Configuration management
│   ├── logging_config.py            # Logging setup
│   │
│   ├── validators/                  # Configuration Validator
│   │   ├── __init__.py             # Main validator logic
│   │   └── cli.py                  # CLI interface
│   │
│   ├── testing/                     # E2E Testing Harness
│   │   ├── __init__.py             # Testing harness logic
│   │   └── cli.py                  # CLI for running tests
│   │
│   ├── monitoring/                  # Monitoring & Dashboard
│   │   ├── __init__.py             # Core monitoring logic
│   │   ├── dashboard.py            # Streamlit dashboard UI
│   │   └── api.py                  # FastAPI server
│   │
│   └── automation/                  # Automation Scripts
│       ├── __init__.py             # Customer adapters
│       └── cli.py                  # CLI for automation
│
├── examples/                        # Example scripts
│   ├── example_1_onboarding_flow.py
│   ├── example_2_e2e_testing.py
│   └── example_3_monitoring.py
│
├── docker/                          # Docker configuration
│   ├── Dockerfile                  # Production image
│   ├── Dockerfile.dev              # Development image
│   └── docker-compose.yml          # Multi-service setup
│
├── tests/                           # Test suite
│   ├── conftest.py                 # Pytest fixtures
│   ├── test_validators.py
│   └── test_monitoring.py
│
├── .gitignore                       # Git ignore rules
├── .env.example                     # Example env vars
├── requirements.txt                 # Python dependencies
├── setup.py                         # Package setup
├── pytest.ini                       # Pytest config
├── README.md                        # Documentation
└── PROJECT_STRUCTURE.md             # This file
```

## Module Responsibilities

### src/validators/
- Validates SaaS app compatibility for automation
- Detects UI elements and authentication
- Identifies edge cases and risks
- Generates validation reports

### src/testing/
- Executes multi-step test scenarios
- Implements retry logic for flaky elements
- Captures screenshots on failures
- Tracks conversation flow

### src/monitoring/
- Real-time session monitoring
- Event logging with structured data
- Dashboard visualization (Streamlit)
- REST API for data access (FastAPI)
- Metrics and error analysis

### src/automation/
- Customer environment adapters
- Multi-auth support (Basic, OAuth2, SAML, API Key)
- Language switching
- Multi-tab workflows
- Bulk environment setup

## Key Features Per Module

| Module | Feature | Purpose |
|--------|---------|---------|
| validators | Page load check | Verify app accessibility |
| validators | UI detection | Find interactive elements |
| validators | Accessibility scan | Check ARIA labels |
| validators | Login flow test | Validate auth setup |
| validators | Dynamic content | Detect modals/SPAs |
| testing | Retry logic | Handle flaky elements |
| testing | Screenshots | Capture failures |
| testing | Step tracking | Monitor test progress |
| monitoring | Event logging | Track all actions |
| monitoring | Suggestions | Fix common issues |
| monitoring | Metrics | Success rate, timing |
| automation | Auth adapters | Support multiple methods |
| automation | Language switching | Test internationalization |
| automation | Environment setup | Bulk configuration |

## Running the Project

### Development
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```

### Examples
```bash
python examples/example_1_onboarding_flow.py
python examples/example_2_e2e_testing.py
python examples/example_3_monitoring.py
```

### Production
```bash
docker-compose -f docker/docker-compose.yml up -d
# API: http://localhost:8000
# Dashboard: http://localhost:8501
```

## Adding New Features

1. **New Validator Check**: Add to `src/validators/__init__.py`
2. **New Test Step Type**: Extend `ActionStep` in `src/testing/__init__.py`
3. **New Event Type**: Add to `EventType` enum in `src/monitoring/__init__.py`
4. **New Auth Method**: Add case in `src/automation/__init__.py`

## Testing New Functionality

1. Create test file: `tests/test_new_feature.py`
2. Run: `pytest tests/test_new_feature.py -v`
3. Add fixtures as needed in `tests/conftest.py`

## Deployment

- **Local**: `pip install -r requirements.txt && python src/validators/cli.py`
- **Docker**: `docker build -f docker/Dockerfile -t karumi-toolkit:latest .`
- **Compose**: `docker-compose -f docker/docker-compose.yml up`

---

See README.md for full documentation.
