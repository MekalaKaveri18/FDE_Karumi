# Karumi Deployment & Reliability Toolkit

A comprehensive open-source toolkit for onboarding, testing, monitoring, and troubleshooting AI agent deployments. Built to mirror real customer rollout challenges for platforms like Karumi.

## 🎯 Features

### 1. **Automated Onboarding & Configuration Validator**
- Validates browser automation setup and compatibility
- Detects common UI elements (buttons, inputs, links, etc.)
- Tests login flows and authentication mechanisms
- Identifies edge cases (2FA, dynamic modals, lazy loading)
- Generates detailed compatibility reports

### 2. **End-to-End Testing Harness**
- Simulate user interactions with Playwright
- Retry logic for flaky elements (configurable retries)
- Screenshot capture on failures
- Conversation flow validation
- Support for complex multi-step scenarios

### 3. **Monitoring & Troubleshooting Dashboard**
- Real-time session monitoring with Streamlit UI
- FastAPI backend for data serving
- Event logging with structured data
- Automated suggestions for common issues
- Metrics tracking (success rate, response times, error analysis)

### 4. **Lightweight Automation Scripts**
- Customer environment adapters (multiple auth methods)
- Multi-language support switching
- Multi-tab workflow handling
- CAPTCHA detection
- Bulk environment setup and deployment

## 📦 Tech Stack

- **Browser**: Playwright (real browser automation)
- **AI/LLM**: OpenAI, Anthropic, Groq (via LangChain)
- **Language**: Python 3.10+
- **Dashboard**: Streamlit (frontend) + FastAPI (backend)
- **Logging**: structlog (structured JSON logging)
- **Deployment**: Docker, Docker Compose
- **Testing**: pytest, pytest-asyncio

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker (optional)
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/karumi-toolkit.git
cd karumi-toolkit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### Quick Examples

#### 1. Validate a SaaS Application

```bash
python examples/example_1_onboarding_flow.py
```

Or using CLI:

```bash
python -m src.validators.cli validate https://example.com \
  --username demo@example.com \
  --password MyPassword123 \
  --output validation_report.json
```

#### 2. Run End-to-End Tests

```bash
python examples/example_2_e2e_testing.py
```

#### 3. Monitor a Session

```bash
python examples/example_3_monitoring.py

# View dashboard
streamlit run src/monitoring/dashboard.py
```

## 📋 Core Modules

### Validators (`src/validators/`)

```python
from src.validators import ConfigurationValidator

validator = ConfigurationValidator()
report = await validator.validate_app(
    "https://example.com",
    username="user@example.com",
    password="password"
)

print(f"Status: {report.status}")
print(f"Edge cases: {report.edge_cases}")
print(f"Recommendations: {report.recommendations}")
```

### Testing (`src/testing/`)

```python
from src.testing import TestingHarness, ActionStep
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.launch()
    page = await browser.new_page()
    harness = TestingHarness(page)
    
    steps = [
        ActionStep(
            name="Navigate",
            description="Go to dashboard",
            action=lambda p, s: p.goto("https://example.com"),
            retries=3
        )
    ]
    
    result = await harness.run_scenario("My Test", steps)
```

### Monitoring (`src/monitoring/`)

```python
from src.monitoring import get_dashboard, EventType, Severity

dashboard = get_dashboard()
session = dashboard.create_session("my_session_001")

session.log_event(
    event_type=EventType.CLICK,
    message="Clicked submit button",
    severity=Severity.INFO
)

metrics = session.get_metrics()
print(f"Success rate: {metrics.success_rate:.1%}")
```

### Automation (`src/automation/`)

```python
from src.automation import CustomerEnvironmentAdapter, AuthMethod

adapter = CustomerEnvironmentAdapter(page)

# Configure authentication
await adapter.configure_auth(
    AuthMethod.BASIC,
    username="user@example.com",
    password="password"
)

# Switch language
from src.automation import LanguageCode
await adapter.set_language(LanguageCode.ES)

# Get environment info
info = await adapter.get_environment_info()
```

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Services available at:
# - API: http://localhost:8000
# - Dashboard: http://localhost:8501
```

### Build Custom Image

```bash
docker build -f docker/Dockerfile -t karumi-toolkit:latest .
docker run -p 8000:8000 -p 8501:8501 karumi-toolkit:latest
```

## 📊 API Reference

The FastAPI backend provides REST endpoints for monitoring data:

```bash
# Get summary
curl http://localhost:8000/api/summary

# List sessions
curl http://localhost:8000/api/sessions

# Get session data
curl http://localhost:8000/api/sessions/session_001

# Get recent events
curl http://localhost:8000/api/sessions/session_001/events?limit=50

# Get metrics
curl http://localhost:8000/api/sessions/session_001/metrics

# Get errors
curl http://localhost:8000/api/sessions/session_001/errors
```

## 🧪 Testing

Run tests locally:

```bash
pytest tests/ -v

# Run with async support
pytest tests/ -v --asyncio-mode=auto

# Run specific test file
pytest tests/test_validators.py -v
```

## 📝 Configuration

Create a `.env` file for environment variables:

```bash
# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk-...

# Browser Settings
HEADLESS=true
BROWSER_TIMEOUT=30000
SCREENSHOT_ON_FAILURE=true

