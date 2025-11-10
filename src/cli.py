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
    console.print(f"  Database: {settings.get_database_url_safe()}", style="dim")
    
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
    table.add_row("Database URL", settings.get_database_url_safe())
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
def analyze_course(
    years: str = typer.Option(None, help="Comma-separated years to analyze"),
    categories: str = typer.Option(None, help="Comma-separated categories (e.g., Java,Python)")
):
    """Analyze course statistics."""
    from src.models.database import SessionLocal
    from src.analysis import course_analytics
    
    console.print("[bold blue]Analyzing course metrics...[/bold blue]")
    
    db = SessionLocal()
    try:
        # Parse parameters
        year_list = [int(y.strip()) for y in years.split(',')] if years else None
        category_list = [c.strip() for c in categories.split(',')] if categories else None
        
        # Get data
        data = course_analytics.prepare_visualization_data(
            db=db,
            years=year_list,
            categories=category_list
        )
        
        console.print("\n[bold green]✓ Analysis completed![/bold green]")
        
        # Display summary
        if not data['enrollment_filtered'].empty:
            console.print(f"  Total enrollments: {len(data['enrollment_filtered'])}")
        
        if 'certificates' in data and hasattr(data['certificates'], '__len__'):
            total_certs = sum(data['certificates'].values()) if hasattr(data['certificates'], 'values') else 0
            console.print(f"  Total certificates: {total_certs}")
        
    except Exception as e:
        console.print(f"[bold red]✗ Analysis failed: {e}[/bold red]")
        raise typer.Exit(1)
    finally:
        db.close()


@analytics_app.command("annual")
def analyze_annual(year: int = typer.Argument(..., help="Year to generate report for")):
    """Generate annual statistics report."""
    from src.models.database import SessionLocal
    from src.analysis import annual_stats
    
    console.print(f"[bold blue]Generating annual report for {year}...[/bold blue]")
    
    db = SessionLocal()
    try:
        report = annual_stats.generate_annual_report(db=db, year=year)
        
        console.print("\n[bold green]✓ Report generated![/bold green]")
        
        # Display metrics
        metrics = report['metrics']
        table = Table(title=f"Annual Metrics - {year}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Total Enrollments", str(metrics['total_enrollments']))
        table.add_row("German Enrollments", str(metrics['german_enrollments']))
        table.add_row("English Enrollments", str(metrics['english_enrollments']))
        table.add_row("Total Certificates", str(metrics['total_certificates']))
        table.add_row("Overall Completion Rate", f"{metrics['overall_completion_rate']}%")
        table.add_row("German Completion Rate", f"{metrics['german_completion_rate']}%")
        table.add_row("English Completion Rate", f"{metrics['english_completion_rate']}%")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]✗ Report generation failed: {e}[/bold red]")
        raise typer.Exit(1)
    finally:
        db.close()


# Automation commands
automation_app = typer.Typer(help="Automation tasks")
app.add_typer(automation_app, name="automate")


@automation_app.command("enroll")
def batch_enroll(
    course_id: str = typer.Argument(..., help="Course ID to enroll users in"),
    users_file: str = typer.Argument(..., help="CSV file with user emails"),
    headless: bool = typer.Option(True, help="Run browser in headless mode")
):
    """Batch enroll users in a course from CSV file."""
    import pandas as pd
    from src.services.automation_service import automation_service
    
    console.print(f"[bold blue]Starting batch enrollment for course: {course_id}[/bold blue]")
    
    try:
        # Read users from CSV
        df = pd.read_csv(users_file)
        if 'email' not in df.columns:
            console.print("[red]Error: CSV must have 'email' column[/red]")
            raise typer.Exit(1)
        
        users = df['email'].tolist()
        console.print(f"Found {len(users)} users to enroll")
        
        # Perform enrollment
        result = automation_service.batch_enroll_users(
            users=users,
            course_id=course_id,
            headless=headless
        )
        
        # Display results
        console.print(f"\n[bold green]✓ Enrollment completed![/bold green]")
        console.print(f"  Enrolled: {len(result['enrolled'])}")
        console.print(f"  Unregistered: {len(result['unregistered'])}")
        
        if result['unregistered']:
            console.print("\n[yellow]Unregistered users:[/yellow]")
            for email in result['unregistered']:
                console.print(f"  - {email}")
        
    except Exception as e:
        console.print(f"[bold red]✗ Enrollment failed: {e}[/bold red]")
        raise typer.Exit(1)


@automation_app.command("notify-helpdesk")
def notify_helpdesk():
    """Check helpdesk tickets and send notifications."""
    from src.services.automation_service import automation_service
    
    console.print("[bold blue]Checking helpdesk tickets...[/bold blue]")
    
    try:
        result = automation_service.check_and_notify_helpdesk(headless=True)
        
        console.print(f"\n[bold green]✓ Helpdesk check completed![/bold green]")
        console.print(f"  Total tickets: {result['tickets_count']}")
        console.print(f"  Telegram notification: {'Sent' if result['notification_sent'] else 'Failed/Skipped'}")
        console.print(f"  Email notification: {'Sent' if result['email_sent'] else 'Failed/Skipped'}")
        
        # Display analysis
        analysis = result['analysis']
        console.print("\n[cyan]Ticket Analysis:[/cyan]")
        console.print(f"  Within 6 hours: {analysis['within_6hrs']}")
        console.print(f"  Within 12 hours: {analysis['within_12hrs']}")
        console.print(f"  Within 24 hours: {analysis['within_24hrs']}")
        console.print(f"  Within 48 hours: {analysis['within_48hrs']}")
        
    except Exception as e:
        console.print(f"[bold red]✗ Helpdesk check failed: {e}[/bold red]")
        raise typer.Exit(1)


