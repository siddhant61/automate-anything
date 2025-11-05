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


class TestScrapingCommands:
    """Test scraping subcommands."""

    def test_scrape_dashboard_command(self, runner):
        """Test scrape dashboard command (not implemented)."""
        result = runner.invoke(app, ['scrape', 'dashboard'])
        
        assert result.exit_code == 0
        assert 'Phase 3' in result.stdout or 'implemented' in result.stdout

    def test_scrape_helpdesk_command(self, runner):
        """Test scrape helpdesk command (not implemented)."""
        result = runner.invoke(app, ['scrape', 'helpdesk'])
        
        assert result.exit_code == 0
        assert 'Phase 3' in result.stdout or 'implemented' in result.stdout


class TestAnalyticsCommands:
    """Test analytics subcommands."""

    def test_analytics_course_command_success(self, runner):
        """Test analytics course command with valid data."""
        with patch('src.models.database.SessionLocal') as mock_session_local:
            with patch('src.analysis.course_analytics.prepare_visualization_data') as mock_prepare:
                import pandas as pd
                
                mock_db = Mock()
                mock_session_local.return_value = mock_db
                
                # Mock return data
                mock_prepare.return_value = {
                    'enrollment_filtered': pd.DataFrame({'id': [1, 2, 3]}),
                    'certificates': {'CoD': 10, 'RoA': 5}
                }
                
                result = runner.invoke(app, ['analytics', 'course'])
                
                assert result.exit_code == 0
                assert 'Analyzing course metrics' in result.stdout
                assert 'Analysis completed' in result.stdout
                mock_db.close.assert_called_once()

    def test_analytics_course_command_with_params(self, runner):
        """Test analytics course command with year and category filters."""
        with patch('src.models.database.SessionLocal') as mock_session_local:
            with patch('src.analysis.course_analytics.prepare_visualization_data') as mock_prepare:
                import pandas as pd
                
                mock_db = Mock()
                mock_session_local.return_value = mock_db
                
                mock_prepare.return_value = {
                    'enrollment_filtered': pd.DataFrame({'id': [1]}),
                    'certificates': {}
                }
                
                result = runner.invoke(app, ['analytics', 'course', '--years', '2023,2024', '--categories', 'Java,Python'])
                
                assert result.exit_code == 0
                assert 'Analyzing course metrics' in result.stdout
                mock_db.close.assert_called_once()
                
                # Verify parameters were parsed correctly
                call_args = mock_prepare.call_args
                assert call_args[1]['years'] == [2023, 2024]
                assert call_args[1]['categories'] == ['Java', 'Python']

    def test_analytics_course_command_error(self, runner):
        """Test analytics course command with error."""
        with patch('src.models.database.SessionLocal') as mock_session_local:
            with patch('src.analysis.course_analytics.prepare_visualization_data') as mock_prepare:
                mock_db = Mock()
                mock_session_local.return_value = mock_db
                
                mock_prepare.side_effect = Exception("Analysis failed")
                
                result = runner.invoke(app, ['analytics', 'course'])
                
                assert result.exit_code == 1
                assert 'Analysis failed' in result.stdout
                mock_db.close.assert_called_once()

    def test_analytics_annual_command_success(self, runner):
        """Test analytics annual command."""
        with patch('src.models.database.SessionLocal') as mock_session_local:
            with patch('src.analysis.annual_stats.generate_annual_report') as mock_generate:
                mock_db = Mock()
                mock_session_local.return_value = mock_db
                
                mock_generate.return_value = {
                    'metrics': {
                        'total_enrollments': 1000,
                        'german_enrollments': 600,
                        'english_enrollments': 400,
                        'total_certificates': 500,
                        'overall_completion_rate': 50.0,
                        'german_completion_rate': 55.0,
                        'english_completion_rate': 45.0
                    }
                }
                
                result = runner.invoke(app, ['analytics', 'annual', '2023'])
                
                assert result.exit_code == 0
                assert 'Generating annual report for 2023' in result.stdout
                assert 'Report generated' in result.stdout
                assert '1000' in result.stdout
                mock_db.close.assert_called_once()

    def test_analytics_annual_command_error(self, runner):
        """Test analytics annual command with error."""
        with patch('src.models.database.SessionLocal') as mock_session_local:
            with patch('src.analysis.annual_stats.generate_annual_report') as mock_generate:
                mock_db = Mock()
                mock_session_local.return_value = mock_db
                
                mock_generate.side_effect = Exception("Report generation failed")
                
                result = runner.invoke(app, ['analytics', 'annual', '2023'])
                
                assert result.exit_code == 1
                assert 'Report generation failed' in result.stdout
                mock_db.close.assert_called_once()