# Testing Settings
MAX_RETRIES=3
RETRY_DELAY=2
TEST_TIMEOUT=60

# Monitoring
LOG_LEVEL=INFO
ENABLE_SENTRY=false

# Dashboard
DASHBOARD_PORT=8501
API_PORT=8000
```

## 📚 Detailed Usage Examples

### Example 1: Complete Onboarding Flow

```python
# Validate → Configure → Test
python examples/example_1_onboarding_flow.py
```

**Output:**
```
Validation Status: SUCCESS
Checks Passed: 6/6

⚠️ Edge Cases Detected:
  - Dynamic modals detected (2)
  - Lazy loading detected

💡 Recommendations:
  - Good ARIA labels present - voice automation may work well
  - Improve accessibility with proper labels
```

### Example 2: E2E Testing

```python
# Run complex user scenario with retries and monitoring
python examples/example_2_e2e_testing.py
```

**Output:**
```
📈 Test Scenario: Sales Dashboard Analysis
Overall Status: PASSED
Duration: 3450ms

Steps Executed:
  ✅ Navigate to Dashboard (450ms)
  ✅ Filter Sales Data (800ms)
  ✅ Verify Chart Display (300ms)
  ✅ Extract Chart Insights (250ms)
```

### Example 3: Monitoring

```python
# Monitor session in real-time
python examples/example_3_monitoring.py
```

**Output:**
```
ℹ️ NAVIGATION   | Navigated to dashboard page
ℹ️ WAIT         | Waiting for chart data to load
ℹ️ CLICK        | Clicked filter button
⚠️ ERROR        | Failed to load chart - selector changed
ℹ️ WAIT         | Retrying with new selector
```

## 🔧 Advanced Features

### Custom Retry Logic

```python
step = ActionStep(
    name="Risky Operation",
    action=my_async_function,
    retries=5,           # Max 5 attempts
    retry_delay=3        # 3 seconds between retries
)
```

### Multiple Authentication Methods

```python
# Basic Auth
await adapter.configure_auth(AuthMethod.BASIC, username="...", password="...")

# OAuth2
await adapter.configure_auth(AuthMethod.OAUTH2, client_id="...", client_secret="...")

# API Key
await adapter.configure_auth(AuthMethod.API_KEY, api_key="...", header_name="X-API-Key")

# SAML
await adapter.configure_auth(AuthMethod.SAML, username="...", password="...", idp_url="...")
```

### Bulk Environment Setup

```python
from src.automation import BulkEnvironmentSetup

setup = BulkEnvironmentSetup()

# Register multiple environments
await setup.register_environment(
    "production", "https://prod.example.com",
    AuthMethod.BASIC, username="prod_user", password="..."
)

await setup.register_environment(
    "staging", "https://staging.example.com",
    AuthMethod.OAUTH2, client_id="...", client_secret="..."
)

# Deploy to all
results = await setup.deploy_to_all(deployment_config)
```

## 📈 Performance Monitoring

The toolkit includes built-in metrics:

- **Response Times**: Track action execution duration
- **Success Rate**: Monitor pass/fail rates
- **Error Tracking**: Categorize and suggest fixes
- **Event Timeline**: Detailed action history
- **Browser State**: Capture page state at each step

## 🐛 Troubleshooting

### Playwright Installation Issues

```bash
# Re-install browsers
playwright install chromium

# For WSL/Linux
playwright install-deps
```

### Browser Timeouts

```python
# Increase timeout for slow applications
validator = ConfigurationValidator(timeout=60000)  # 60 seconds

# Or per-step
step = ActionStep(..., retries=5, retry_delay=3)
```

### Authentication Failures

Enable logging for detailed diagnostics:

```python
import structlog
logger = structlog.get_logger(__name__)
logger.info("Auth attempt", method=auth_method, user=username)
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🎓 Use Cases

✅ **Pre-deployment Validation**: Check application compatibility before deploying agents  
✅ **Quality Assurance**: End-to-end testing with retry logic and failure capture  
✅ **Production Monitoring**: Real-time tracking of agent behavior and errors  
✅ **Customer Onboarding**: Automated setup and configuration for different environments  
✅ **Troubleshooting**: Quick diagnostics with suggested fixes  
✅ **Feedback Loops**: Structured data for product team insights  

## 🚀 Next Steps

1. **Clone & Setup**: `git clone && cd karumi-toolkit && pip install -r requirements.txt`
2. **Run Examples**: Try the 3 example scripts to see toolkit in action
3. **Customize**: Adapt validators and test scenarios for your SaaS
4. **Deploy**: Use Docker Compose for production deployment
5. **Monitor**: Access Streamlit dashboard at `http://localhost:8501`
6. **Share**: Record demo video showing toolkit capabilities

## 📞 Support

- **Issues**: Open GitHub issue for bugs
- **Discussions**: Use GitHub Discussions for questions
- **Docs**: Check `/docs` folder for detailed guides
- **Examples**: See `/examples` for more use cases

## ⭐ Show Your Support

Found this useful? Please consider:
- Starring the repository
- Sharing with others
- Contributing improvements
- Using in your production systems

---

**Built for Karumi — Making AI Agent Deployments Reliable** 🚀
