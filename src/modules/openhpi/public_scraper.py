"""
Public (non-authenticated) scraper for OpenHPI platform.

This module provides scraping functionality that does NOT require credentials.
It scrapes publicly available data from the OpenHPI courses page.

Based on the original openhpi-visualizer/scraper.py logic.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from src.models.tables import Source, ScrapedData, ProcessedData, ScrapingJob
from src.core.utils import utcnow

logger = logging.getLogger(__name__)


class OpenHPIPublicScraper:
    """
    Public scraper for OpenHPI platform.
    
    This scraper only accesses publicly available data and does NOT require
    authentication. It is suitable for general use without credentials.
    """
    
    def __init__(self, db: Session):
        """
        Initialize public scraper.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.base_url = "https://open.hpi.de"
        self.session = requests.Session()
        # Set user agent to be polite
        self.session.headers.update({
            'User-Agent': 'OpenHPI-Automation-Platform/1.0 (Educational Purpose)'
        })
    
    def scrape_courses_page(self) -> List[Dict]:
        """
        Scrape the public courses page.
        
        Returns:
            List[Dict]: List of course data dictionaries with title, description, etc.
        """
        courses_url = f"{self.base_url}/courses"
        
        try:
            response = self.session.get(courses_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            course_cards = soup.find_all('div', class_='course-card')
            
            courses_data = []
            for card in course_cards:
                course = {}
                
                # Extract title
                title_tag = card.find('div', class_='course-card__title')
                course['title'] = title_tag.text.strip() if title_tag else 'No title found'
                
                # Extract description
                desc_tag = card.find('div', class_='course-card__description')
                course['description'] = desc_tag.text.strip() if desc_tag else 'No description found'
                
                # Extract URL and course ID
                link_tag = card.find('a', href=True)
                if link_tag:
                    course['url'] = self.base_url + link_tag['href']
                    # Extract course_id from URL (e.g., /courses/python-basics -> python-basics)
                    course['course_id'] = link_tag['href'].split('/')[-1]
                
                # Extract language if available
                lang_tag = card.find('span', class_='course-card__language')
                if lang_tag:
                    course['language'] = lang_tag.text.strip()
                
                # Extract status/category if available
                status_tag = card.find('span', class_='course-card__status')
                if status_tag:
                    course['status'] = status_tag.text.strip()
                
                courses_data.append(course)
            
            logger.info(f"Successfully scraped {len(courses_data)} courses from public page")
            return courses_data
            
        except requests.RequestException as e:
            logger.error(f"Error scraping courses page: {e}")
            raise
    
    def save_to_generic_tables(
        self, 
        source: Source, 
        courses_data: List[Dict],
        raw_html: str
    ) -> Dict:
        """
        Save scraped data to generic tables (ScrapedData, ProcessedData).
        
        Args:
            source: Source object for this scrape
            courses_data: List of parsed course dictionaries
            raw_html: Raw HTML content
            
        Returns:
            Dict: Statistics about saved data
        """
        # Create scraped data record
        scraped = ScrapedData(
            source_id=source.id,
            url=f"{self.base_url}/courses",
            raw_html=raw_html,
            raw_json={'courses': courses_data},
            scraped_at=utcnow(),
            status_code=200,
            content_type='text/html'
        )
        self.db.add(scraped)
        self.db.flush()  # Get the ID
        
        # Create processed data records (one per course)
        processed_count = 0
        for course in courses_data:
            processed = ProcessedData(
                scraped_data_id=scraped.id,
                title=course.get('title'),
                content_text=course.get('description'),
                summary=course.get('description')[:200] if course.get('description') else None,
                data_metadata={
                    'course_id': course.get('course_id'),
                    'url': course.get('url'),
                    'language': course.get('language'),
                    'status': course.get('status')
                },
                processor_module='openhpi_public',
                processed_at=utcnow()
            )
            self.db.add(processed)
            processed_count += 1
        
        # Update source last_scraped_at
        source.last_scraped_at = utcnow()
        
        self.db.commit()
        
        return {
            'scraped_data_id': scraped.id,
            'processed_records': processed_count
        }
    
    def scrape_and_save(self, source_id: int) -> Dict:
        """
        Full workflow: scrape courses from public page and save to generic tables.
        
        Args:
            source_id: ID of the source to scrape
            
        Returns:
            Dict: Scraping results with statistics
        """
        # Get source
        source = self.db.query(Source).filter_by(id=source_id).first()
        if not source:
            raise ValueError(f"Source with id {source_id} not found")
        
        # Create scraping job
        job = ScrapingJob(
            job_type="openhpi_public_scrape",
            status="running",
            started_at=utcnow(),
            job_metadata={'source_id': source_id}
        )
        self.db.add(job)
        self.db.commit()
        
        try:
            # Scrape courses
            response = self.session.get(f"{self.base_url}/courses", timeout=30)
            response.raise_for_status()
            raw_html = response.text
            
            courses_data = self.scrape_courses_page()
            
            # Save to generic tables
            save_result = self.save_to_generic_tables(source, courses_data, raw_html)
            
            # Update job status
            job.status = "completed"
            job.completed_at = utcnow()
            job.records_processed = save_result['processed_records']
            self.db.commit()
            
            return {
                'success': True,
                'courses_count': len(courses_data),
                'processed_records': save_result['processed_records'],
                'scraped_data_id': save_result['scraped_data_id'],
                'job_id': job.id
            }
            
        except Exception as e:
            # Update job with error
            job.status = "failed"
            job.completed_at = utcnow()
            job.error_message = str(e)
            self.db.commit()
            
            logger.error(f"Public scraping job failed: {e}")
            raise
    
    def close(self):
        """Close the requests session."""
        self.session.close()


def scrape_openhpi_public(db: Session, source_id: int) -> Dict:
    """
    Convenience function to scrape OpenHPI public data.
    
    Args:
        db: Database session
        source_id: ID of the source to scrape
        
    Returns:
        Dict: Scraping results
    """
    scraper = OpenHPIPublicScraper(db)
    try:
        return scraper.scrape_and_save(source_id)
    finally:
        scraper.close()
