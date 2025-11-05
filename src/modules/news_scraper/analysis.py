"""
News Analyzer - Sentiment Analysis for Headlines.

This module analyzes news headlines using AI to perform sentiment analysis.
It demonstrates the platform's generic analysis pipeline capabilities.
"""

import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from src.models.tables import ProcessedData, ScrapedData
from src.services.ai_service import AIService
from src.core.utils import utcnow

logger = logging.getLogger(__name__)


def analyze_headlines(db: Session, scraped_data_id: int) -> Dict:
    """
    Analyze news headlines using AI sentiment analysis.
    
    This function retrieves scraped news data, extracts headlines,
    and uses the Google Gemini AI service to perform sentiment analysis
    on each headline.
    
    Args:
        db: Database session
        scraped_data_id: ID of the scraped data to analyze
        
    Returns:
        Dict: Analysis results with sentiment scores
    """
    # Get the scraped data
    scraped = db.query(ScrapedData).filter_by(id=scraped_data_id).first()
    if not scraped:
        raise ValueError(f"Scraped data with id {scraped_data_id} not found")
    
    # Get all processed data items for this scraped data
    processed_items = db.query(ProcessedData).filter_by(
        scraped_data_id=scraped_data_id
    ).all()
    
    if not processed_items:
        logger.warning(f"No processed data found for scraped_data_id {scraped_data_id}")
        return {
            'success': True,
            'message': 'No headlines to analyze',
            'analyzed_count': 0
        }
    
    # Initialize AI service
    ai_service = AIService()
    
    if not ai_service.enabled:
        logger.warning("AI service not enabled - skipping sentiment analysis")
        # Still mark as analyzed but with no sentiment
        for item in processed_items:
            item.sentiment_score = 0.0
            item.data_metadata = item.data_metadata or {}
            item.data_metadata['sentiment'] = 'neutral'
            item.data_metadata['sentiment_note'] = 'AI service not configured'
        db.commit()
        
        return {
            'success': True,
            'message': 'AI service not configured - marked as neutral',
            'analyzed_count': len(processed_items),
            'ai_enabled': False
        }
    
    # Analyze each headline
    analyzed_count = 0
    errors = []
    
    for item in processed_items:
        try:
            # Prepare headline for analysis
            headline = item.title or "Untitled"
            
            # Use AI to analyze sentiment
            # We'll ask Gemini to classify sentiment and provide a score
            import langfun as lf
            
            prompt = f"""Analyze the sentiment of this news headline: "{headline}"

Respond with ONLY a JSON object in this format:
{{"sentiment": "positive|negative|neutral", "score": 0.0-1.0, "reasoning": "brief explanation"}}

Where score ranges from:
- 0.0-0.3: Very negative
- 0.3-0.5: Slightly negative
- 0.5: Neutral
- 0.5-0.7: Slightly positive
- 0.7-1.0: Very positive
"""
            
            try:
                response = lf.query(
                    prompt,
                    lm=lf.llms.GeminiPro()
                )
                
                # Parse the response
                import json
                response_str = str(response).strip()
                
                # Try to extract JSON from the response
                if '{' in response_str and '}' in response_str:
                    json_start = response_str.index('{')
                    json_end = response_str.rindex('}') + 1
                    json_str = response_str[json_start:json_end]
                    result = json.loads(json_str)
                    
                    sentiment = result.get('sentiment', 'neutral')
                    score = float(result.get('score', 0.5))
                    reasoning = result.get('reasoning', '')
                    
                    # Update the processed data with sentiment information
                    item.sentiment_score = score
                    item.data_metadata = item.data_metadata or {}
                    item.data_metadata['sentiment'] = sentiment
                    item.data_metadata['sentiment_reasoning'] = reasoning
                    
                    analyzed_count += 1
                    
                else:
                    # If we can't parse JSON, assign neutral
                    item.sentiment_score = 0.5
                    item.data_metadata = item.data_metadata or {}
                    item.data_metadata['sentiment'] = 'neutral'
                    item.data_metadata['sentiment_note'] = 'Could not parse AI response'
                    
            except Exception as ai_error:
                logger.warning(f"AI analysis failed for headline '{headline}': {ai_error}")
                # Assign neutral on error
                item.sentiment_score = 0.5
                item.data_metadata = item.data_metadata or {}
                item.data_metadata['sentiment'] = 'neutral'
                item.data_metadata['sentiment_error'] = str(ai_error)
                errors.append({
                    'headline': headline,
                    'error': str(ai_error)
                })
                
        except Exception as e:
            logger.error(f"Error analyzing item {item.id}: {e}")
            errors.append({
                'item_id': item.id,
                'error': str(e)
            })
    
    # Commit all updates
    db.commit()
    
    return {
        'success': True,
        'message': f'Analyzed {analyzed_count} headlines',
        'analyzed_count': analyzed_count,
        'total_items': len(processed_items),
        'error_count': len(errors),
        'errors': errors if errors else None,
        'ai_enabled': True
    }


def bulk_analyze_source(db: Session, source_id: int) -> Dict:
    """
    Analyze all scraped data for a news source.
    
    This is a convenience function that analyzes all scraped data
    for a given source.
    
    Args:
        db: Database session
        source_id: ID of the source
        
    Returns:
        Dict: Bulk analysis results
    """
    from src.models.tables import Source
    
    # Get source
    source = db.query(Source).filter_by(id=source_id).first()
    if not source:
        raise ValueError(f"Source with id {source_id} not found")
    
    # Get all scraped data for this source
    scraped_items = db.query(ScrapedData).filter_by(source_id=source_id).all()
    
    if not scraped_items:
        return {
            'success': True,
            'message': 'No scraped data found for this source',
            'analyzed_count': 0
        }
    
    # Analyze each scraped data
    total_analyzed = 0
    results = []
    
    for scraped in scraped_items:
        try:
            result = analyze_headlines(db, scraped.id)
            total_analyzed += result.get('analyzed_count', 0)
            results.append({
                'scraped_data_id': scraped.id,
                'result': result
            })
        except Exception as e:
            logger.error(f"Error analyzing scraped_data {scraped.id}: {e}")
            results.append({
                'scraped_data_id': scraped.id,
                'error': str(e)
            })
    
    return {
        'success': True,
        'source_id': source_id,
        'source_name': source.name,
        'total_scraped_items': len(scraped_items),
        'total_analyzed': total_analyzed,
        'results': results
    }
