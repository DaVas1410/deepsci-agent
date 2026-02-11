"""
arXiv API client for searching and retrieving physics papers
"""

import arxiv
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
    
    def __str__(self) -> str:
        authors_str = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            authors_str += f" et al. ({len(self.authors)} authors)"
        return f"{self.title}\n{authors_str}\n{self.published.year} | {self.url}"


class ArxivClient:
    """Client for interacting with arXiv API"""
    
    def __init__(self, max_results: int = 10):
        self.max_results = max_results
        self.client = arxiv.Client()
    
    def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        sort_by: arxiv.SortCriterion = arxiv.SortCriterion.Relevance,
        categories: Optional[List[str]] = None
    ) -> List[Paper]:
        """
        Search arXiv for papers matching the query
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            sort_by: Sort criterion (Relevance, LastUpdatedDate, SubmittedDate)
            categories: Filter by arXiv categories (e.g., ['physics.quant-ph'])
        
        Returns:
            List of Paper objects
        """
        if max_results is None:
            max_results = self.max_results
        
        # Add category filter to query if specified
        if categories:
            cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
            query = f"({query}) AND ({cat_query})"
        
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=sort_by
        )
        
        papers = []
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
                categories=result.categories
            )
            papers.append(paper)
        
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
        
        # Create a safe filename
        safe_title = "".join(c for c in paper.title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title[:100]  # Limit length
        filename = f"{paper.id}_{safe_title}.pdf"
        filepath = os.path.join(directory, filename)
        
        # Download using arxiv library
        search = arxiv.Search(id_list=[paper.id])
        result = next(self.client.results(search))
        result.download_pdf(dirpath=directory, filename=filename)
        
        return filepath