class TestAutomationCommands:
    """Test automation subcommands."""

    def test_automate_enroll_command_success(self, runner):
        """Test batch enroll command."""
        import tempfile
        import os
        
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('email\n')
            f.write('user1@example.com\n')
            f.write('user2@example.com\n')
            temp_file = f.name
        
        try:
            with patch('src.services.automation_service.automation_service.batch_enroll_users') as mock_enroll:
                mock_enroll.return_value = {
                    'enrolled': ['user1@example.com', 'user2@example.com'],
                    'unregistered': []
                }
                
                result = runner.invoke(app, ['automate', 'enroll', 'course123', temp_file])
                
                assert result.exit_code == 0
                assert 'Starting batch enrollment' in result.stdout
                assert 'Enrollment completed' in result.stdout
                assert 'Found 2 users' in result.stdout
        finally:
            os.unlink(temp_file)

    def test_automate_enroll_command_missing_column(self, runner):
        """Test batch enroll command with missing email column."""
        import tempfile
        import os
        
        # Create a temporary CSV file without email column
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('name\n')
            f.write('John Doe\n')
            temp_file = f.name
        
        try:
            result = runner.invoke(app, ['automate', 'enroll', 'course123', temp_file])
            
            assert result.exit_code == 1
            assert 'email' in result.stdout.lower()
        finally:
            os.unlink(temp_file)

    def test_automate_enroll_command_with_unregistered(self, runner):
        """Test batch enroll command with unregistered users."""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('email\n')
            f.write('user1@example.com\n')
            f.write('user2@example.com\n')
            temp_file = f.name
        
        try:
            with patch('src.services.automation_service.automation_service.batch_enroll_users') as mock_enroll:
                mock_enroll.return_value = {
                    'enrolled': ['user1@example.com'],
                    'unregistered': ['user2@example.com']
                }
                
                result = runner.invoke(app, ['automate', 'enroll', 'course123', temp_file])
                
                assert result.exit_code == 0
                assert 'Unregistered users' in result.stdout
                assert 'user2@example.com' in result.stdout
        finally:
            os.unlink(temp_file)

    def test_automate_enroll_command_error(self, runner):
        """Test batch enroll command with error."""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('email\n')
            f.write('user1@example.com\n')
            temp_file = f.name
        
        try:
            with patch('src.services.automation_service.automation_service.batch_enroll_users') as mock_enroll:
                mock_enroll.side_effect = Exception("Enrollment failed")
                
                result = runner.invoke(app, ['automate', 'enroll', 'course123', temp_file])
                
                assert result.exit_code == 1
                assert 'Enrollment failed' in result.stdout
        finally:
            os.unlink(temp_file)

    def test_automate_notify_helpdesk_command_success(self, runner):
        """Test notify-helpdesk command."""
        with patch('src.services.automation_service.automation_service.check_and_notify_helpdesk') as mock_notify:
            mock_notify.return_value = {
                'tickets_count': 5,
                'notification_sent': True,
                'email_sent': True,
                'analysis': {
                    'within_6hrs': 2,
                    'within_12hrs': 3,
                    'within_24hrs': 4,
                    'within_48hrs': 5
                }
            }
            
            result = runner.invoke(app, ['automate', 'notify-helpdesk'])
            
            assert result.exit_code == 0
            assert 'Checking helpdesk tickets' in result.stdout
            assert 'Helpdesk check completed' in result.stdout
            assert '5' in result.stdout

    def test_automate_notify_helpdesk_command_error(self, runner):
        """Test notify-helpdesk command with error."""
        with patch('src.services.automation_service.automation_service.check_and_notify_helpdesk') as mock_notify:
            mock_notify.side_effect = Exception("Helpdesk check failed")
            
            result = runner.invoke(app, ['automate', 'notify-helpdesk'])
            
            assert result.exit_code == 1
            assert 'Helpdesk check failed' in result.stdout

    def test_automate_update_page_command_success(self, runner):
        """Test update-page command."""
        import tempfile
        import os
        
        # Create a temporary content file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write('<h1>New Content</h1>')
            temp_file = f.name
        
        try:
            with patch('src.services.automation_service.automation_service.update_page') as mock_update:
                mock_update.return_value = True
                
                result = runner.invoke(app, ['automate', 'update-page', 'test-page', temp_file])
                
                assert result.exit_code == 0
                assert 'Updating page: test-page' in result.stdout
                assert 'updated successfully' in result.stdout
        finally:
            os.unlink(temp_file)

    def test_automate_update_page_command_failure(self, runner):
        """Test update-page command with failure."""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write('<h1>New Content</h1>')
            temp_file = f.name
        
        try:
            with patch('src.services.automation_service.automation_service.update_page') as mock_update:
                mock_update.return_value = False
                
                result = runner.invoke(app, ['automate', 'update-page', 'test-page', temp_file])
                
                assert result.exit_code == 1
                assert 'Failed to update page' in result.stdout
        finally:
            os.unlink(temp_file)

    def test_automate_update_page_command_file_not_found(self, runner):
        """Test update-page command with missing file."""
        result = runner.invoke(app, ['automate', 'update-page', 'test-page', '/nonexistent/file.html'])
        
        assert result.exit_code == 1
        assert 'not found' in result.stdout


