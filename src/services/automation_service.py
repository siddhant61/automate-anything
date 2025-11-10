"""
Automation service for OpenHPI platform operations.

This module provides automation functionality ported from the original scripts:
- batch_enroll.py: Batch enrollment of users
- helpdesk_notifier.py: Helpdesk ticket monitoring and notification
- page_updater.py: Page content updates
"""

import asyncio
import logging
from datetime import datetime, date
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import mimetypes
from telegram import Bot
import pandas as pd
import numpy as np

from src.core.config import settings
from src.models.tables import HelpdeskTicket


logger = logging.getLogger(__name__)


class AutomationService:
    """Service for platform automation tasks."""
    
    def __init__(self):
        """Initialize automation service."""
        self.settings = settings
    
    def _create_driver(self, headless: bool = True) -> webdriver.Chrome:
        """
        Create and configure Chrome WebDriver.
        
        Args:
            headless: Whether to run in headless mode
            
        Returns:
            Configured Chrome WebDriver
        """
        options = webdriver.ChromeOptions()
        
        if headless:
            options.add_argument("--headless")
        
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        
        # Disable notifications
        prefs = {"profile.default_content_setting_values.notifications": 2}
        options.add_experimental_option("prefs", prefs)
        
        return webdriver.Chrome(options=options)
    
    def _login_openhpi(self, driver: webdriver.Chrome) -> bool:
        """
        Login to OpenHPI platform.
        
        Args:
            driver: Chrome WebDriver instance
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            url = f"{self.settings.openhpi_base_url}/sessions/new"
            driver.get(url)
            
            wait = WebDriverWait(driver, 10)
            
            # Find and fill username
            username_field = wait.until(
                EC.presence_of_element_located((By.ID, "login_email"))
            )
            username_field.send_keys(self.settings.openhpi_username)
            
            # Find and fill password
            password_field = wait.until(
                EC.presence_of_element_located((By.ID, "login_password"))
            )
            openhpi_password = self.settings.openhpi_password.get_secret_value() if self.settings.openhpi_password else ""
            password_field.send_keys(openhpi_password)
            
            # Click login button
            login_button = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
            )
            login_button.click()
            
            # Wait for redirect
            wait.until(lambda d: d.current_url != url)
            
            return True
        except Exception as e:
            logger.error("Login failed: {str(e)}")
            return False
    
    def batch_enroll_users(
        self, 
        users: List[str], 
        course_id: str,
        headless: bool = True
    ) -> Dict[str, List[str]]:
        """
        Batch enroll users in a course.
        
        Args:
            users: List of user email addresses
            course_id: Course identifier
            headless: Whether to run in headless mode
            
        Returns:
            Dictionary with 'enrolled' and 'unregistered' user lists
        """
        driver = None
        enrolled_emails = []
        unregistered_emails = []
        
        try:
            driver = self._create_driver(headless=headless)
            
            # Login to OpenHPI
            if not self._login_openhpi(driver):
                raise Exception("Failed to login to OpenHPI")
            
            # Navigate to users page
            driver.get(f"{self.settings.openhpi_base_url}/users")
            wait = WebDriverWait(driver, 10)
            
            for email in users:
                try:
                    # Search for user
                    search_field = wait.until(
                        EC.presence_of_element_located((By.ID, "user_filter_query"))
                    )
                    search_field.clear()
                    search_field.send_keys(email)
                    
                    search_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                    search_btn.click()
                    
                    # Check if user exists
                    try:
                        details_link = wait.until(
                            EC.presence_of_element_located((By.LINK_TEXT, "Details"))
                        )
                        details_link.click()
                        
                        # Masquerade as user
                        masq_btn = wait.until(
                            EC.presence_of_element_located((By.LINK_TEXT, "MASQ"))
                        )
                        masq_btn.click()
                        
                        # Navigate to course
                        driver.get(f"{self.settings.openhpi_base_url}/courses/{course_id}")
                        
                        # Check if already enrolled
                        try:
                            driver.find_element(By.LINK_TEXT, "Enter course")
                            logger.info(f"{email} is already enrolled.")
                        except NoSuchElementException:
                            # Enroll user
                            enroll_btn = wait.until(
                                EC.presence_of_element_located((By.LINK_TEXT, "Enroll"))
                            )
                            enroll_btn.click()
                        
                        # Demasquerade
                        demasq_link = wait.until(
                            EC.presence_of_element_located((By.LINK_TEXT, "DEMASQ"))
                        )
                        demasq_link.click()
                        
                        enrolled_emails.append(email)
                        
                        # Return to users page
                        driver.get(f"{self.settings.openhpi_base_url}/users")
                        
                    except Exception as e:
                        logger.warning(f"User {email} not found or error: {str(e)}")
                        unregistered_emails.append(email)
                        driver.get(f"{self.settings.openhpi_base_url}/users")
                        
                except Exception as e:
                    logger.error(f"Error processing {email}: {str(e)}")
                    unregistered_emails.append(email)
        
        finally:
            if driver:
                driver.quit()
        
        return {
            'enrolled': enrolled_emails,
            'unregistered': unregistered_emails
        }
    
    def _login_helpdesk(self, driver: webdriver.Chrome) -> bool:
        """
        Login to helpdesk system.
        
        Args:
            driver: Chrome WebDriver instance
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            driver.get(f"{self.settings.helpdesk_url}/#login")
            
            wait = WebDriverWait(driver, 10)
            
            # Find and fill username
            username_field = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
            )
            username_field.send_keys(self.settings.helpdesk_username)
            
            # Find and fill password
            password_field = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
            )
            helpdesk_password = self.settings.helpdesk_password.get_secret_value() if self.settings.helpdesk_password else ""
            password_field.send_keys(helpdesk_password)
            
            # Click login button
            login_btn = driver.find_element(By.CLASS_NAME, "btn--primary")
            login_btn.click()
            
            return True
        except Exception as e:
            logger.error("Helpdesk login failed: {str(e)}")
            return False
    
    def check_and_notify_helpdesk(self, headless: bool = True) -> Dict[str, any]:
        """
        Check helpdesk tickets and send notifications.
        
        Args:
            headless: Whether to run in headless mode
            
        Returns:
            Dictionary with ticket information and notification status
        """
        driver = None
        tickets_data = []
        
        try:
            driver = self._create_driver(headless=headless)
            
            # Login to helpdesk
            if not self._login_helpdesk(driver):
                raise Exception("Failed to login to helpdesk")
            
            # Navigate to open tickets
            driver.get(f"{self.settings.helpdesk_url}/#ticket/view/all_open")
            
            wait = WebDriverWait(driver, 60)
            content = wait.until(
                EC.presence_of_element_located((By.ID, "content_permanent_TicketOverview"))
            )
            
            # Get pagination
            try:
                page_element = content.find_element(By.CLASS_NAME, "js-pager")
                pages = page_element.find_elements(By.CLASS_NAME, "js-page")
                num_pages = len(pages) if pages else 1
            except NoSuchElementException:
                num_pages = 1
            
            # Collect tickets from all pages
            for page_num in range(num_pages):
                if page_num > 0:
                    # Click next page
                    page_element.find_elements(By.CLASS_NAME, "js-page")[page_num].click()
                
                # Get ticket rows
                table_body = content.find_element(By.CLASS_NAME, "js-tableBody")
                ticket_rows = table_body.find_elements(By.CLASS_NAME, "item")
                
                for i, row in enumerate(ticket_rows):
                    try:
                        ticket_id = row.find_element(By.CSS_SELECTOR, "td:nth-child(3) a").text
                        ticket_url = row.find_element(By.CSS_SELECTOR, "td:nth-child(3) a").get_attribute("href")
                        time_open = row.find_element(By.CLASS_NAME, "humanTimeFromNow").text
                        state = row.find_elements(By.CLASS_NAME, "user-popover")[1].text
                        owner = row.find_element(By.CSS_SELECTOR, "td:nth-child(7)").text
                        
                        tickets_data.append({
                            'ticket_id': ticket_id,
                            'ticket_url': ticket_url,
                            'time_open': time_open,
                            'state': state,
                            'owner': owner if owner else 'Not Assigned'
                        })
                    except Exception as e:
                        logger.error(f"Error extracting ticket data: {str(e)}")
            
            # Analyze tickets
            analysis = self._analyze_tickets(tickets_data)
            
            # Send notifications
            notification_sent = False
            telegram_bot_token = self.settings.telegram_bot_token.get_secret_value() if self.settings.telegram_bot_token else ""
            if telegram_bot_token and self.settings.telegram_chat_id:
                notification_sent = asyncio.run(
                    self._send_telegram_notification(tickets_data, analysis)
                )
            
            # Send email with CSV
            email_sent = False
            if self.settings.smtp_username and self.settings.email_from:
                email_sent = self._send_email_notification(tickets_data)
            
            return {
                'success': True,
                'tickets_count': len(tickets_data),
                'tickets': tickets_data,
                'analysis': analysis,
                'notification_sent': notification_sent,
                'email_sent': email_sent
            }
        
        finally:
            if driver:
                driver.quit()
    
    def _analyze_tickets(self, tickets: List[Dict]) -> Dict[str, any]:
        """
        Analyze ticket data.
        
        Args:
            tickets: List of ticket dictionaries
            
        Returns:
            Dictionary with analysis results
        """
        h6 = h12 = h24 = h48 = 0
        owner_counts = {}
        
        for ticket in tickets:
            time_str = ticket['time_open']
            owner = ticket['owner']
            
            # Count by owner
            owner_counts[owner] = owner_counts.get(owner, 0) + 1
            
            # Parse time
            if 'ago' in time_str:
                hrs = [int(s) for s in time_str.split() if s.isdigit()]
                if hrs:
                    if 'hour' in time_str:
                        hour_val = hrs[0]
                        if hour_val <= 6:
                            h6 += 1
                        elif hour_val <= 12:
                            h12 += 1
                        elif hour_val <= 24:
                            h24 += 1
                    elif 'minute' in time_str:
                        h6 += 1
            elif '/' in time_str:  # Date format, more than 48 hours
                h48 += 1
        
        return {
            'within_6hrs': h6,
            'within_12hrs': h12,
            'within_24hrs': h24,
            'within_48hrs': h48,
            'by_owner': owner_counts
        }
    
    async def _send_telegram_notification(
        self, 
        tickets: List[Dict], 
        analysis: Dict
    ) -> bool:
        """
        Send notification via Telegram.
        
        Args:
            tickets: List of ticket dictionaries
            analysis: Analysis results
            
        Returns:
            True if notification sent successfully
        """
        try:
            telegram_bot_token = self.settings.telegram_bot_token.get_secret_value() if self.settings.telegram_bot_token else ""
            bot = Bot(telegram_bot_token)
            
            message = f"""
=== Helpdesk Notification ===

Date: {date.today()}
Time: {datetime.now().strftime('%H:%M')}
Total Tickets: {len(tickets)}

Time Range Analysis:
Within 06 Hrs: {analysis['within_6hrs']}
Within 12 Hrs: {analysis['within_12hrs']}
Within 24 Hrs: {analysis['within_24hrs']}
Within 48 Hrs: {analysis['within_48hrs']}

Tickets by Owner:
"""
            for owner, count in analysis['by_owner'].items():
                message += f"{owner}: {count}\n"
            
            text = f"```\n{message}\n```"
            await bot.send_message(
                chat_id=self.settings.telegram_chat_id,
                text=text,
                parse_mode='MarkdownV2'
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {str(e)}")
            return False
    
    def _send_email_notification(self, tickets: List[Dict]) -> bool:
        """
        Send email notification with ticket CSV.
        
        Args:
            tickets: List of ticket dictionaries
            
        Returns:
            True if email sent successfully
        """
        try:
            # Create CSV
            df = pd.DataFrame(tickets)
            timestamp = datetime.now().strftime('%H')
            filename = f'tickets_{timestamp}_{date.today()}.csv'
            df.to_csv(filename, index=False)
            
            # Prepare email
            msg = MIMEMultipart()
            msg['From'] = self.settings.email_from
            msg['To'] = self.settings.email_to
            msg['Subject'] = f'Open tickets at {timestamp} Uhr on {date.today()}'
            
            msg.attach(MIMEText("Please find the attachment", 'plain'))
            
            # Attach CSV
            with open(filename, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={filename}')
                msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(f"{self.settings.smtp_host}:{self.settings.smtp_port}")
            server.ehlo()
            server.starttls()
            smtp_password = self.settings.smtp_password.get_secret_value() if self.settings.smtp_password else ""
            server.login(self.settings.smtp_username, smtp_password)
            server.sendmail(self.settings.email_from, self.settings.email_to, msg.as_string())
            server.quit()
            
            # Clean up CSV file
            import os
            os.remove(filename)
            
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def update_page(
        self,
        page_name: str,
        content: str,
        headless: bool = True
    ) -> bool:
        """
        Update page content on OpenHPI platform.
        
        Args:
            page_name: Name of the page to update
            content: New content for the page
            headless: Whether to run in headless mode
            
        Returns:
            True if update successful, False otherwise
        """
        driver = None
        
        try:
            driver = self._create_driver(headless=headless)
            
            # Login to OpenHPI
            if not self._login_openhpi(driver):
                raise Exception("Failed to login to OpenHPI")
            
            # Navigate to page
            driver.get(f"{self.settings.openhpi_base_url}/pages/{page_name}")
            
            wait = WebDriverWait(driver, 10)
            
            # Find and click first editor
            col = driver.find_element(By.CSS_SELECTOR, "div.col")
            editors = col.find_elements(By.CLASS_NAME, "text-truncate")
            
            if editors:
                editors[0].click()
                
                # Find input field and update content
                input_field = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "textarea"))
                )
                input_field.clear()
                input_field.send_keys(content)
                
                # Submit
                submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
                submit_btn.click()
                
                return True
            else:
                logger.warning("No editor found on page")
                return False
        
        except Exception as e:
            logger.error(f"Failed to update page: {str(e)}")
            return False
        
        finally:
            if driver:
                driver.quit()


# Global service instance
automation_service = AutomationService()
