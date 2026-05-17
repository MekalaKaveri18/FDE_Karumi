# Getting Started with Karumi Toolkit

This guide will help you get up and running with the Karumi Deployment & Reliability Toolkit.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git (optional, for cloning)
- 2GB of free disk space

## Installation (5 minutes)

### Step 1: Clone or Download

```bash
git clone https://github.com/yourusername/karumi-toolkit.git
cd karumi-toolkit
```

### Step 2: Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
playwright install
```

### Step 4: Copy Environment File

```bash
cp .env.example .env
# Edit .env with your API keys if needed
```

## Quick Start (10 minutes)

### 1. Validate Your First App

```bash
python examples/example_1_onboarding_flow.py
```

This will:
- Test if a SaaS app is accessible
- Detect UI elements
- Check authentication setup
- Identify potential issues

### 2. Run a Test Scenario

```bash
python examples/example_2_e2e_testing.py
```

This will:
- Simulate user interactions
- Handle retries automatically
- Take screenshots on failures
- Generate a test report

### 3. View Monitoring Dashboard

```bash
# Terminal 1: Start API server
python -m uvicorn src.monitoring.api:app --reload

# Terminal 2: Start Streamlit dashboard
streamlit run src/monitoring/dashboard.py
```

Visit: http://localhost:8501

## Common Tasks

### Using the Validator CLI

```bash
# Validate an application
python -m src.validators.cli validate https://example.com \
  --username user@example.com \
  --password mypassword \
  --output report.json

# View the report
cat report.json
```

### Creating Custom Tests

Create `my_test.py`:

```python
import asyncio
from src.testing import TestingHarness, ActionStep
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        harness = TestingHarness(page)
        
        # Navigate to your app
        await harness.navigate("https://example.com")
        
        # Create and run steps
        steps = [
            ActionStep(
                name="Click Button",
                description="Click the submit button",
                action=lambda p, s: p.click("[type='submit']"),
                retries=3
            )
        ]
        
        result = await harness.run_scenario("My Test", steps)
        print(f"Result: {result.overall_status}")
        
        await browser.close()

asyncio.run(main())
```

Run it:
```bash
python my_test.py
```

### Monitoring a Session

```python
from src.monitoring import get_dashboard, EventType, Severity

dashboard = get_dashboard()
session = dashboard.create_session("demo_001")

# Log events
session.log_event(
    event_type=EventType.CLICK,
    message="Clicked login button",
    severity=Severity.INFO
)

# Check metrics
metrics = session.get_metrics()
print(f"Success Rate: {metrics.success_rate:.1%}")
```

## Docker Deployment

### Single Service

```bash
# Build image
docker build -f docker/Dockerfile -t karumi:latest .

# Run container
docker run -p 8000:8000 -p 8501:8501 karumi:latest
```

### Multi-Service (Recommended)

```bash
# Start all services
docker-compose -f docker/docker-compose.yml up

# Stop services
docker-compose -f docker/docker-compose.yml down
```

Access:
- **API**: http://localhost:8000
- **Dashboard**: http://localhost:8501

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_validators.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'playwright'"

**Solution:**
```bash
pip install -r requirements.txt
playwright install
```

### Issue: "Playwright browser not found"

**Solution:**
```bash
playwright install
# Or for headless browsers
playwright install-deps
```

### Issue: "Connection refused" when starting dashboard

**Solution:**
```bash
# Make sure API is running in another terminal
python -m uvicorn src.monitoring.api:app --reload

# Then start dashboard
streamlit run src/monitoring/dashboard.py
```

### Issue: Timeout errors on slow connections

**Solution:** Increase timeout in .env:
```bash
BROWSER_TIMEOUT=60000
TEST_TIMEOUT=120
```

## Next Steps

1. **Read the README**: `cat README.md`
2. **Explore Examples**: Check `examples/` directory
3. **Review Code**: Understand structure in `src/`
4. **Write Tests**: Create tests in `tests/`
5. **Deploy**: Use Docker for production

## File Structure

```
karumi-toolkit/
├── src/              # Main code
├── examples/         # Example scripts
├── tests/           # Test cases
├── docker/          # Docker files
├── docs/            # Documentation
├── README.md        # Main docs
└── requirements.txt # Dependencies
```

## Support & Help

- 📖 **Documentation**: See README.md
- 🐛 **Issues**: GitHub Issues
- 💬 **Discussions**: GitHub Discussions
- 📧 **Email**: support@example.com

## Useful Commands

```bash
# See all available commands
make help

# Install and setup
make install
make dev

# Running
make examples
make run-validator
make run-dashboard

# Testing
make test
make lint
make format

# Docker
make docker-build
make docker-up
```

## Performance Tips

1. Use headless mode (default) for faster execution
2. Increase retries for flaky applications
3. Run in parallel using pytest-xdist
4. Monitor memory usage with large screenshot collections

## Security

1. Never commit `.env` file with real credentials
2. Use environment variables for secrets
3. Restrict dashboard access in production
4. Review browser console logs for sensitive data

## Feedback

Help us improve by:
- Reporting issues
- Suggesting features
- Sharing usage patterns
- Contributing code

---

**Ready to get started?** Run your first example:

```bash
python examples/example_1_onboarding_flow.py
```

Good luck! 🚀
