"""
Generic scraping orchestrator service.

This orchestrator can load and run different scraping modules based on source type.
It provides a unified interface for scraping any type of data source.
"""

import logging
from typing import Dict, Optional, Callable
from sqlalchemy.orm import Session

from src.models.tables import Source

logger = logging.getLogger(__name__)


class ScrapingOrchestrator:
    """
    Orchestrator for managing different scraping modules.
    
    This allows the platform to support multiple data sources and scraping
    strategies without hardcoding specific implementations.
    """
    
    def __init__(self):
        """Initialize the scraping orchestrator."""
        self._scrapers: Dict[str, Callable] = {}
        self._register_default_scrapers()
    
    def _register_default_scrapers(self):
        """Register default scrapers (built-in modules)."""
        try:
            from src.modules.openhpi.public_scraper import scrape_openhpi_public
            self.register_scraper('openhpi_public', scrape_openhpi_public)
            logger.info("Registered OpenHPI public scraper")
        except ImportError as e:
            logger.warning(f"Could not register OpenHPI public scraper: {e}")
    
    def register_scraper(self, module_name: str, scraper_func: Callable):
        """
        Register a scraper function for a module.
        
        Args:
            module_name: Name of the module (e.g., 'openhpi_public', 'generic')
            scraper_func: Function that takes (db: Session, source_id: int) and returns Dict
        """
        self._scrapers[module_name] = scraper_func
        logger.info(f"Registered scraper for module: {module_name}")
    
    def get_scraper(self, module_name: str) -> Optional[Callable]:
        """
        Get a scraper function by module name.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Scraper function or None if not found
        """
        return self._scrapers.get(module_name)
    
    def list_available_scrapers(self) -> list:
        """
        List all registered scrapers.
        
        Returns:
            List of module names
        """
        return list(self._scrapers.keys())
    
    def scrape_source(self, db: Session, source_id: int) -> Dict:
        """
        Scrape a data source using the appropriate module.
        
        Args:
            db: Database session
            source_id: ID of the source to scrape
            
        Returns:
            Dict: Scraping results
            
        Raises:
            ValueError: If source not found or module not registered
        """
        # Get source
        source = db.query(Source).filter_by(id=source_id).first()
        if not source:
            raise ValueError(f"Source with id {source_id} not found")
        
        if not source.is_active:
            raise ValueError(f"Source {source.name} is not active")
        
        # Get scraper for this module
        scraper_func = self.get_scraper(source.module_name)
        if not scraper_func:
            raise ValueError(
                f"No scraper registered for module '{source.module_name}'. "
                f"Available: {self.list_available_scrapers()}"
            )
        
        # Execute scraping
        logger.info(f"Scraping source '{source.name}' using module '{source.module_name}'")
        try:
            result = scraper_func(db, source_id)
            logger.info(f"Successfully scraped source '{source.name}'")
            return result
        except Exception as e:
            logger.error(f"Error scraping source '{source.name}': {e}")
            raise


# Global orchestrator instance
scraping_orchestrator = ScrapingOrchestrator()
