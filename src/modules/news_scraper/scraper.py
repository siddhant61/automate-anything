"""
News Scraper - Hacker News Headlines.

This module scrapes news headlines from Hacker News (news.ycombinator.com)
as a demonstration of the platform's generic scraping capabilities.

Uses requests + BeautifulSoup4 (no authentication required).
"""

import logging
from typing import List, Dict
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from src.models.tables import Source, ScrapedData, ProcessedData, ScrapingJob
from src.core.utils import utcnow

logger = logging.getLogger(__name__)


class HackerNewsScraper:
    """
    Scraper for Hacker News front page.
    
    This scraper accesses publicly available data without authentication.
    It demonstrates how a simple news scraper can be integrated into the platform.
    """
    
    def __init__(self, db: Session):
        """
        Initialize Hacker News scraper.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.base_url = "https://news.ycombinator.com"
        self.session = requests.Session()
        # Set user agent to be polite
        self.session.headers.update({
            'User-Agent': 'Data-Pipeline-Platform/1.0 (Educational Purpose)'
        })
    
    def scrape_front_page(self) -> List[Dict]:
        """
        Scrape the Hacker News front page for headlines.
        
        Returns:
            List[Dict]: List of news items with title, url, points, etc.
        """
        try:
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Hacker News uses a table structure for posts
            news_items = []
            
            # Find all story rows (they have class 'athing')
            story_rows = soup.find_all('tr', class_='athing')
            
            for story_row in story_rows[:30]:  # Get top 30 stories
                news_item = {}
                
                # Get story ID
                news_item['story_id'] = story_row.get('id', '')
                
                # Get title and URL
                title_cell = story_row.find('span', class_='titleline')
                if title_cell:
                    link = title_cell.find('a')
                    if link:
                        news_item['title'] = link.text.strip()
                        news_item['url'] = link.get('href', '')
                        
                        # Get domain if it's a link story
                        site_span = title_cell.find('span', class_='sitestr')
                        if site_span:
                            news_item['domain'] = site_span.text.strip()
                
                # Get the next row for metadata (points, user, time, comments)
                subtext_row = story_row.find_next_sibling('tr')
                if subtext_row:
                    subtext = subtext_row.find('td', class_='subtext')
                    if subtext:
                        # Get points
                        score = subtext.find('span', class_='score')
                        if score:
                            news_item['points'] = score.text.strip()
                        
                        # Get author
                        user = subtext.find('a', class_='hnuser')
                        if user:
                            news_item['author'] = user.text.strip()
                        
                        # Get age
                        age = subtext.find('span', class_='age')
                        if age:
                            news_item['age'] = age.text.strip()
                        
                        # Get comment count
                        comments_link = subtext.find_all('a')
                        for link in comments_link:
                            if 'comment' in link.text.lower():
                                news_item['comments'] = link.text.strip()
                                news_item['comments_url'] = f"{self.base_url}/{link.get('href', '')}"
                
                if news_item.get('title'):  # Only add if we got a title
                    news_items.append(news_item)
            
            logger.info(f"Successfully scraped {len(news_items)} news items from Hacker News")
            return news_items
            
        except requests.RequestException as e:
            logger.error(f"Error scraping Hacker News: {e}")
            raise
    
    def save_to_generic_tables(
        self,
        source: Source,
        news_items: List[Dict],
        raw_html: str
    ) -> Dict:
        """
        Save scraped news data to generic tables (ScrapedData, ProcessedData).
        
        Args:
            source: Source object for this scrape
            news_items: List of parsed news item dictionaries
            raw_html: Raw HTML content
            
        Returns:
            Dict: Statistics about saved data
        """
        # Create scraped data record
        scraped = ScrapedData(
            source_id=source.id,
            url=self.base_url,
            raw_html=raw_html,
            raw_json={'news_items': news_items},
            scraped_at=utcnow(),
            status_code=200,
            content_type='text/html'
        )
        self.db.add(scraped)
        self.db.flush()  # Get the ID
        
        # Create processed data records (one per news item)
        processed_count = 0
        for item in news_items:
            # Extract the main text content
            content_parts = []
            if item.get('points'):
                content_parts.append(f"Points: {item['points']}")
            if item.get('author'):
                content_parts.append(f"By: {item['author']}")
            if item.get('age'):
                content_parts.append(f"Posted: {item['age']}")
            if item.get('comments'):
                content_parts.append(f"{item['comments']}")
            
            content_text = " | ".join(content_parts) if content_parts else ""
            
            processed = ProcessedData(
                scraped_data_id=scraped.id,
                title=item.get('title'),
                content_text=content_text,
                summary=item.get('title')[:200] if item.get('title') else None,
                data_metadata={
                    'story_id': item.get('story_id'),
                    'url': item.get('url'),
                    'domain': item.get('domain'),
                    'points': item.get('points'),
                    'author': item.get('author'),
                    'age': item.get('age'),
                    'comments': item.get('comments'),
                    'comments_url': item.get('comments_url')
                },
                processor_module='news_scraper',
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
        Full workflow: scrape Hacker News and save to generic tables.
        
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
            job_type="news_scraper",
            status="running",
            started_at=utcnow(),
            job_metadata={'source_id': source_id}
        )
        self.db.add(job)
        self.db.commit()
        
        try:
            # Scrape news
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            raw_html = response.text
            
            news_items = self.scrape_front_page()
            
            # Save to generic tables
            save_result = self.save_to_generic_tables(source, news_items, raw_html)
            
            # Update job status
            job.status = "completed"
            job.completed_at = utcnow()
            job.records_processed = save_result['processed_records']
            self.db.commit()
            
            return {
                'success': True,
                'news_count': len(news_items),
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
            
            logger.error(f"News scraping job failed: {e}")
            raise
    
    def close(self):
        """Close the requests session."""
        self.session.close()


def scrape_news(db: Session, source_id: int) -> Dict:
    """
    Convenience function to scrape Hacker News.
    
    This is the main entry point that gets registered with the ScrapingOrchestrator.
    
    Args:
        db: Database session
        source_id: ID of the source to scrape
        
    Returns:
        Dict: Scraping results
    """
    scraper = HackerNewsScraper(db)
    try:
        return scraper.scrape_and_save(source_id)
    finally:
        scraper.close()
