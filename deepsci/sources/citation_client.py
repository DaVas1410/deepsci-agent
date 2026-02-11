"""
Semantic Scholar API client for citation metrics and paper enrichment
Enhanced with retry logic, fallback to Google Scholar, caching, and better error handling
"""

from semanticscholar import SemanticScholar
from typing import Optional, Dict, Any
import time
import logging
from deepsci.sources.citation_cache import CitationCache

# Set up logging for debugging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class CitationClient:
    """Client for fetching citation metrics from Semantic Scholar with fallbacks"""
    
    def __init__(self, delay_seconds: float = 1.0, use_scholar_fallback: bool = True, use_cache: bool = True):
        """
        Initialize citation client
        
        Args:
            delay_seconds: Delay between API requests
            use_scholar_fallback: Whether to use Google Scholar as fallback
            use_cache: Whether to cache citation data
        """
        self.sch = SemanticScholar(timeout=8)  # Increased timeout
        self.delay_seconds = delay_seconds
        self.last_request_time = 0
        self.use_scholar_fallback = use_scholar_fallback
        self.scholar_client = None
        self.use_cache = use_cache
        self.cache = CitationCache() if use_cache else None
        
        # Statistics for debugging
        self.stats = {
            'semantic_scholar_success': 0,
            'semantic_scholar_fail': 0,
            'scholar_fallback_used': 0,
            'cache_hits': 0,
            'total_attempts': 0
        }
    
    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)
        self.last_request_time = time.time()
    
    def _get_scholar_fallback(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Fallback to Google Scholar for citation counts
        
        Args:
            title: Paper title
            
        Returns:
            Dictionary with citation metrics or None
        """
        if not self.use_scholar_fallback:
            return None
        
        try:
            # Lazy import to avoid loading if not needed
            if self.scholar_client is None:
                from deepsci.sources.scholar_client import ScholarClient
                self.scholar_client = ScholarClient()
            
            data = self.scholar_client.enrich_paper_with_scholar(title)
            if data and data.get('citation_count', 0) > 0:
                self.stats['scholar_fallback_used'] += 1
                return {
                    'citation_count': data['citation_count'],
                    'influential_citations': 0,  # Scholar doesn't provide this
                    'reference_count': 0,
                    'year': data.get('year'),
                    'fields': [],
                    'venue': data.get('venue'),
                    's2_fields': [],
                }
            return None
        except Exception as e:
            logger.debug(f"Scholar fallback failed: {e}")
            return None
    
    def get_citations_by_arxiv_id(self, arxiv_id: str, paper_title: str = None, retry_count: int = 2) -> Optional[Dict[str, Any]]:
        """
        Get citation metrics for a paper by arXiv ID with retry logic
        
        Args:
            arxiv_id: arXiv ID (e.g., '2301.12345')
            paper_title: Paper title for fallback lookup
            retry_count: Number of retries on failure
            
        Returns:
            Dictionary with citation metrics or None if not found
        """
        self.stats['total_attempts'] += 1
        
        # Clean arxiv ID
        arxiv_id = arxiv_id.replace('arxiv:', '').replace('arXiv:', '').replace('v1', '').replace('v2', '').replace('v3', '')
        
        # Check cache first
        if self.cache:
            cached = self.cache.get(arxiv_id)
            if cached:
                self.stats['cache_hits'] += 1
                return cached
        
        # Try Semantic Scholar with retries
        for attempt in range(retry_count + 1):
            try:
                self._wait_for_rate_limit()
                
                # Search by arXiv ID
                paper = self.sch.get_paper(f'arXiv:{arxiv_id}', fields=[
                    'citationCount',
                    'influentialCitationCount',
                    'referenceCount',
                    'year',
                    'fieldsOfStudy',
                    'publicationVenue',
                    's2FieldsOfStudy'
                ])
                
                if not paper:
                    logger.debug(f"Paper not found in Semantic Scholar: {arxiv_id}")
                    continue
                
                self.stats['semantic_scholar_success'] += 1
                
                result = {
                    'citation_count': paper.citationCount or 0,
                    'influential_citations': paper.influentialCitationCount or 0,
                    'reference_count': paper.referenceCount or 0,
                    'year': paper.year,
                    'fields': paper.fieldsOfStudy or [],
                    'venue': paper.publicationVenue.get('name') if paper.publicationVenue else None,
                    's2_fields': [f.get('category') for f in (paper.s2FieldsOfStudy or [])],
                }
                
                # Cache the result
                if self.cache:
                    self.cache.set(arxiv_id, result)
                
                return result
                
            except Exception as e:
                logger.debug(f"Semantic Scholar attempt {attempt + 1} failed for {arxiv_id}: {str(e)[:100]}")
                if attempt < retry_count:
                    time.sleep(1 * (attempt + 1))  # Exponential backoff
                continue
        
        # All Semantic Scholar attempts failed
        self.stats['semantic_scholar_fail'] += 1
        
        # Try Google Scholar fallback if we have a title
        if paper_title and self.use_scholar_fallback:
            logger.debug(f"Trying Scholar fallback for: {paper_title[:50]}")
            result = self._get_scholar_fallback(paper_title)
            
            # Cache Scholar result too
            if result and self.cache:
                self.cache.set(arxiv_id, result)
            
            return result
        
        return None
    
    def get_citations_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Get citation metrics for a paper by DOI
        
        Args:
            doi: Digital Object Identifier
            
        Returns:
            Dictionary with citation metrics or None if not found
        """
        try:
            self._wait_for_rate_limit()
            
            paper = self.sch.get_paper(f'DOI:{doi}', fields=[
                'citationCount',
                'influentialCitationCount',
                'referenceCount'
            ])
            
            if not paper:
                return None
            
            return {
                'citation_count': paper.citationCount or 0,
                'influential_citations': paper.influentialCitationCount or 0,
                'reference_count': paper.referenceCount or 0,
            }
            
        except Exception:
            return None
    
    def search_paper(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Search for a paper by title and get citation metrics
        
        Args:
            title: Paper title
            
        Returns:
            Dictionary with citation metrics or None if not found
        """
        try:
            self._wait_for_rate_limit()
            
            results = self.sch.search_paper(title, limit=1, fields=[
                'citationCount',
                'influentialCitationCount',
                'referenceCount',
                'year'
            ])
            
            if not results or len(results) == 0:
                return None
            
            paper = results[0]
            
            return {
                'citation_count': paper.citationCount or 0,
                'influential_citations': paper.influentialCitationCount or 0,
                'reference_count': paper.referenceCount or 0,
                'year': paper.year,
            }
            
        except Exception:
            return None
    
    def get_citation_velocity(self, arxiv_id: str) -> Optional[float]:
        """
        Calculate citation velocity (citations per year)
        
        Args:
            arxiv_id: arXiv ID
            
        Returns:
            Citations per year or None
        """
        metrics = self.get_citations_by_arxiv_id(arxiv_id)
        
        if not metrics or not metrics.get('year'):
            return None
        
        from datetime import datetime
        current_year = datetime.now().year
        years_since_publication = max(1, current_year - metrics['year'])
        
        return metrics['citation_count'] / years_since_publication
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about citation fetching
        
        Returns:
            Dictionary with success/failure counts
        """
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset statistics counters"""
        self.stats = {
            'semantic_scholar_success': 0,
            'semantic_scholar_fail': 0,
            'scholar_fallback_used': 0,
            'total_attempts': 0
        }
