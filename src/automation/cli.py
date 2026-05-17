"""One-click test deployment script"""

import asyncio
import json
from typing import Dict, Any, Optional
import typer
from playwright.async_api import async_playwright
from src.automation import CustomerEnvironmentAdapter, BulkEnvironmentSetup, AuthMethod

app = typer.Typer()


@app.command()
def setup_environment(
    env_name: str = typer.Argument(..., help="Environment name"),
    url: str = typer.Option(..., "--url", "-u", help="Application URL"),
    auth_method: str = typer.Option("basic", "--auth", "-a", help="Authentication method"),
    username: Optional[str] = typer.Option(None, "--username"),
    password: Optional[str] = typer.Option(None, "--password"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Config file to save"),
):
    """Set up a customer environment"""
    
    async def setup():
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()
            
            adapter = CustomerEnvironmentAdapter(page)
            
            # Configure authentication
            auth_config = {"username": username, "password": password}
            success = await adapter.configure_auth(AuthMethod(auth_method), **auth_config)
            
            if success:
                # Get environment info
                info = await adapter.get_environment_info()
                
                typer.echo(" Environment setup successful!")
                typer.echo(json.dumps(info, indent=2))
                
                # Save config if requested
                if config_file:
                    config = {
                        "env_name": env_name,
                        "url": url,
                        "auth_method": auth_method,
                        "info": info
                    }
                    with open(config_file, "w") as f:
                        json.dump(config, f, indent=2)
                    typer.echo(f"\nConfig saved to {config_file}")
            else:
                typer.echo(" Environment setup failed!")
            
            await context.close()
            await browser.close()
    
    asyncio.run(setup())


@app.command()
def bulk_deploy(
    config_file: str = typer.Argument(..., help="Bulk configuration file"),
):
    """Deploy to multiple environments"""
    
    async def deploy():
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
            
            setup = BulkEnvironmentSetup()
            
            # Register environments
            for env_config in config.get("environments", []):
                await setup.register_environment(
                    env_config["name"],
                    env_config["url"],
                    AuthMethod(env_config.get("auth_method", "basic")),
                    **env_config.get("credentials", {})
                )
            
            # Deploy
            typer.echo("Starting bulk deployment...")
            results = await setup.deploy_to_all(config.get("deployment", {}))
            
            # Report results
            typer.echo("\nDeployment Results:")
            for env, success in results.items():
                status = " Success" if success else " Failed"
                typer.echo(f"  {env}: {status}")
            
            status = setup.get_status()
            typer.echo(f"\nTotal environments: {status['total']}")
        
        except Exception as e:
            typer.echo(f" Error: {str(e)}", err=True)
    
    asyncio.run(deploy())


@app.command()
def validate_language(
    url: str = typer.Option(..., "--url", "-u", help="Application URL"),
    language: str = typer.Option("en", "--language", "-l", help="Language code"),
):
    """Test language switching"""
    
    async def test():
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()
            
            adapter = CustomerEnvironmentAdapter(page)
            
            # Navigate to URL
            await page.goto(url)
            
            # Try to switch language
            from src.automation import LanguageCode
            success = await adapter.set_language(LanguageCode(language))
            
            if success:
                typer.echo(f" Language switched to {language}")
                title = await page.title()
                typer.echo(f"Page title: {title}")
            else:
                typer.echo(f" Could not switch to language: {language}")
            
            await context.close()
            await browser.close()
    
    asyncio.run(test())


def main():
    app()


if __name__ == "__main__":
    main()
