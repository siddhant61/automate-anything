"""
Tests for scraping service.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.services.scraping_service import (
    OpenHPIScraper,
    scrape_courses,
    ScrapingError
)
from src.models.tables import Course, ScrapingJob


@pytest.fixture
def mock_db():
    """Create mock database session."""
    db = Mock()
    db.query.return_value.filter_by.return_value.first.return_value = None
    db.add = Mock()
    db.commit = Mock()
    db.rollback = Mock()
    return db


@pytest.fixture
def scraper(mock_db):
    """Create scraper instance."""
    with patch('src.services.scraping_service.settings') as mock_settings:
        mock_settings.openhpi_base_url = "https://open.hpi.de"
        mock_settings.openhpi_username = "test_user"
        mock_settings.openhpi_password = "test_pass"
        return OpenHPIScraper(mock_db)


class TestOpenHPIScraper:
    """Test OpenHPIScraper class."""

    def test_initialization(self, mock_db):
        """Test scraper initialization."""
        with patch('src.services.scraping_service.settings') as mock_settings:
            mock_settings.openhpi_base_url = "https://open.hpi.de"
            scraper = OpenHPIScraper(mock_db)
            
            assert scraper.db is mock_db
            assert scraper.session is not None
            assert scraper.base_url == "https://open.hpi.de"
            assert scraper.authenticated is False

    @patch('src.services.scraping_service.settings')
    def test_login_no_credentials(self, mock_settings, mock_db):
        """Test login fails without credentials."""
        mock_settings.openhpi_username = None
        mock_settings.openhpi_password = None
        mock_settings.openhpi_base_url = "https://open.hpi.de"
        
        scraper = OpenHPIScraper(mock_db)
        result = scraper.login()
        
        assert result is False
        assert scraper.authenticated is False

    @patch('src.services.scraping_service.settings')
    def test_login_success(self, mock_settings, scraper):
        """Test successful login."""
        mock_settings.openhpi_username = "test_user"
        mock_settings.openhpi_password = "test_pass"
        
        # Mock the login page response with a form
        login_page_html = """
        <html>
            <form action="/sessions">
                <input type="hidden" name="csrf_token" value="abc123" />
                <input type="text" name="login" />
                <input type="password" name="password" />
            </form>
        </html>
        """
        
        # Mock successful login redirect
        mock_response_login = Mock()
        mock_response_login.text = login_page_html
        mock_response_login.raise_for_status = Mock()
        
        mock_response_submit = Mock()
        mock_response_submit.ok = True
        mock_response_submit.url = "https://open.hpi.de/dashboard"
        
        with patch.object(scraper.session, 'get', return_value=mock_response_login):
            with patch.object(scraper.session, 'post', return_value=mock_response_submit):
                result = scraper.login()
        
        assert result is True
        assert scraper.authenticated is True

    @patch('src.services.scraping_service.settings')
    def test_login_failure(self, mock_settings, scraper):
        """Test failed login."""
        mock_settings.openhpi_username = "test_user"
        mock_settings.openhpi_password = "wrong_pass"
        
        # Mock login page
        mock_response_login = Mock()
        mock_response_login.text = "<html><form></form></html>"
        mock_response_login.raise_for_status = Mock()
        
        # Mock failed login (redirects back to login page)
        mock_response_submit = Mock()
        mock_response_submit.ok = True
        mock_response_submit.url = "https://open.hpi.de/sessions/new"
        
        with patch.object(scraper.session, 'get', return_value=mock_response_login):
            with patch.object(scraper.session, 'post', return_value=mock_response_submit):
                result = scraper.login()
        
        assert result is False
        assert scraper.authenticated is False

    @patch('src.services.scraping_service.settings')
    def test_login_exception(self, mock_settings, scraper):
        """Test login handles exceptions."""
        mock_settings.openhpi_username = "test_user"
        mock_settings.openhpi_password = "test_pass"
        
        with patch.object(scraper.session, 'get', side_effect=Exception("Network error")):
            result = scraper.login()
        
        assert result is False
        assert scraper.authenticated is False

    def test_scrape_courses_list_success(self, scraper):
        """Test successful course list scraping."""
        # Mock HTML response with course cards
        html_content = """
        <html>
            <div class="course-card">
                <div class="course-card__title">Python for Beginners</div>
                <div class="course-card__description">Learn Python programming</div>
                <a href="/courses/python-101">View Course</a>
                <span class="course-card__language">English</span>
            </div>
            <div class="course-card">
                <div class="course-card__title">Machine Learning</div>
                <div class="course-card__description">ML fundamentals</div>
                <a href="/courses/ml-2024">View Course</a>
                <span class="course-card__language">German</span>
            </div>
        </html>
        """
        
        mock_response = Mock()
        mock_response.text = html_content
        mock_response.raise_for_status = Mock()
        
        with patch.object(scraper.session, 'get', return_value=mock_response):
            courses = scraper.scrape_courses_list()
        
        assert len(courses) == 2
        assert courses[0]['course_id'] == 'python-101'
        assert courses[0]['title'] == 'Python for Beginners'
        assert courses[0]['language'] == 'English'
        assert courses[1]['course_id'] == 'ml-2024'

    def test_scrape_courses_list_empty(self, scraper):
        """Test scraping with no courses found."""
        html_content = "<html><body>No courses</body></html>"
        
        mock_response = Mock()
        mock_response.text = html_content
        mock_response.raise_for_status = Mock()
        
        with patch.object(scraper.session, 'get', return_value=mock_response):
            courses = scraper.scrape_courses_list()
        
        assert len(courses) == 0

    def test_scrape_courses_list_exception(self, scraper):
        """Test scraping handles exceptions."""
        with patch.object(scraper.session, 'get', side_effect=Exception("Connection error")):
            with pytest.raises(ScrapingError, match="Failed to scrape courses"):
                scraper.scrape_courses_list()

    def test_save_courses_to_db_new_courses(self, scraper, mock_db):
        """Test saving new courses to database."""
        courses_data = [
            {
                'course_id': 'python-101',
                'title': 'Python for Beginners',
                'description': 'Learn Python',
                'url': 'https://open.hpi.de/courses/python-101',
                'language': 'English'
            },
            {
                'course_id': 'ml-2024',
                'title': 'Machine Learning',
                'description': 'ML fundamentals',
                'url': 'https://open.hpi.de/courses/ml-2024',
                'language': 'German'
            }
        ]
        
        # Mock no existing courses
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        count = scraper.save_courses_to_db(courses_data)
        
        assert count == 2
        assert mock_db.add.call_count == 2
        assert mock_db.commit.called

    def test_save_courses_to_db_update_existing(self, scraper, mock_db):
        """Test updating existing courses in database."""
        courses_data = [
            {
                'course_id': 'python-101',
                'title': 'Python for Beginners - Updated',
                'description': 'Learn Python - New Description',
                'url': 'https://open.hpi.de/courses/python-101',
                'language': 'English'
            }
        ]
        
        # Mock existing course
        existing_course = Mock(spec=Course)
        existing_course.course_id = 'python-101'
        existing_course.title = 'Python for Beginners'
        existing_course.description = 'Learn Python'
        mock_db.query.return_value.filter_by.return_value.first.return_value = existing_course
        
        count = scraper.save_courses_to_db(courses_data)
        
        assert count == 1
        assert existing_course.title == 'Python for Beginners - Updated'
        assert mock_db.commit.called

    def test_save_courses_to_db_partial_failure(self, scraper, mock_db):
        """Test saving courses with some failures."""
        courses_data = [
            {'course_id': 'valid-1', 'title': 'Valid Course'},
            {'course_id': 'invalid', 'title': None},  # Will cause error
        ]
        
        # First call succeeds, second raises exception
        mock_db.query.return_value.filter_by.return_value.first.side_effect = [
            None,  # First course doesn't exist
            Exception("DB error")  # Second course causes error
        ]
        
        count = scraper.save_courses_to_db(courses_data)
        
        # Should continue despite error with one course
        assert count == 1

    def test_save_courses_to_db_commit_failure(self, scraper, mock_db):
        """Test handling commit failure."""
        courses_data = [{'course_id': 'test-1', 'title': 'Test'}]
        
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        mock_db.commit.side_effect = Exception("Commit failed")
        
        with pytest.raises(Exception, match="Commit failed"):
            scraper.save_courses_to_db(courses_data)
        
        assert mock_db.rollback.called

    def test_scrape_and_save_courses_success(self, scraper, mock_db):
        """Test full scrape and save workflow."""
        # Mock scrape_courses_list
        mock_courses = [
            {'course_id': 'test-1', 'title': 'Test Course 1'},
            {'course_id': 'test-2', 'title': 'Test Course 2'}
        ]
        
        # Mock ScrapingJob creation
        mock_job = Mock(spec=ScrapingJob)
        mock_job.id = 123
        mock_db.add = Mock()
        
        with patch.object(scraper, 'scrape_courses_list', return_value=mock_courses):
            with patch.object(scraper, 'save_courses_to_db', return_value=2):
                result = scraper.scrape_and_save_courses()
        
        assert result['status'] == 'success'
        assert result['courses_scraped'] == 2
        assert result['courses_saved'] == 2
        assert mock_db.commit.called

    def test_scrape_and_save_courses_failure(self, scraper, mock_db):
        """Test full workflow with failure."""
        mock_job = Mock(spec=ScrapingJob)
        mock_db.add = Mock()
        
        with patch.object(scraper, 'scrape_courses_list', side_effect=Exception("Scraping failed")):
            with pytest.raises(Exception, match="Scraping failed"):
                scraper.scrape_and_save_courses()
        
        # Job should be marked as failed
        assert mock_db.commit.called

    def test_close(self, scraper):
        """Test closing the session."""
        scraper.session.close = Mock()
        scraper.close()
        assert scraper.session.close.called


class TestScrapeCourseFunction:
    """Test the convenience function."""

    @patch('src.services.scraping_service.OpenHPIScraper')
    def test_scrape_courses_function(self, mock_scraper_class):
        """Test scrape_courses convenience function."""
        mock_db = Mock()
        mock_scraper_instance = Mock()
        mock_scraper_instance.scrape_and_save_courses.return_value = {
            'status': 'success',
            'courses_scraped': 5,
            'courses_saved': 5
        }
        mock_scraper_instance.close = Mock()
        mock_scraper_class.return_value = mock_scraper_instance
        
        result = scrape_courses(mock_db)
        
        assert result['status'] == 'success'
        assert result['courses_scraped'] == 5
        mock_scraper_instance.close.assert_called_once()

    @patch('src.services.scraping_service.OpenHPIScraper')
    def test_scrape_courses_function_ensures_close(self, mock_scraper_class):
        """Test scrape_courses closes session even on exception."""
        mock_db = Mock()
        mock_scraper_instance = Mock()
        mock_scraper_instance.scrape_and_save_courses.side_effect = Exception("Error")
        mock_scraper_instance.close = Mock()
        mock_scraper_class.return_value = mock_scraper_instance
        
        with pytest.raises(Exception):
            scrape_courses(mock_db)
        
        # Should still close even on exception
        mock_scraper_instance.close.assert_called_once()