class TestCourseCommands:
    """Test course subcommands."""

    def test_course_parse_command_success(self, runner):
        """Test course parse command."""
        import tempfile
        import os
        import json
        
        # Create a temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'course': 'data'}, f)
            temp_file = f.name
        
        try:
            with patch('src.services.course_parser_service.course_parser_service.parse_course_structure') as mock_parse:
                mock_parse.return_value = {
                    'tar_path': '/path/to/course.tar.gz',
                    'chapters': 3,
                    'sequentials': 10,
                    'verticals': 25
                }
                
                result = runner.invoke(app, ['course', 'parse', temp_file])
                
                assert result.exit_code == 0
                assert 'Parsing course from' in result.stdout
                assert 'Course parsed successfully' in result.stdout
                assert '3' in result.stdout
        finally:
            os.unlink(temp_file)

    def test_course_parse_command_with_options(self, runner):
        """Test course parse command with custom options."""
        import tempfile
        import os
        import json
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'course': 'data'}, f)
            temp_file = f.name
        
        try:
            with patch('src.services.course_parser_service.course_parser_service.parse_course_structure') as mock_parse:
                mock_parse.return_value = {
                    'tar_path': '/path/to/course.tar.gz',
                    'chapters': 2,
                    'sequentials': 5,
                    'verticals': 15
                }
                
                result = runner.invoke(app, [
                    'course', 'parse', temp_file,
                    '--org', 'TestOrg',
                    '--course-id', 'test123',
                    '--url-name', '2025'
                ])
                
                assert result.exit_code == 0
                assert 'Course parsed successfully' in result.stdout
        finally:
            os.unlink(temp_file)

    def test_course_parse_command_file_not_found(self, runner):
        """Test course parse command with missing file."""
        result = runner.invoke(app, ['course', 'parse', '/nonexistent/file.json'])
        
        assert result.exit_code == 1
        assert 'not found' in result.stdout

    def test_course_parse_command_error(self, runner):
        """Test course parse command with error."""
        import tempfile
        import os
        import json
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'course': 'data'}, f)
            temp_file = f.name
        
        try:
            with patch('src.services.course_parser_service.course_parser_service.parse_course_structure') as mock_parse:
                mock_parse.side_effect = Exception("Parsing failed")
                
                result = runner.invoke(app, ['course', 'parse', temp_file])
                
                assert result.exit_code == 1
                assert 'Course parsing failed' in result.stdout
        finally:
            os.unlink(temp_file)


