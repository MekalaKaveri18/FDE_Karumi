"""CLI for Testing Harness"""

import asyncio
import json
import typer
from playwright.async_api import async_playwright
from src.testing import TestingHarness, create_sample_scenario

app = typer.Typer()


@app.command()
def run_scenario(
    url: str = typer.Argument(..., help="Application URL to test"),
    scenario_name: str = typer.Option("Default Scenario", "--scenario", "-s", help="Name of test scenario"),
    headless: bool = typer.Option(True, "--headless/--no-headless", help="Run browser in headless mode"),
    output: str = typer.Option("test_results.json", "--output", "-o", help="Output file path"),
):
    """Run a test scenario against a SaaS application"""
    
    async def main():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            context = await browser.new_context()
            page = await context.new_page()
            
            harness = TestingHarness(page, headless=headless)
            
            # Create sample scenario
            steps = await create_sample_scenario()
            
            # Run scenario
            result = await harness.run_scenario(scenario_name, steps)
            
            # Convert to dict for serialization
            result_dict = {
                "scenario": result.scenario_name,
                "overall_status": result.overall_status.value,
                "duration_ms": result.duration_ms,
                "timestamp": result.timestamp,
                "steps": [
                    {
                        "name": step.step_name,
                        "status": step.status.value,
                        "duration_ms": step.duration_ms,
                        "error": step.error,
                        "screenshot": step.screenshot_path,
                        "details": step.details
                    }
                    for step in result.steps
                ],
                "conversation_flow": result.conversation_flow
            }
            
            # Print results
            typer.echo(json.dumps(result_dict, indent=2))
            
            # Save to file
            with open(output, "w") as f:
                json.dump(result_dict, f, indent=2)
            typer.echo(f"\nResults saved to {output}")
            
            await context.close()
            await browser.close()
    
    asyncio.run(main())


def main():
    app()


if __name__ == "__main__":
    main()
