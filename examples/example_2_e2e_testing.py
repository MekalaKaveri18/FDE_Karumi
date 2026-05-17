"""Example 2: End-to-End Testing Scenario"""

import asyncio
import sys
import os

# Add parent directory to path so imports work from anywhere
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright
from src.testing import TestingHarness, ActionStep
from src.monitoring import get_dashboard, EventType, Severity


async def navigate_to_dashboard(page, step):
    """Navigate to dashboard"""
    await page.goto("https://example-saas.com/dashboard")
    await page.wait_for_selector("[data-testid='dashboard']", timeout=5000)
    return True


async def filter_sales_data(page, step):
    """Filter sales data"""
    # Click filter button
    await page.click("[data-testid='filter-button']")
    
    # Wait for filter panel
    await page.wait_for_selector("[data-testid='filter-panel']", timeout=3000)
    
    # Select filter criteria
    await page.click("select[data-testid='filter-type']")
    await page.click("text=Sales")
    
    # Set date range
    await page.fill("[data-testid='start-date']", "2024-01-01")
    await page.fill("[data-testid='end-date']", "2024-12-31")
    
    # Apply filter
    await page.click("[data-testid='apply-filter']")
    
    # Wait for results
    await page.wait_for_selector("[data-testid='results']", timeout=5000)
    
    return True


async def verify_chart_display(page, step):
    """Verify chart is displaying correctly"""
    # Check if chart container is visible
    chart_visible = await page.is_visible("[data-testid='chart']")
    
    if not chart_visible:
        raise Exception("Chart not visible after filtering")
    
    return True


async def extract_chart_insights(page, step):
    """Extract insights from chart"""
    # Get chart data or text representation
    chart_title = await page.text_content("[data-testid='chart-title']")
    chart_data = await page.text_content("[data-testid='chart-data']")
    
    return {"title": chart_title, "data": chart_data}


async def main():
    """Run end-to-end testing scenario"""
    
    print("=" * 60)
    print("Karumi E2E Testing - Example 2")
    print("=" * 60)
    
    # Create dashboard and session
    dashboard = get_dashboard()
    session = dashboard.create_session("e2e_test_001")
    
    print(f"\n Session created: e2e_test_001")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Create test harness
        harness = TestingHarness(page, headless=True)
        
        # Define test steps
        steps = [
            ActionStep(
                name="Navigate to Dashboard",
                description="Go to dashboard page",
                action=navigate_to_dashboard,
                expected_outcome="Dashboard loads successfully",
                retries=3
            ),
            ActionStep(
                name="Filter Sales Data",
                description="Apply sales filter with date range",
                action=filter_sales_data,
                expected_outcome="Filter applied and results shown",
                retries=3
            ),
            ActionStep(
                name="Verify Chart Display",
                description="Verify chart renders correctly",
                action=verify_chart_display,
                expected_outcome="Chart is visible and contains data",
                retries=2
            ),
            ActionStep(
                name="Extract Chart Insights",
                description="Extract data from chart for analysis",
                action=extract_chart_insights,
                expected_outcome="Chart data successfully extracted",
                retries=2
            ),
        ]
        
        # Run the scenario
        result = await harness.run_scenario(
            "Sales Dashboard Analysis",
            steps
        )
        
        # Log results to monitoring session
        for step_result in result.steps:
            severity = Severity.ERROR if step_result.status.value == "failed" else Severity.INFO
            session.log_event(
                event_type=EventType.CLICK,  # Generic event type for this example
                message=f"Step '{step_result.step_name}' - {step_result.status.value}",
                severity=severity,
                details=step_result.details
            )
        
        # Print summary
        print(f"\n Test Scenario: {result.scenario_name}")
        print(f"Overall Status: {result.overall_status.value.upper()}")
        print(f"Duration: {result.duration_ms:.0f}ms")
        print(f"\nSteps Executed:")
        for step in result.steps:
            status_icon = "" if step.status.value == "passed" else ""
            print(f"  {status_icon} {step.step_name} ({step.duration_ms:.0f}ms)")
            if step.error:
                print(f"      Error: {step.error}")
        
        # Print session metrics
        metrics = session.get_metrics()
        print(f"\n Session Metrics:")
        print(f"  Total Events: {metrics.total_events}")
        print(f"  Errors: {metrics.errors}")
        print(f"  Success Rate: {metrics.success_rate:.1%}")
        
        await context.close()
        await browser.close()
    
    print("\n" + "=" * 60)
    print(" E2E testing complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
