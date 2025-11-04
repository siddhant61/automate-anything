"""
Command-line interface for OpenHPI automation tasks.
"""

import typer
from rich.console import Console
from rich.table import Table

from src.core.config import settings
from src.models.database import init_db

app = typer.Typer(
    name="openhpi",
    help="OpenHPI Automation CLI - Manage courses, users, and analytics",
    add_completion=False,
)

console = Console()


@app.command()
def init():
    """Initialize the database and create necessary directories."""
    console.print("[bold blue]Initializing OpenHPI Automation...[/bold blue]")
    
    # Initialize database
    init_db()
    console.print("✓ Database initialized", style="green")
    
    # Verify configuration
    console.print("✓ Configuration loaded", style="green")
    console.print(f"  Environment: {settings.env}", style="dim")
    console.print(f"  Database: {settings.database_url}", style="dim")
    
    console.print("\n[bold green]Initialization complete![/bold green]")
    console.print("\nNext steps:")
    console.print("  1. Configure your .env file with credentials")
    console.print("  2. Run 'openhpi scrape courses' to fetch course data")
    console.print("  3. Run 'openhpi serve' to start the API server")


@app.command()
def config():
    """Display current configuration (without sensitive values)."""
    table = Table(title="OpenHPI Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    
    # Non-sensitive settings only
    table.add_row("Environment", settings.env)
    table.add_row("Debug Mode", str(settings.debug))
    table.add_row("Log Level", settings.log_level)
    table.add_row("API Host", settings.api_host)
    table.add_row("API Port", str(settings.api_port))
    table.add_row("Database URL", settings.database_url)
    table.add_row("Data Directory", str(settings.data_dir))
    table.add_row("Reports Directory", str(settings.reports_dir))
    
    console.print(table)


@app.command()
def serve(
    host: str = typer.Option(None, help="API server host"),
    port: int = typer.Option(None, help="API server port"),
    reload: bool = typer.Option(False, help="Enable auto-reload"),
):
    """Start the FastAPI server."""
    import uvicorn
    
    console.print("[bold blue]Starting OpenHPI Automation API...[/bold blue]")
    
    uvicorn.run(
        "src.main:app",
        host=host or settings.api_host,
        port=port or settings.api_port,
        reload=reload or settings.debug,
        workers=1 if reload or settings.debug else settings.api_workers,
    )


# Placeholder commands for future implementation
scrape_app = typer.Typer(help="Data scraping commands")
app.add_typer(scrape_app, name="scrape")


@scrape_app.command("courses")
def scrape_courses_cmd():
    """Scrape course data from OpenHPI."""
    from src.models.database import SessionLocal
    from src.services.scraping_service import scrape_courses
    
    console.print("[bold blue]Starting course scraping...[/bold blue]")
    
    db = SessionLocal()
    try:
        result = scrape_courses(db)
        
        console.print(f"\n[bold green]✓ Scraping completed successfully![/bold green]")
        console.print(f"  Courses scraped: {result['courses_scraped']}")
        console.print(f"  Courses saved: {result['courses_saved']}")
        console.print(f"  Job ID: {result['job_id']}")
        
    except Exception as e:
        console.print(f"[bold red]✗ Scraping failed: {e}[/bold red]")
        raise typer.Exit(1)
    finally:
        db.close()


@scrape_app.command("dashboard")
def scrape_dashboard():
    """Scrape dashboard statistics."""
    console.print("[yellow]This command will be implemented in Phase 3[/yellow]")


@scrape_app.command("helpdesk")
def scrape_helpdesk():
    """Scrape helpdesk tickets."""
    console.print("[yellow]This command will be implemented in Phase 3[/yellow]")


# Analytics commands
analytics_app = typer.Typer(help="Analytics and reporting commands")
app.add_typer(analytics_app, name="analytics")


@analytics_app.command("course")
def analyze_course(course_id: str):
    """Analyze course statistics."""
    console.print(f"[yellow]Course analysis for {course_id} - Coming in Phase 4[/yellow]")


@analytics_app.command("annual")
def analyze_annual(year: int):
    """Generate annual statistics report."""
    console.print(f"[yellow]Annual report for {year} - Coming in Phase 4[/yellow]")


# Automation commands
automation_app = typer.Typer(help="Automation tasks")
app.add_typer(automation_app, name="automate")


@automation_app.command("enroll")
def batch_enroll(course_id: str, users_file: str):
    """Batch enroll users in a course."""
    console.print(f"[yellow]Batch enrollment - Coming in Phase 5[/yellow]")


@automation_app.command("notify")
def send_notifications():
    """Send helpdesk notifications."""
    console.print("[yellow]Notifications - Coming in Phase 5[/yellow]")


if __name__ == "__main__":
    app()
