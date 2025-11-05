"""
Tests for CLI commands.
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
from typer.testing import CliRunner

from src.cli import app


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


class TestCLICommands:
    """Test CLI command functionality."""

    @patch('src.cli.init_db')
    def test_init_command(self, mock_init_db, runner):
        """Test init command."""
        result = runner.invoke(app, ['init'])
        
        assert result.exit_code == 0
        assert 'Initializing OpenHPI Automation' in result.stdout
        assert 'Database initialized' in result.stdout
        assert 'Configuration loaded' in result.stdout
        mock_init_db.assert_called_once()

    @patch('src.cli.settings')
    def test_config_command(self, mock_settings, runner):
        """Test config command."""
        mock_settings.env = 'development'
        mock_settings.debug = True
        mock_settings.log_level = 'INFO'
        mock_settings.api_host = 'localhost'
        mock_settings.api_port = 8000
        mock_settings.database_url = 'sqlite:///test.db'
        mock_settings.data_dir = '/data'
        mock_settings.reports_dir = '/reports'
        
        result = runner.invoke(app, ['config'])
        
        assert result.exit_code == 0
        assert 'OpenHPI Configuration' in result.stdout
        assert 'development' in result.stdout
        assert 'localhost' in result.stdout

    def test_serve_command_default(self, runner):
        """Test serve command with defaults."""
        # Import uvicorn inside the function to mock it
        with patch('uvicorn.run') as mock_uvicorn_run:
            with patch('src.cli.settings') as mock_settings:
                mock_settings.api_host = 'localhost'
                mock_settings.api_port = 8000
                mock_settings.debug = False
                mock_settings.api_workers = 4
                
                result = runner.invoke(app, ['serve'])
                
                assert result.exit_code == 0
                assert 'Starting OpenHPI Automation API' in result.stdout
                mock_uvicorn_run.assert_called_once()

    def test_serve_command_with_options(self, runner):
        """Test serve command with custom options."""
        with patch('uvicorn.run') as mock_uvicorn_run:
            result = runner.invoke(app, ['serve', '--host', '0.0.0.0', '--port', '9000', '--reload'])
            
            assert result.exit_code == 0
            mock_uvicorn_run.assert_called_once()
            
            # Check that custom host and port were used
            call_kwargs = mock_uvicorn_run.call_args[1]
            assert call_kwargs['host'] == '0.0.0.0'
            assert call_kwargs['port'] == 9000
            assert call_kwargs['reload'] is True

    def test_scrape_courses_command(self, runner):
        """Test scrape courses command."""
        with patch('src.services.scraping_service.scrape_courses') as mock_scrape:
            with patch('src.models.database.SessionLocal') as mock_session_local:
                mock_db = Mock()
                mock_session_local.return_value = mock_db
                
                mock_scrape.return_value = {
                    'courses_scraped': 25,
                    'courses_saved': 25,
                    'job_id': 1
                }
                
                result = runner.invoke(app, ['scrape', 'courses'])
                
                assert result.exit_code == 0
                assert 'Starting course scraping' in result.stdout
                assert 'Scraping completed successfully' in result.stdout
                assert '25' in result.stdout
                mock_scrape.assert_called_once_with(mock_db)
                mock_db.close.assert_called_once()

    def test_scrape_courses_command_error(self, runner):
        """Test scrape courses command with error."""
        with patch('src.services.scraping_service.scrape_courses') as mock_scrape:
            with patch('src.models.database.SessionLocal') as mock_session_local:
                mock_db = Mock()
                mock_session_local.return_value = mock_db
                
                mock_scrape.side_effect = Exception("Scraping failed")
                
                result = runner.invoke(app, ['scrape', 'courses'])
                
                # Command should handle error gracefully
                assert 'Starting course scraping' in result.stdout
                mock_db.close.assert_called_once()


class TestCLIHelp:
    """Test CLI help and documentation."""

    def test_app_help(self, runner):
        """Test main app help."""
        result = runner.invoke(app, ['--help'])
        
        assert result.exit_code == 0
        assert 'OpenHPI Automation CLI' in result.stdout
        assert 'init' in result.stdout
        assert 'config' in result.stdout
        assert 'serve' in result.stdout
        assert 'scrape' in result.stdout

    def test_init_help(self, runner):
        """Test init command help."""
        result = runner.invoke(app, ['init', '--help'])
        
        assert result.exit_code == 0
        assert 'Initialize' in result.stdout or 'init' in result.stdout

    def test_serve_help(self, runner):
        """Test serve command help."""
        result = runner.invoke(app, ['serve', '--help'])
        
        assert result.exit_code == 0
        assert 'FastAPI' in result.stdout or 'server' in result.stdout

    def test_scrape_help(self, runner):
        """Test scrape command help."""
        result = runner.invoke(app, ['scrape', '--help'])
        
        assert result.exit_code == 0
        assert 'scraping' in result.stdout.lower() or 'courses' in result.stdout.lower()