@automation_app.command("update-page")
def update_page(
    page_name: str = typer.Argument(..., help="Name of the page to update"),
    content_file: str = typer.Argument(..., help="File containing new page content"),
    headless: bool = typer.Option(True, help="Run browser in headless mode")
):
    """Update page content on OpenHPI platform."""
    from src.services.automation_service import automation_service
    
    console.print(f"[bold blue]Updating page: {page_name}[/bold blue]")
    
    try:
        # Read content from file
        with open(content_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update page
        success = automation_service.update_page(
            page_name=page_name,
            content=content,
            headless=headless
        )
        
        if success:
            console.print(f"[bold green]✓ Page '{page_name}' updated successfully![/bold green]")
        else:
            console.print(f"[bold red]✗ Failed to update page[/bold red]")
            raise typer.Exit(1)
        
    except FileNotFoundError:
        console.print(f"[red]Error: Content file '{content_file}' not found[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]✗ Page update failed: {e}[/bold red]")
        raise typer.Exit(1)


# Course management commands
course_app = typer.Typer(help="Course management commands")
app.add_typer(course_app, name="course")


@course_app.command("parse")
def parse_course(
    input_file: str = typer.Argument(..., help="JSON file with EdX course data"),
    org: str = typer.Option("HPI", help="Organization identifier"),
    course_id: str = typer.Option("course", help="Course identifier"),
    url_name: str = typer.Option("2024", help="URL name for the course")
):
    """Parse EdX course data and generate OpenHPI structure."""
    import json
    from src.services.course_parser_service import course_parser_service
    
    console.print(f"[bold blue]Parsing course from: {input_file}[/bold blue]")
    
    try:
        # Read course data
        with open(input_file, 'r') as f:
            course_data = json.load(f)
        
        # Parse course
        result = course_parser_service.parse_course_structure(
            course_data=course_data,
            output_dir=str(settings.exports_dir / "course_exports"),
            org=org,
            course_id=course_id,
            url_name=url_name
        )
        
        console.print(f"\n[bold green]✓ Course parsed successfully![/bold green]")
        console.print(f"  Output: {result['tar_path']}")
        console.print(f"  Chapters: {result['chapters']}")
        console.print(f"  Sequentials: {result['sequentials']}")
        console.print(f"  Verticals: {result['verticals']}")
        
    except FileNotFoundError:
        console.print(f"[red]Error: Input file '{input_file}' not found[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]✗ Course parsing failed: {e}[/bold red]")
        raise typer.Exit(1)


# User analysis commands
user_app = typer.Typer(help="User analysis commands")
app.add_typer(user_app, name="users")


@user_app.command("find-teachers")
def find_teachers(
    survey_ids: str = typer.Option(None, help="Comma-separated survey IDs"),
    output: str = typer.Option(None, help="Output CSV file path")
):
    """Find users who identified as teachers in surveys."""
    from src.models.database import SessionLocal
    from src.analysis import user_analysis
    
    console.print("[bold blue]Finding teacher users...[/bold blue]")
    
    db = SessionLocal()
    try:
        survey_id_list = [s.strip() for s in survey_ids.split(',')] if survey_ids else None
        
        df = user_analysis.find_teacher_users(
            db=db,
            survey_ids=survey_id_list
        )
        
        console.print(f"\n[bold green]✓ Found {len(df)} teacher users![/bold green]")
        
        if output:
            df.to_csv(output, index=False)
            console.print(f"  Results saved to: {output}")
        else:
            # Display first 10 rows
            console.print("\nFirst 10 teachers:")
            console.print(df.head(10).to_string())
        
    except Exception as e:
        console.print(f"[bold red]✗ Teacher search failed: {e}[/bold red]")
        raise typer.Exit(1)
    finally:
        db.close()


# Dashboard command
@app.command("dashboard")
def run_dashboard(
    port: int = typer.Option(8501, help="Port to run dashboard on"),
    api_url: str = typer.Option("http://localhost:8000", help="API base URL")
):
    """Launch the Streamlit dashboard."""
    import subprocess
    import os
    
    console.print("[bold blue]Starting OpenHPI Dashboard...[/bold blue]")
    console.print(f"  Dashboard will be available at: http://localhost:{port}")
    console.print(f"  Connecting to API at: {api_url}")
    
    # Set environment variable for API URL
    env = os.environ.copy()
    env['API_BASE_URL'] = api_url
    
    try:
        subprocess.run([
            "streamlit", "run",
            "src/dashboard.py",
            "--server.port", str(port),
            "--server.address", "0.0.0.0"
        ], env=env)
    except KeyboardInterrupt:
        console.print("\n[yellow]Dashboard stopped[/yellow]")
    except Exception as e:
        console.print(f"[bold red]✗ Failed to start dashboard: {e}[/bold red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