class TestUserCommands:
    """Test user subcommands."""

    def test_users_find_teachers_command_success(self, runner):
        """Test find-teachers command."""
        import pandas as pd
        
        with patch('src.models.database.SessionLocal') as mock_session_local:
            with patch('src.analysis.user_analysis.find_teacher_users') as mock_find:
                mock_db = Mock()
                mock_session_local.return_value = mock_db
                
                # Mock return DataFrame
                mock_find.return_value = pd.DataFrame({
                    'email': ['teacher1@example.com', 'teacher2@example.com'],
                    'name': ['Teacher 1', 'Teacher 2']
                })
                
                result = runner.invoke(app, ['users', 'find-teachers'])
                
                assert result.exit_code == 0
                assert 'Finding teacher users' in result.stdout
                assert 'Found 2 teacher users' in result.stdout
                mock_db.close.assert_called_once()

    def test_users_find_teachers_command_with_params(self, runner):
        """Test find-teachers command with survey IDs."""
        import pandas as pd
        
        with patch('src.models.database.SessionLocal') as mock_session_local:
            with patch('src.analysis.user_analysis.find_teacher_users') as mock_find:
                mock_db = Mock()
                mock_session_local.return_value = mock_db
                
                mock_find.return_value = pd.DataFrame({
                    'email': ['teacher1@example.com'],
                    'name': ['Teacher 1']
                })
                
                result = runner.invoke(app, ['users', 'find-teachers', '--survey-ids', 'survey1,survey2'])
                
                assert result.exit_code == 0
                mock_find.assert_called_once()
                call_args = mock_find.call_args
                assert call_args[1]['survey_ids'] == ['survey1', 'survey2']

    def test_users_find_teachers_command_with_output(self, runner):
        """Test find-teachers command with output file."""
        import pandas as pd
        import tempfile
        import os
        
        temp_file = tempfile.mktemp(suffix='.csv')
        
        try:
            with patch('src.models.database.SessionLocal') as mock_session_local:
                with patch('src.analysis.user_analysis.find_teacher_users') as mock_find:
                    mock_db = Mock()
                    mock_session_local.return_value = mock_db
                    
                    mock_df = pd.DataFrame({
                        'email': ['teacher1@example.com'],
                        'name': ['Teacher 1']
                    })
                    mock_find.return_value = mock_df
                    
                    result = runner.invoke(app, ['users', 'find-teachers', '--output', temp_file])
                    
                    assert result.exit_code == 0
                    assert 'Results saved to' in result.stdout
                    assert temp_file in result.stdout
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_users_find_teachers_command_error(self, runner):
        """Test find-teachers command with error."""
        with patch('src.models.database.SessionLocal') as mock_session_local:
            with patch('src.analysis.user_analysis.find_teacher_users') as mock_find:
                mock_db = Mock()
                mock_session_local.return_value = mock_db
                
                mock_find.side_effect = Exception("Teacher search failed")
                
                result = runner.invoke(app, ['users', 'find-teachers'])
                
                assert result.exit_code == 1
                assert 'Teacher search failed' in result.stdout
                mock_db.close.assert_called_once()


class TestDashboardCommand:
    """Test dashboard command."""

    def test_dashboard_command_success(self, runner):
        """Test dashboard command."""
        with patch('subprocess.run') as mock_run:
            # Simulate keyboard interrupt to stop the command
            mock_run.side_effect = KeyboardInterrupt()
            
            result = runner.invoke(app, ['dashboard'])
            
            assert result.exit_code == 0 or 'Dashboard stopped' in result.stdout

    def test_dashboard_command_with_options(self, runner):
        """Test dashboard command with custom options."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = KeyboardInterrupt()
            
            result = runner.invoke(app, ['dashboard', '--port', '8502', '--api-url', 'http://api:8000'])
            
            # Should at least start the process
            call_args = mock_run.call_args
            if call_args:
                assert '8502' in str(call_args)

    def test_dashboard_command_error(self, runner):
        """Test dashboard command with error."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = Exception("Failed to start dashboard")
            
            result = runner.invoke(app, ['dashboard'])
            
            assert result.exit_code == 1
            assert 'Failed to start dashboard' in result.stdout
