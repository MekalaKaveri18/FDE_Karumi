"""Example 1: Full Onboarding Flow for a SaaS Application"""

import asyncio
import sys
import os

# Add parent directory to path so imports work from anywhere
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.validators import ConfigurationValidator
from src.automation import CustomerEnvironmentAdapter, AuthMethod
from playwright.async_api import async_playwright


async def main():
    """
    Complete onboarding flow:
    1. Validate the target application
    2. Configure authentication
    3. Test basic interactions
    """
    
    # Configuration
    TARGET_URL = "https://example-saas.com"
    TEST_USERNAME = "demo@example.com"
    TEST_PASSWORD = "DemoPassword123!"
    
    print("=" * 60)
    print("Karumi Onboarding Flow - Example 1")
    print("=" * 60)
    
    # Step 1: Validate the application
    print("\n Step 1: Validating application setup...")
    validator = ConfigurationValidator(headless=True)
    report = await validator.validate_app(TARGET_URL, TEST_USERNAME, TEST_PASSWORD)
    
    print(f"\nValidation Status: {report.status.upper()}")
    print(f"Checks Passed: {sum(1 for c in report.checks if c.passed)}/{len(report.checks)}")
    
    if report.edge_cases:
        print("\n Edge Cases Detected:")
        for case in report.edge_cases:
            print(f"  - {case}")
    
    if report.recommendations:
        print("\n Recommendations:")
        for rec in report.recommendations:
            print(f"  - {rec}")
    
    # Step 2: Configure and test
    print("\n Step 2: Setting up authentication...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        adapter = CustomerEnvironmentAdapter(page)
        
        # Configure auth
        success = await adapter.configure_auth(
            AuthMethod.BASIC,
            username=TEST_USERNAME,
            password=TEST_PASSWORD
        )
        
        if success:
            print(" Authentication configured")
            
            # Get environment info
            env_info = await adapter.get_environment_info()
            print(f" Environment ready: {env_info['url']}")
        else:
            print(" Failed to configure authentication")
        
        await context.close()
        await browser.close()
    
    print("\n" + "=" * 60)
    print(" Onboarding flow complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
