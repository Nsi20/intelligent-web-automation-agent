"""Intelligent Web Automation Agent - Main CLI Application."""
import asyncio
import typer
from rich.console import Console
from rich.table import Table
from typing import Optional

from config.settings import settings
from src.orchestrator.tasks.job_board_monitor import IndeedJobMonitor
from src.browser.automation import BrowserAutomation
from src.llm.client import LLMClient
from src.utils.logger import logger

app = typer.Typer(
    name="web-agent",
    help="Intelligent Web Automation Agent with LLM-powered decision making",
    add_completion=False
)
console = Console()


@app.command()
def monitor_jobs(
    keywords: Optional[str] = typer.Option(None, "--keywords", "-k", help="Job search keywords"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Job location"),
    filter_criteria: Optional[str] = typer.Option(None, "--filter", "-f", help="LLM filtering criteria"),
    no_email: bool = typer.Option(False, "--no-email", help="Disable email notifications"),
):
    """Monitor Indeed job board for new listings."""
    console.print("\n[bold blue]🤖 Starting Intelligent Job Monitor[/bold blue]\n")
    
    async def run():
        monitor = IndeedJobMonitor()
        results = await monitor.run(
            keywords=keywords,
            location=location,
            filter_criteria=filter_criteria,
            send_email=not no_email
        )
        
        # Display results
        console.print(f"\n[green]✓[/green] Found {len(results['jobs'])} total jobs")
        console.print(f"[green]✓[/green] {len(results['new_jobs'])} new jobs after filtering\n")
        
        if results['new_jobs']:
            table = Table(title="New Job Listings")
            table.add_column("Title", style="cyan")
            table.add_column("Company", style="magenta")
            table.add_column("Location", style="green")
            table.add_column("Type", style="yellow")
            
            for job in results['new_jobs'][:10]:  # Show first 10
                table.add_row(
                    job.get('title', 'N/A'),
                    job.get('company', 'N/A'),
                    job.get('location', 'N/A'),
                    job.get('job_type', 'N/A')
                )
            
            console.print(table)
            console.print(f"\n[bold]Summary:[/bold]\n{results['summary']}\n")
        else:
            console.print("[yellow]No new jobs found.[/yellow]\n")
    
    asyncio.run(run())


@app.command()
def test_browser(
    url: str = typer.Option("https://example.com", "--url", "-u", help="URL to test"),
    headed: bool = typer.Option(False, "--headed", help="Run in headed mode (visible browser)"),
):
    """Test browser automation functionality."""
    console.print(f"\n[bold blue]🌐 Testing Browser Automation[/bold blue]\n")
    console.print(f"URL: {url}")
    console.print(f"Mode: {'Headed' if headed else 'Headless'}\n")
    
    async def run():
        async with BrowserAutomation(headless=not headed) as browser:
            await browser.navigate(url)
            console.print("[green]✓[/green] Navigation successful")
            
            title = await browser.evaluate("document.title")
            console.print(f"[green]✓[/green] Page title: {title}")
            
            screenshot_path = await browser.screenshot()
            console.print(f"[green]✓[/green] Screenshot saved: {screenshot_path}\n")
    
    asyncio.run(run())


@app.command()
def test_llm(
    prompt: str = typer.Option("What is web automation?", "--prompt", "-p", help="Test prompt"),
):
    """Test LLM integration."""
    console.print("\n[bold blue]🧠 Testing LLM Integration[/bold blue]\n")
    console.print(f"Prompt: {prompt}\n")
    
    llm = LLMClient()
    response = llm.chat(prompt)
    
    console.print("[bold]Response:[/bold]")
    console.print(response)
    console.print()


@app.command()
def config_check():
    """Check configuration and display settings."""
    console.print("\n[bold blue]⚙️  Configuration Check[/bold blue]\n")
    
    table = Table(title="Current Settings")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Groq API Key", "✓ Configured" if settings.groq_api_key else "✗ Missing")
    table.add_row("Email Enabled", str(settings.email_enabled))
    table.add_row("Browser Headless", str(settings.browser_headless))
    table.add_row("Job Keywords", settings.job_search_keywords)
    table.add_row("Job Location", settings.job_location)
    table.add_row("Data Directory", str(settings.data_dir))
    table.add_row("Logs Directory", str(settings.logs_dir))
    
    console.print(table)
    console.print()


@app.command()
def show_jobs(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of jobs to show"),
):
    """Show stored job listings."""
    from src.utils.storage import JobStorage
    
    console.print("\n[bold blue]📋 Stored Job Listings[/bold blue]\n")
    
    storage = JobStorage()
    latest = storage.get_latest_jobs()
    
    if not latest:
        console.print("[yellow]No jobs stored yet. Run 'monitor-jobs' first.[/yellow]\n")
        return
    
    jobs = latest.get('jobs', [])
    console.print(f"Last run: {latest.get('timestamp', 'Unknown')}")
    console.print(f"Keywords: {latest.get('keywords', 'Unknown')}")
    console.print(f"Total jobs: {len(jobs)}\n")
    
    if jobs:
        table = Table(title=f"Latest {min(limit, len(jobs))} Jobs")
        table.add_column("Title", style="cyan")
        table.add_column("Company", style="magenta")
        table.add_column("Location", style="green")
        
        for job in jobs[:limit]:
            table.add_row(
                job.get('title', 'N/A'),
                job.get('company', 'N/A'),
                job.get('location', 'N/A')
            )
        
        console.print(table)
    console.print()


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()

