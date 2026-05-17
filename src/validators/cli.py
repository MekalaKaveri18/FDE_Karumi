"""CLI for Configuration Validator"""

import asyncio
import json
from typing import Optional
import typer
from src.validators import ConfigurationValidator

app = typer.Typer()


@app.command()
def validate(
    url: str = typer.Argument(..., help="Target application URL"),
    username: Optional[str] = typer.Option(None, "--username", "-u", help="Test username"),
    password: Optional[str] = typer.Option(None, "--password", "-p", help="Test password"),
    headless: bool = typer.Option(True, "--headless/--no-headless", help="Run browser in headless mode"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """Validate a SaaS application for agent compatibility"""
    
    validator = ConfigurationValidator(headless=headless)
    report = asyncio.run(validator.validate_app(url, username, password))
    
    # Convert report to dict for serialization
    report_dict = {
        "url": report.url,
        "status": report.status,
        "timestamp": report.timestamp,
        "checks": [
            {
                "name": check.check_name,
                "passed": check.passed,
                "message": check.message,
                "details": check.details
            }
            for check in report.checks
        ],
        "edge_cases": report.edge_cases,
        "recommendations": report.recommendations
    }
    
    # Print to console
    typer.echo(json.dumps(report_dict, indent=2))
    
    # Save to file if specified
    if output:
        with open(output, "w") as f:
            json.dump(report_dict, f, indent=2)
        typer.echo(f"\nReport saved to {output}")


def main():
    app()


if __name__ == "__main__":
    main()
