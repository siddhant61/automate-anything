"""
Scraping service for OpenHPI platform.

This module replaces the Selenium-based scrapers with a modern, requests-based approach.
Uses requests.Session() for authenticated scraping and BeautifulSoup4 for parsing.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.utils import utcnow
from src.models.tables import Course, CourseStats, ScrapingJob

logger = logging.getLogger(__name__)


class ScrapingError(Exception):
    """Base exception for scraping errors."""
    pass


class OpenHPIScraper:
    """
    Scraper for OpenHPI platform using requests instead of Selenium.
    
    This replaces the brittle Selenium-based scrapers (data_scraper.py, course_scraper.py)
    with a more robust, maintainable solution.
    """
    
    def __init__(self, db: Session):
        """
        Initialize scraper with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.session = requests.Session()
        self.base_url = settings.openhpi_base_url
        self.authenticated = False
    
    def login(self) -> bool:
        """
        Authenticate with OpenHPI platform.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        openhpi_password = settings.openhpi_password.get_secret_value() if settings.openhpi_password else ""
        if not settings.openhpi_username or not openhpi_password:
            logger.error("OpenHPI credentials not configured")
            return False
        
        try:
            # First, get the login page to retrieve any CSRF tokens
            login_url = f"{self.base_url}/sessions/new"
            response = self.session.get(login_url)
            response.raise_for_status()
            
            # Parse the login form to find any hidden fields
            soup = BeautifulSoup(response.text, 'html.parser')
            login_form = soup.find('form')
            
            # Build login data
            login_data = {
                'login': settings.openhpi_username,
                'password': openhpi_password,
            }
            
            # Add any hidden form fields (CSRF tokens, etc.)
            if login_form:
                for hidden in login_form.find_all('input', type='hidden'):
                    name = hidden.get('name')
                    value = hidden.get('value')
                    if name:
                        login_data[name] = value
            
            # Submit login
            login_submit_url = f"{self.base_url}/sessions"
            response = self.session.post(login_submit_url, data=login_data, allow_redirects=True)
            
            # Check if login was successful
            # A successful login usually redirects and sets cookies
            self.authenticated = response.ok and 'sessions/new' not in response.url
            
            if self.authenticated:
                logger.info("Successfully authenticated with OpenHPI")
            else:
                logger.error("Failed to authenticate with OpenHPI")
            
            return self.authenticated
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def scrape_courses_list(self) -> List[Dict]:
        """
        Scrape the list of available courses from OpenHPI.
        
        This replaces the Selenium logic from course_scraper.py with requests.
        
        Returns:
            List[Dict]: List of course data dictionaries
        """
        try:
            courses_url = f"{self.base_url}/courses"
            response = self.session.get(courses_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            course_cards = soup.find_all('div', class_='course-card')
            
            courses = []
            for card in course_cards:
                course_data = {}
                
                # Extract title
                title_tag = card.find('div', class_='course-card__title')
                if title_tag:
                    course_data['title'] = title_tag.text.strip()
                
                # Extract description
                desc_tag = card.find('div', class_='course-card__description')
                if desc_tag:
                    course_data['description'] = desc_tag.text.strip()
                
                # Extract URL
                link_tag = card.find('a', href=True)
                if link_tag:
                    course_data['url'] = self.base_url + link_tag['href']
                    # Extract course ID from URL
                    course_data['course_id'] = link_tag['href'].split('/')[-1]
                
                # Extract language if available
                lang_tag = card.find('span', class_='course-card__language')
                if lang_tag:
                    course_data['language'] = lang_tag.text.strip()
                
                if course_data.get('course_id'):
                    courses.append(course_data)
            
            logger.info(f"Scraped {len(courses)} courses")
            return courses
            
        except Exception as e:
            logger.error(f"Error scraping courses list: {e}")
            raise ScrapingError(f"Failed to scrape courses: {e}")
    
    def save_courses_to_db(self, courses_data: List[Dict]) -> int:
        """
        Save scraped courses to database.
        
        Args:
            courses_data: List of course dictionaries
            
        Returns:
            int: Number of courses saved/updated
        """
        saved_count = 0
        
        for data in courses_data:
            try:
                # Check if course already exists
                course = self.db.query(Course).filter_by(
                    course_id=data['course_id']
                ).first()
                
                if course:
                    # Update existing course
                    course.title = data.get('title', course.title)
                    course.description = data.get('description', course.description)
                    course.url = data.get('url', course.url)
                    course.language = data.get('language', course.language)
                    course.updated_at = utcnow()
                else:
                    # Create new course
                    course = Course(
                        course_id=data['course_id'],
                        title=data.get('title', 'Unknown'),
                        description=data.get('description'),
                        url=data.get('url'),
                        language=data.get('language')
                    )
                    self.db.add(course)
                
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Error saving course {data.get('course_id')}: {e}")
                continue
        
        try:
            self.db.commit()
            logger.info(f"Saved {saved_count} courses to database")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error committing courses to database: {e}")
            raise
        
        return saved_count
    
    def scrape_and_save_courses(self) -> Dict:
        """
        Full workflow: scrape courses and save to database.
        
        Returns:
            Dict: Job result with statistics
        """
        # Create scraping job
        job = ScrapingJob(
            job_type="course_list",
            status="running",
            started_at=utcnow()
        )
        self.db.add(job)
        self.db.commit()
        
        try:
            # Scrape courses
            courses = self.scrape_courses_list()
            
            # Save to database
            saved_count = self.save_courses_to_db(courses)
            
            # Update job status
            job.status = "completed"
            job.completed_at = utcnow()
            job.records_processed = saved_count
            self.db.commit()
            
            return {
                "status": "success",
                "courses_scraped": len(courses),
                "courses_saved": saved_count,
                "job_id": job.id
            }
            
        except Exception as e:
            # Update job with error
            job.status = "failed"
            job.completed_at = utcnow()
            job.error_message = str(e)
            self.db.commit()
            
            logger.error(f"Scraping job failed: {e}")
            raise
    
    def close(self):
        """Close the requests session."""
        self.session.close()


def scrape_courses(db: Session) -> Dict:
    """
    Convenience function to scrape courses.
    
    Args:
        db: Database session
        
    Returns:
        Dict: Scraping results
    """
    scraper = OpenHPIScraper(db)
    try:
        return scraper.scrape_and_save_courses()
    finally:
        scraper.close()
