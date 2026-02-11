"""
arXiv API client for searching and retrieving physics papers
"""

import arxiv
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Paper:
    """Represents a research paper"""
    id: str
    title: str
    authors: List[str]
    abstract: str
    published: datetime
    updated: datetime
    url: str
    pdf_url: str
    categories: List[str]
    citation_count: int = 0
    influential_citations: int = 0
    source: str = "arxiv"
    
    def __str__(self) -> str:
        authors_str = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            authors_str += f" et al. ({len(self.authors)} authors)"
        citations = f" | {self.citation_count} citations" if self.citation_count > 0 else ""
        return f"{self.title}\n{authors_str}\n{self.published.year}{citations} | {self.url}"


class ArxivClient:
    """Client for interacting with arXiv API with rate limiting"""
    
    def __init__(self, max_results: int = 10, delay_seconds: float = 3.0):
        """
        Initialize arXiv client
        
        Args:
            max_results: Default maximum results per query
            delay_seconds: Delay between requests (arXiv recommends 3+ seconds)
        """
        self.max_results = max_results
        self.delay_seconds = delay_seconds
        self.client = arxiv.Client(
            page_size=100,
            delay_seconds=delay_seconds,
            num_retries=3
        )
        self.last_request_time = 0
    
    def _wait_for_rate_limit(self):
        """Ensure we don't exceed arXiv's rate limit"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)
        self.last_request_time = time.time()
    
    def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        sort_by: arxiv.SortCriterion = arxiv.SortCriterion.Relevance,
        categories: Optional[List[str]] = None,
        fetch_citations: bool = False
    ) -> List[Paper]:
        """
        Search arXiv for papers matching the query
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            sort_by: Sort criterion (Relevance, LastUpdatedDate, SubmittedDate)
            categories: Filter by arXiv categories (e.g., ['physics.quant-ph'])
            fetch_citations: Whether to fetch citation counts (slower)
        
        Returns:
            List of Paper objects
        """
        if max_results is None:
            max_results = self.max_results
        
        # Add category filter to query if specified
        if categories:
            cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
            query = f"({query}) AND ({cat_query})"
        
        # Wait to respect rate limit
        self._wait_for_rate_limit()
        
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_by
        )
        
        papers = []
        try:
            for result in self.client.results(search):
                paper = Paper(
                    id=result.entry_id.split('/')[-1],
                    title=result.title,
                    authors=[author.name for author in result.authors],
                    abstract=result.summary,
                    published=result.published,
                    updated=result.updated,
                    url=result.entry_id,
                    pdf_url=result.pdf_url,
                    categories=result.categories,
                    source="arxiv"
                )
                papers.append(paper)
        except Exception as e:
            # Re-raise with more helpful message
            if "429" in str(e):
                raise Exception(
                    "arXiv rate limit exceeded. Please wait a moment and try again. "
                    "The system will automatically retry with delays."
                )
            raise
        
        # Fetch citations if requested
        if fetch_citations and papers:
            papers = self._enrich_with_citations(papers)
        
        return papers
    
    def _enrich_with_citations(self, papers: List[Paper]) -> List[Paper]:
        """
        Enrich papers with citation data from Semantic Scholar (PARALLEL)
        
        Args:
            papers: List of Paper objects
            
        Returns:
            Papers with citation counts added
        """
        from deepsci.sources.citation_client import CitationClient
        import concurrent.futures
        from rich.progress import Progress, SpinnerColumn, TextColumn
        
        citation_client = CitationClient()
        
        def fetch_citation(paper):
            """Fetch citation for a single paper"""
            try:
                # Pass paper title for Google Scholar fallback
                metrics = citation_client.get_citations_by_arxiv_id(
                    paper.id, 
                    paper_title=paper.title,
                    retry_count=1  # Reduce retries for parallel processing speed
                )
                if metrics:
                    paper.citation_count = metrics['citation_count']
                    paper.influential_citations = metrics['influential_citations']
            except Exception as e:
                # Still fail gracefully but at least we tried harder
                pass
            return paper
        
        # Use thread pool for parallel fetching
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            papers = list(executor.map(fetch_citation, papers))
        
        # Print stats for debugging (optional)
        if papers and citation_client.stats['total_attempts'] > 0:
            success_rate = (citation_client.stats['semantic_scholar_success'] / 
                          citation_client.stats['total_attempts'] * 100)
            # Only show if there were issues
            if success_rate < 80:
                from rich.console import Console
                console = Console()
                console.print(f"[dim]  Citation fetch: {citation_client.stats['semantic_scholar_success']}/{citation_client.stats['total_attempts']} success, "
                            f"{citation_client.stats['scholar_fallback_used']} from Scholar[/dim]")
        
        return papers
    
    def get_paper(self, paper_id: str) -> Optional[Paper]:
        """
        Get a specific paper by its arXiv ID
        
        Args:
            paper_id: arXiv paper ID (e.g., '2301.12345' or 'arxiv:2301.12345')
        
        Returns:
            Paper object or None if not found
        """
        # Clean up paper ID
        paper_id = paper_id.replace('arxiv:', '').replace('arXiv:', '')
        
        # Wait to respect rate limit
        self._wait_for_rate_limit()
        
        search = arxiv.Search(id_list=[paper_id])
        
        try:
            result = next(self.client.results(search))
            return Paper(
                id=result.entry_id.split('/')[-1],
                title=result.title,
                authors=[author.name for author in result.authors],
                abstract=result.summary,
                published=result.published,
                updated=result.updated,
                url=result.entry_id,
                pdf_url=result.pdf_url,
                categories=result.categories
            )
        except StopIteration:
            return None
        except Exception as e:
            if "429" in str(e):
                raise Exception(
                    "arXiv rate limit exceeded. Please wait a moment and try again."
                )
            raise
    
    def download_pdf(self, paper: Paper, directory: str = "./downloads") -> str:
        """
        Download the PDF of a paper
        
        Args:
            paper: Paper object to download
            directory: Directory to save the PDF
        
        Returns:
            Path to the downloaded PDF
        """
        import os
        os.makedirs(directory, exist_ok=True)
        
        # Wait to respect rate limit
        self._wait_for_rate_limit()
        
        # Create a safe filename
        safe_title = "".join(c for c in paper.title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title[:100]  # Limit length
        filename = f"{paper.id}_{safe_title}.pdf"
        filepath = os.path.join(directory, filename)
        
        try:
            # Download using arxiv library
            search = arxiv.Search(id_list=[paper.id])
            result = next(self.client.results(search))
            result.download_pdf(dirpath=directory, filename=filename)
            
            return filepath
        except Exception as e:
            if "429" in str(e):
                raise Exception(
                    "arXiv rate limit exceeded. Please wait and try again."
                )
            raise
