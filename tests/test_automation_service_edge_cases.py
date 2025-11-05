"""
Edge case tests for automation service to improve coverage.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from src.services.automation_service import AutomationService


@pytest.fixture
def service():
    """Create automation service instance."""
    return AutomationService()


class TestBatchEnrollEdgeCases:
    """Test batch enrollment edge cases."""

    @patch('src.services.automation_service.AutomationService._login_openhpi')
    @patch('src.services.automation_service.webdriver.Chrome')
    @patch('src.services.automation_service.WebDriverWait')
    def test_batch_enroll_element_not_found(self, mock_wait, mock_chrome, mock_login, service):
        """Test batch enrollment when element is not found."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_login.return_value = True
        
        mock_wait_instance = Mock()
        mock_wait.return_value = mock_wait_instance
        mock_wait_instance.until.side_effect = TimeoutException("Element not found")
        
        mock_driver.quit = Mock()
        
        result = service.batch_enroll_users(
            users=['user@test.com'],
            course_id='test-course',
            headless=True
        )
        
        # Should handle gracefully
        assert 'enrolled' in result
        assert 'unregistered' in result

    @patch('src.services.automation_service.AutomationService._login_openhpi')
    @patch('src.services.automation_service.webdriver.Chrome')
    def test_batch_enroll_login_failure(self, mock_chrome, mock_login, service):
        """Test batch enrollment with login failure."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_login.return_value = False
        mock_driver.quit = Mock()
        
        # Should raise exception on login failure
        with pytest.raises(Exception, match="Failed to login to OpenHPI"):
            service.batch_enroll_users(
                users=['user@test.com'],
                course_id='test-course',
                headless=True
            )

    @patch('src.services.automation_service.webdriver.Chrome')
    @patch('src.services.automation_service.WebDriverWait')
    def test_batch_enroll_empty_users_list(self, mock_wait, mock_chrome, service):
        """Test batch enrollment with empty users list."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        result = service.batch_enroll_users(
            users=[],
            course_id='test-course',
            headless=True
        )
        
        assert result['enrolled'] == []
        assert result['unregistered'] == []


