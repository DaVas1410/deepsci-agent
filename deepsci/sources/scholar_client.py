"""
Google Scholar client for additional citation data and paper discovery
"""

from scholarly import scholarly, ProxyGenerator
from typing import List, Dict, Any, Optional
import time
from deepsci.sources.arxiv_client import Paper
from datetime import datetime


class ScholarClient:
    """Client for interacting with Google Scholar"""
    
    def __init__(self, delay_seconds: float = 2.0):
        """
        Initialize Google Scholar client
        
        Args:
            delay_seconds: Delay between requests to be respectful
        """
        self.delay_seconds = delay_seconds
        self.last_request_time = 0
        self._setup_proxy()
    
    def _setup_proxy(self):
        """Setup proxy to avoid rate limiting (optional)"""
        try:
            # Use free ScraperAPI proxy if available
            # For now, just use default without proxy
            pass
        except Exception:
            pass
    
    def _wait_for_rate_limit(self):
        """Ensure we don't make requests too quickly"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)
        self.last_request_time = time.time()
    
    def search_papers(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search Google Scholar for papers
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of paper dictionaries with metadata
        """
        try:
            self._wait_for_rate_limit()
            
            search_query = scholarly.search_pubs(query)
            results = []
            
            for i, pub in enumerate(search_query):
                if i >= max_results:
                    break
                
                try:
                    # Extract citation data
                    paper_data = {
                        'title': pub.get('bib', {}).get('title', 'Unknown'),
                        'authors': pub.get('bib', {}).get('author', []),
                        'abstract': pub.get('bib', {}).get('abstract', ''),
                        'year': pub.get('bib', {}).get('pub_year'),
                        'citation_count': pub.get('num_citations', 0),
                        'url': pub.get('pub_url', pub.get('eprint_url', '')),
                        'venue': pub.get('bib', {}).get('venue', ''),
                        'publisher': pub.get('bib', {}).get('publisher', ''),
                    }
                    
                    results.append(paper_data)
                    
                    # Be respectful with rate limiting
                    self._wait_for_rate_limit()
                    
                except Exception as e:
                    # Skip papers that fail to parse
                    continue
            
            return results
            
        except Exception as e:
            # Return empty list on failure (Scholar can be finicky)
            return []
    
    def enrich_paper_with_scholar(self, paper_title: str) -> Optional[Dict[str, Any]]:
        """
        Enrich paper data with Google Scholar citation metrics
        
        Args:
            paper_title: Title of the paper to search for
            
        Returns:
            Dictionary with Scholar citation data or None
        """
        try:
            self._wait_for_rate_limit()
            
            # Search for the specific paper by title
            search_query = scholarly.search_pubs(paper_title)
            pub = next(search_query, None)
            
            if not pub:
                return None
            
            # Extract enhanced citation data
            scholar_data = {
                'citation_count': pub.get('num_citations', 0),
                'url_citations': pub.get('url_citations', ''),
                'url_related': pub.get('url_related_articles', ''),
                'year': pub.get('bib', {}).get('pub_year'),
                'venue': pub.get('bib', {}).get('venue', ''),
                'publisher': pub.get('bib', {}).get('publisher', ''),
            }
            
            return scholar_data
            
        except Exception:
            return None
    
    def get_author_info(self, author_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an author from Google Scholar
        
        Args:
            author_name: Name of the author
            
        Returns:
            Dictionary with author information or None
        """
        try:
            self._wait_for_rate_limit()
            
            search_query = scholarly.search_author(author_name)
            author = next(search_query, None)
            
            if not author:
                return None
            
            # Fill in author details
            author = scholarly.fill(author)
            
            return {
                'name': author.get('name', ''),
                'affiliation': author.get('affiliation', ''),
                'citations': author.get('citedby', 0),
                'h_index': author.get('hindex', 0),
                'i10_index': author.get('i10index', 0),
                'interests': author.get('interests', []),
            }
            
        except Exception:
            return None
    
    def get_cited_by(self, paper_title: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Get papers that cite a given paper
        
        Args:
            paper_title: Title of the paper
            max_results: Maximum number of citing papers to return
            
        Returns:
            List of citing papers
        """
        try:
            self._wait_for_rate_limit()
            
            # Find the paper
            search_query = scholarly.search_pubs(paper_title)
            pub = next(search_query, None)
            
            if not pub or not pub.get('url_citations'):
                return []
            
            # Get citing articles
            citing_papers = []
            
            # Note: This requires additional API calls
            # For now, return empty list to avoid excessive requests
            # Can be implemented later if needed
            
            return citing_papers
            
        except Exception:
            return []
