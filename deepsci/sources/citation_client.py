"""
Semantic Scholar API client for citation metrics and paper enrichment
"""

from semanticscholar import SemanticScholar
from typing import Optional, Dict, Any
import time


class CitationClient:
    """Client for fetching citation metrics from Semantic Scholar"""
    
    def __init__(self, delay_seconds: float = 1.0):
        """
        Initialize citation client
        
        Args:
            delay_seconds: Delay between API requests
        """
        self.sch = SemanticScholar(timeout=10)
        self.delay_seconds = delay_seconds
        self.last_request_time = 0
    
    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)
        self.last_request_time = time.time()
    
    def get_citations_by_arxiv_id(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """
        Get citation metrics for a paper by arXiv ID
        
        Args:
            arxiv_id: arXiv ID (e.g., '2301.12345')
            
        Returns:
            Dictionary with citation metrics or None if not found
        """
        try:
            # Clean arxiv ID
            arxiv_id = arxiv_id.replace('arxiv:', '').replace('arXiv:', '')
            
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
                return None
            
            return {
                'citation_count': paper.citationCount or 0,
                'influential_citations': paper.influentialCitationCount or 0,
                'reference_count': paper.referenceCount or 0,
                'year': paper.year,
                'fields': paper.fieldsOfStudy or [],
                'venue': paper.publicationVenue.get('name') if paper.publicationVenue else None,
                's2_fields': [f.get('category') for f in (paper.s2FieldsOfStudy or [])],
            }
            
        except Exception as e:
            # Silently fail for citation lookup
            # Papers might not be in Semantic Scholar database
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