class TestHelpdeskNotificationEdgeCases:
    """Test helpdesk notification edge cases."""

    @patch('src.services.automation_service.AutomationService._login_helpdesk')
    @patch('src.services.automation_service.webdriver.Chrome')
    def test_check_helpdesk_login_failure(self, mock_chrome, mock_login, service):
        """Test helpdesk check with login failure."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_login.return_value = False
        mock_driver.quit = Mock()
        
        # Should raise exception on login failure
        with pytest.raises(Exception, match="Failed to login to helpdesk"):
            service.check_and_notify_helpdesk(headless=True)

    @patch('src.services.automation_service.AutomationService._login_helpdesk')
    @patch('src.services.automation_service.webdriver.Chrome')
    @patch('src.services.automation_service.WebDriverWait')
    def test_check_helpdesk_no_tickets(self, mock_wait, mock_chrome, mock_login, service):
        """Test helpdesk check when no tickets exist."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_login.return_value = True
        
        # Mock the wait for content
        mock_wait_instance = Mock()
        mock_wait.return_value = mock_wait_instance
        
        # Mock content element with table structure
        mock_content = Mock()
        mock_wait_instance.until.return_value = mock_content
        
        # Mock the table body with no tickets
        mock_table_body = Mock()
        mock_table_body.find_elements.return_value = []  # No ticket rows
        mock_content.find_element.return_value = mock_table_body
        
        # Mock driver quit
        mock_driver.quit = Mock()
        
        result = service.check_and_notify_helpdesk(headless=True)
        
        assert result['tickets_count'] == 0
        assert result['analysis']['within_6hrs'] == 0

    @patch('src.services.automation_service.AutomationService._login_helpdesk')
    @patch('src.services.automation_service.webdriver.Chrome')
    @patch('src.services.automation_service.WebDriverWait')
    def test_check_helpdesk_element_not_found(self, mock_wait, mock_chrome, mock_login, service):
        """Test helpdesk check when ticket elements not found."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_login.return_value = True
        
        mock_wait_instance = Mock()
        mock_wait.return_value = mock_wait_instance
        mock_wait_instance.until.side_effect = TimeoutException("Elements not found")
        mock_driver.quit = Mock()
        
        # Should raise exception when elements not found
        with pytest.raises(TimeoutException):
            service.check_and_notify_helpdesk(headless=True)


class TestPageUpdateEdgeCases:
    """Test page update edge cases."""

    @patch('src.services.automation_service.AutomationService._login_openhpi')
    @patch('src.services.automation_service.webdriver.Chrome')
    def test_update_page_login_failure(self, mock_chrome, mock_login, service):
        """Test page update with login failure."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_login.return_value = False
        mock_driver.quit = Mock()
        
        result = service.update_page(
            page_name='test-page',
            content='<h1>Test</h1>',
            headless=True
        )
        
        assert result is False

    @patch('src.services.automation_service.AutomationService._login_openhpi')
    @patch('src.services.automation_service.webdriver.Chrome')
    @patch('src.services.automation_service.WebDriverWait')
    def test_update_page_element_not_found(self, mock_wait, mock_chrome, mock_login, service):
        """Test page update when page element not found."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_login.return_value = True
        
        mock_wait_instance = Mock()
        mock_wait.return_value = mock_wait_instance
        mock_wait_instance.until.side_effect = TimeoutException("Page not found")
        mock_driver.quit = Mock()
        
        result = service.update_page(
            page_name='nonexistent-page',
            content='<h1>Test</h1>',
            headless=True
        )
        
        assert result is False

    @patch('src.services.automation_service.AutomationService._login_openhpi')
    @patch('src.services.automation_service.webdriver.Chrome')
    @patch('src.services.automation_service.WebDriverWait')
    def test_update_page_save_failure(self, mock_wait, mock_chrome, mock_login, service):
        """Test page update when save fails."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_login.return_value = True
        
        mock_wait_instance = Mock()
        mock_wait.return_value = mock_wait_instance
        
        mock_element = Mock()
        mock_element.clear = Mock()
        mock_element.send_keys = Mock()
        mock_element.click.side_effect = Exception("Save failed")
        mock_wait_instance.until.return_value = mock_element
        mock_driver.quit = Mock()
        
        result = service.update_page(
            page_name='test-page',
            content='<h1>Test</h1>',
            headless=True
        )
        
        assert result is False


