"""
Tests for news scraper module.

Tests the news scraper functionality including scraping and analysis.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.database import Base
from src.models.tables import Source, ScrapedData, ProcessedData
from src.modules.news_scraper.scraper import HackerNewsScraper, scrape_news
from src.modules.news_scraper.analysis import analyze_headlines
from src.services.scraping_orchestrator import scraping_orchestrator


# Test database setup
@pytest.fixture(scope="function")
def test_db():
    """Create a test database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture
def mock_hn_response():
    """Mock HTML response from Hacker News."""
    return """
    <html>
    <body>
        <table>
            <tr class="athing" id="12345">
                <td>
                    <span class="titleline">
                        <a href="https://example.com/article1">Test Article 1</a>
                        <span class="sitestr">example.com</span>
                    </span>
                </td>
            </tr>
            <tr>
                <td class="subtext">
                    <span class="score">100 points</span>
                    <a class="hnuser">testuser</a>
                    <span class="age">2 hours ago</span>
                    <a>45 comments</a>
                </td>
            </tr>
            <tr class="athing" id="67890">
                <td>
                    <span class="titleline">
                        <a href="https://example.com/article2">Test Article 2</a>
                    </span>
                </td>
            </tr>
            <tr>
                <td class="subtext">
                    <span class="score">50 points</span>
                    <a class="hnuser">anotheruser</a>
                    <span class="age">1 hour ago</span>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


# ==================== Scraper Tests ====================

def test_news_scraper_registered():
    """Test that news scraper is registered with orchestrator."""
    scrapers = scraping_orchestrator.list_available_scrapers()
    assert 'news_scraper' in scrapers


def test_scrape_front_page(test_db, mock_hn_response):
    """Test scraping Hacker News front page."""
    scraper = HackerNewsScraper(test_db)
    
    with patch('requests.Session.get') as mock_get:
        mock_response = Mock()
        mock_response.text = mock_hn_response
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        news_items = scraper.scrape_front_page()
        
        assert len(news_items) == 2
        assert news_items[0]['title'] == 'Test Article 1'
        assert news_items[0]['url'] == 'https://example.com/article1'
        assert news_items[0]['domain'] == 'example.com'
        assert news_items[0]['points'] == '100 points'
        assert news_items[0]['author'] == 'testuser'


def test_save_to_generic_tables(test_db, mock_hn_response):
    """Test saving scraped data to generic tables."""
    # Create a source
    source = Source(
        name="Hacker News",
        url="https://news.ycombinator.com",
        source_type="news",
        module_name="news_scraper",
        is_active=True
    )
    test_db.add(source)
    test_db.commit()
    
    scraper = HackerNewsScraper(test_db)
    
    news_items = [
        {
            'story_id': '12345',
            'title': 'Test Article',
            'url': 'https://example.com/test',
            'points': '100 points',
            'author': 'testuser'
        }
    ]
    
    result = scraper.save_to_generic_tables(source, news_items, mock_hn_response)
    
    assert result['processed_records'] == 1
    assert result['scraped_data_id'] is not None
    
    # Check database
    scraped = test_db.query(ScrapedData).first()
    assert scraped is not None
    assert scraped.source_id == source.id
    
    processed = test_db.query(ProcessedData).first()
    assert processed is not None
    assert processed.title == 'Test Article'
    assert processed.processor_module == 'news_scraper'


def test_scrape_and_save_full_workflow(test_db, mock_hn_response):
    """Test the full scrape and save workflow."""
    # Create a source
    source = Source(
        name="Hacker News",
        url="https://news.ycombinator.com",
        source_type="news",
        module_name="news_scraper",
        is_active=True
    )
    test_db.add(source)
    test_db.commit()
    
    with patch('requests.Session.get') as mock_get:
        mock_response = Mock()
        mock_response.text = mock_hn_response
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = scrape_news(test_db, source.id)
        
        assert result['success'] is True
        assert result['news_count'] == 2
        assert result['processed_records'] == 2
        
        # Verify data in database
        scraped_data = test_db.query(ScrapedData).all()
        assert len(scraped_data) == 1
        
        processed_data = test_db.query(ProcessedData).all()
        assert len(processed_data) == 2


def test_scrape_invalid_source(test_db):
    """Test scraping with invalid source ID."""
    with pytest.raises(ValueError, match="Source with id 99999 not found"):
        scrape_news(test_db, 99999)


# ==================== Analysis Tests ====================

def test_analyze_headlines_no_ai(test_db, mock_hn_response):
    """Test analyzing headlines when AI service is not configured."""
    # Create source and scraped data
    source = Source(
        name="Hacker News",
        url="https://news.ycombinator.com",
        source_type="news",
        module_name="news_scraper",
        is_active=True
    )
    test_db.add(source)
    test_db.commit()
    
    scraped = ScrapedData(
        source_id=source.id,
        url="https://news.ycombinator.com",
        raw_html=mock_hn_response,
        status_code=200
    )
    test_db.add(scraped)
    test_db.commit()
    
    # Add processed data
    processed = ProcessedData(
        scraped_data_id=scraped.id,
        title="Test Headline",
        content_text="Test content",
        processor_module="news_scraper"
    )
    test_db.add(processed)
    test_db.commit()
    
    # Mock AI service as disabled
    with patch('src.modules.news_scraper.analysis.AIService') as mock_ai:
        mock_ai_instance = Mock()
        mock_ai_instance.enabled = False
        mock_ai.return_value = mock_ai_instance
        
        result = analyze_headlines(test_db, scraped.id)
        
        assert result['success'] is True
        assert result['ai_enabled'] is False
        assert result['analyzed_count'] == 1
        
        # Check that neutral sentiment was assigned
        processed = test_db.query(ProcessedData).first()
        assert processed.sentiment_score == 0.0


def test_analyze_headlines_with_ai(test_db, mock_hn_response):
    """Test analyzing headlines with AI enabled."""
    # Create source and scraped data
    source = Source(
        name="Hacker News",
        url="https://news.ycombinator.com",
        source_type="news",
        module_name="news_scraper",
        is_active=True
    )
    test_db.add(source)
    test_db.commit()
    
    scraped = ScrapedData(
        source_id=source.id,
        url="https://news.ycombinator.com",
        raw_html=mock_hn_response,
        status_code=200
    )
    test_db.add(scraped)
    test_db.commit()
    
    # Add processed data
    processed = ProcessedData(
        scraped_data_id=scraped.id,
        title="Amazing Breakthrough in Technology",
        content_text="Test content",
        processor_module="news_scraper"
    )
    test_db.add(processed)
    test_db.commit()
    
    # Mock AI service and langfun
    with patch('src.modules.news_scraper.analysis.AIService') as mock_ai, \
         patch('langfun.query') as mock_query:
        
        mock_ai_instance = Mock()
        mock_ai_instance.enabled = True
        mock_ai.return_value = mock_ai_instance
        
        # Mock langfun response
        mock_query.return_value = '{"sentiment": "positive", "score": 0.8, "reasoning": "Very positive headline"}'
        
        result = analyze_headlines(test_db, scraped.id)
        
        assert result['success'] is True
        assert result['ai_enabled'] is True
        assert result['analyzed_count'] == 1
        
        # Check sentiment was assigned
        processed = test_db.query(ProcessedData).first()
        assert processed.sentiment_score == 0.8
        assert processed.data_metadata['sentiment'] == 'positive'


def test_analyze_invalid_scraped_data(test_db):
    """Test analyzing with invalid scraped_data_id."""
    with pytest.raises(ValueError, match="Scraped data with id 99999 not found"):
        analyze_headlines(test_db, 99999)


def test_analyze_no_processed_data(test_db):
    """Test analyzing when there's no processed data."""
    # Create source and scraped data without processed data
    source = Source(
        name="Hacker News",
        url="https://news.ycombinator.com",
        source_type="news",
        module_name="news_scraper",
        is_active=True
    )
    test_db.add(source)
    test_db.commit()
    
    scraped = ScrapedData(
        source_id=source.id,
        url="https://news.ycombinator.com",
        raw_html="<html></html>",
        status_code=200
    )
    test_db.add(scraped)
    test_db.commit()
    
    result = analyze_headlines(test_db, scraped.id)
    
    assert result['success'] is True
    assert result['analyzed_count'] == 0
