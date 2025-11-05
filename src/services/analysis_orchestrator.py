"""
Generic analysis orchestrator service.

This orchestrator can apply different analysis pipelines to processed data
based on the module/source type.
"""

import logging
from typing import Dict, Optional, Callable, List
from sqlalchemy.orm import Session

from src.models.tables import ProcessedData, Source

logger = logging.getLogger(__name__)


class AnalysisOrchestrator:
    """
    Orchestrator for managing different analysis modules.
    
    This allows the platform to support multiple analysis strategies
    without hardcoding specific implementations.
    """
    
    def __init__(self):
        """Initialize the analysis orchestrator."""
        self._analyzers: Dict[str, Callable] = {}
    
    def register_analyzer(self, module_name: str, analyzer_func: Callable):
        """
        Register an analyzer function for a module.
        
        Args:
            module_name: Name of the module (e.g., 'openhpi', 'generic_sentiment')
            analyzer_func: Function that takes (db: Session, processed_data_id: int) and returns Dict
        """
        self._analyzers[module_name] = analyzer_func
        logger.info(f"Registered analyzer for module: {module_name}")
    
    def get_analyzer(self, module_name: str) -> Optional[Callable]:
        """
        Get an analyzer function by module name.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Analyzer function or None if not found
        """
        return self._analyzers.get(module_name)
    
    def list_available_analyzers(self) -> list:
        """
        List all registered analyzers.
        
        Returns:
            List of module names
        """
        return list(self._analyzers.keys())
    
    def analyze_data(
        self, 
        db: Session, 
        processed_data_id: int,
        analyzer_module: Optional[str] = None
    ) -> Dict:
        """
        Analyze processed data using the appropriate module.
        
        Args:
            db: Database session
            processed_data_id: ID of the processed data to analyze
            analyzer_module: Optional specific analyzer to use. If None, uses source's module
            
        Returns:
            Dict: Analysis results
            
        Raises:
            ValueError: If data not found or analyzer not available
        """
        # Get processed data
        processed = db.query(ProcessedData).filter_by(id=processed_data_id).first()
        if not processed:
            raise ValueError(f"Processed data with id {processed_data_id} not found")
        
        # Determine which analyzer to use
        if analyzer_module:
            module_name = analyzer_module
        else:
            # Use the processor module that created this data
            module_name = processed.processor_module
        
        # Get analyzer
        analyzer_func = self.get_analyzer(module_name)
        if not analyzer_func:
            raise ValueError(
                f"No analyzer registered for module '{module_name}'. "
                f"Available: {self.list_available_analyzers()}"
            )
        
        # Execute analysis
        logger.info(f"Analyzing data {processed_data_id} using module '{module_name}'")
        try:
            result = analyzer_func(db, processed_data_id)
            logger.info(f"Successfully analyzed data {processed_data_id}")
            return result
        except Exception as e:
            logger.error(f"Error analyzing data {processed_data_id}: {e}")
            raise
    
    def bulk_analyze(
        self,
        db: Session,
        source_id: int,
        analyzer_module: Optional[str] = None
    ) -> Dict:
        """
        Analyze all processed data for a source.
        
        Args:
            db: Database session
            source_id: ID of the source
            analyzer_module: Optional specific analyzer to use
            
        Returns:
            Dict: Bulk analysis results
        """
        # Get source
        source = db.query(Source).filter_by(id=source_id).first()
        if not source:
            raise ValueError(f"Source with id {source_id} not found")
        
        # Get all processed data for this source
        processed_items = db.query(ProcessedData).join(
            ProcessedData.scraped_data
        ).filter(
            ProcessedData.scraped_data.has(source_id=source_id)
        ).all()
        
        if not processed_items:
            return {
                'success': True,
                'message': 'No processed data found for this source',
                'analyzed_count': 0
            }
        
        # Analyze each item
        results = []
        errors = []
        
        for item in processed_items:
            try:
                result = self.analyze_data(db, item.id, analyzer_module)
                results.append({
                    'processed_data_id': item.id,
                    'result': result
                })
            except Exception as e:
                errors.append({
                    'processed_data_id': item.id,
                    'error': str(e)
                })
        
        return {
            'success': True,
            'source_id': source_id,
            'source_name': source.name,
            'total_items': len(processed_items),
            'analyzed_count': len(results),
            'error_count': len(errors),
            'results': results,
            'errors': errors
        }


# Global orchestrator instance
analysis_orchestrator = AnalysisOrchestrator()