class TestLoginEdgeCases:
    """Test login edge cases."""

    @patch('src.services.automation_service.webdriver.Chrome')
    @patch('src.services.automation_service.WebDriverWait')
    def test_login_helpdesk_timeout(self, mock_wait, mock_chrome, service):
        """Test helpdesk login timeout."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        mock_driver.get = Mock()
        mock_wait_instance = Mock()
        mock_wait.return_value = mock_wait_instance
        mock_wait_instance.until.side_effect = TimeoutException("Timeout")
        
        result = service._login_helpdesk(mock_driver)
        
        assert result is False

    @patch('src.services.automation_service.webdriver.Chrome')
    @patch('src.services.automation_service.WebDriverWait')
    def test_login_helpdesk_element_not_found(self, mock_wait, mock_chrome, service):
        """Test helpdesk login when element not found."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        mock_driver.get = Mock()
        mock_driver.find_element.side_effect = NoSuchElementException("Element not found")
        
        result = service._login_helpdesk(mock_driver)
        
        assert result is False

    @patch('src.services.automation_service.webdriver.Chrome')
    @patch('src.services.automation_service.WebDriverWait')
    def test_login_openhpi_timeout(self, mock_wait, mock_chrome, service):
        """Test OpenHPI login timeout."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        mock_driver.get = Mock()
        mock_wait_instance = Mock()
        mock_wait.return_value = mock_wait_instance
        mock_wait_instance.until.side_effect = TimeoutException("Timeout")
        
        result = service._login_openhpi(mock_driver)
        
        assert result is False


class TestTicketAnalysisEdgeCases:
    """Test ticket analysis edge cases."""

    def test_analyze_tickets_empty(self, service):
        """Test analyzing empty tickets list."""
        result = service._analyze_tickets([])
        
        assert result['within_6hrs'] == 0
        assert result['within_12hrs'] == 0
        assert result['within_24hrs'] == 0
        assert result['within_48hrs'] == 0
        assert result['by_owner'] == {}

    def test_analyze_tickets_various_time_formats(self, service):
        """Test analyzing tickets with various time formats."""
        tickets = [
            {'ticket_id': '1', 'time_open': '30 minutes ago', 'owner': 'User1', 'state': 'open'},
            {'ticket_id': '2', 'time_open': '5 hours ago', 'owner': 'User2', 'state': 'open'},
            {'ticket_id': '3', 'time_open': '15 hours ago', 'owner': 'User1', 'state': 'open'},
            {'ticket_id': '4', 'time_open': '30 hours ago', 'owner': 'User3', 'state': 'open'},
            {'ticket_id': '5', 'time_open': '2024/01/15 10:30', 'owner': 'User4', 'state': 'open'},
            {'ticket_id': '6', 'time_open': 'invalid format', 'owner': 'User5', 'state': 'open'},
        ]
        
        result = service._analyze_tickets(tickets)
        
        # Should categorize based on time
        assert result['within_6hrs'] >= 2
        assert result['by_owner']['User1'] == 2


class TestNotificationEdgeCases:
    """Test notification edge cases."""

    @patch('src.services.automation_service.smtplib.SMTP')
    def test_send_email_smtp_login_failure(self, mock_smtp, service):
        """Test email notification with SMTP login failure."""
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        mock_server.login.side_effect = Exception("Login failed")
        
        service.settings.email_from = "from@test.com"
        service.settings.email_to = "to@test.com"
        service.settings.smtp_username = "user"
        service.settings.smtp_password = "pass"
        service.settings.smtp_host = "smtp.test.com"
        service.settings.smtp_port = 587
        
        tickets = [{'ticket_id': '1', 'owner': 'Test', 'time_open': '1h', 'state': 'open', 'ticket_url': 'http://test'}]
        
        result = service._send_email_notification(tickets)
        
        assert result is False

    @patch('src.services.automation_service.smtplib.SMTP')
    def test_send_email_sendmail_failure(self, mock_smtp, service):
        """Test email notification with sendmail failure."""
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        mock_server.login = Mock()
        mock_server.sendmail.side_effect = Exception("Send failed")
        
        service.settings.email_from = "from@test.com"
        service.settings.email_to = "to@test.com"
        service.settings.smtp_username = "user"
        service.settings.smtp_password = "pass"
        service.settings.smtp_host = "smtp.test.com"
        service.settings.smtp_port = 587
        
        tickets = [{'ticket_id': '1', 'owner': 'Test', 'time_open': '1h', 'state': 'open', 'ticket_url': 'http://test'}]
        
        result = service._send_email_notification(tickets)
        
        assert result is False


class TestDriverCreationEdgeCases:
    """Test driver creation edge cases."""

    @patch('src.services.automation_service.webdriver.Chrome')
    def test_create_driver_with_custom_options(self, mock_chrome, service):
        """Test creating driver with various options."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        
        # Test headless
        driver = service._create_driver(headless=True)
        assert driver is not None
        
        # Test non-headless
        driver = service._create_driver(headless=False)
        assert driver is not None

    @patch('src.services.automation_service.webdriver.Chrome')
    def test_create_driver_failure(self, mock_chrome, service):
        """Test driver creation failure."""
        mock_chrome.side_effect = Exception("WebDriver not found")
        
        with pytest.raises(Exception):
            service._create_driver(headless=True)
