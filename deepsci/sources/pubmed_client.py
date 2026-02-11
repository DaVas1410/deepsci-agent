"""
PubMed E-utilities client for biomedical and biophysics literature
"""

from Bio import Entrez
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import time


@dataclass
class PubMedPaper:
    """Represents a PubMed paper"""
    pmid: str
    title: str
    authors: List[str]
    abstract: str
    journal: str
    published_date: str
    doi: Optional[str]
    url: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.pmid,
            'title': self.title,
            'authors': self.authors,
            'abstract': self.abstract,
            'journal': self.journal,
            'published': self.published_date,
            'doi': self.doi,
            'url': self.url,
            'source': 'pubmed'
        }


class PubMedClient:
    """Client for interacting with PubMed E-utilities API"""
    
    def __init__(self, email: str = "deepsci@example.com", delay_seconds: float = 0.34):
        """
        Initialize PubMed client
        
        Args:
            email: Email for NCBI (required by their policy)
            delay_seconds: Delay between requests (NCBI recommends max 3 requests/sec)
        """
        Entrez.email = email
        self.delay_seconds = delay_seconds
        self.last_request_time = 0
    
    def _wait_for_rate_limit(self):
        """Ensure we don't exceed NCBI rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)
        self.last_request_time = time.time()
    
    def search(self, query: str, max_results: int = 10, sort: str = "relevance") -> List[PubMedPaper]:
        """
        Search PubMed for papers
        
        Args:
            query: Search query
            max_results: Maximum number of results
            sort: Sort order (relevance, date, first_author)
            
        Returns:
            List of PubMedPaper objects
        """
        papers = []
        
        try:
            # Search for PMIDs
            self._wait_for_rate_limit()
            search_handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=max_results,
                sort=sort
            )
            search_results = Entrez.read(search_handle)
            search_handle.close()
            
            pmids = search_results.get("IdList", [])
            
            if not pmids:
                return []
            
            # Fetch paper details
            self._wait_for_rate_limit()
            fetch_handle = Entrez.efetch(
                db="pubmed",
                id=pmids,
                rettype="medline",
                retmode="xml"
            )
            fetch_results = Entrez.read(fetch_handle)
            fetch_handle.close()
            
            # Parse results
            for article in fetch_results.get('PubmedArticle', []):
                try:
                    medline = article.get('MedlineCitation', {})
                    pmid = str(medline.get('PMID', ''))
                    
                    article_data = medline.get('Article', {})
                    
                    # Extract title
                    title = article_data.get('ArticleTitle', 'No title')
                    
                    # Extract authors
                    authors_list = article_data.get('AuthorList', [])
                    authors = []
                    for author in authors_list:
                        if 'LastName' in author and 'ForeName' in author:
                            authors.append(f"{author['ForeName']} {author['LastName']}")
                        elif 'CollectiveName' in author:
                            authors.append(author['CollectiveName'])
                    
                    # Extract abstract
                    abstract_data = article_data.get('Abstract', {})
                    abstract_texts = abstract_data.get('AbstractText', [])
                    if isinstance(abstract_texts, list):
                        abstract = ' '.join(str(text) for text in abstract_texts)
                    else:
                        abstract = str(abstract_texts) if abstract_texts else 'No abstract available'
                    
                    # Extract journal
                    journal_data = article_data.get('Journal', {})
                    journal = journal_data.get('Title', 'Unknown journal')
                    
                    # Extract publication date
                    pub_date = article_data.get('ArticleDate', [{}])
                    if pub_date and len(pub_date) > 0:
                        year = pub_date[0].get('Year', '')
                        month = pub_date[0].get('Month', '01')
                        day = pub_date[0].get('Day', '01')
                        published_date = f"{year}-{month}-{day}"
                    else:
                        # Fallback to journal issue date
                        journal_issue = journal_data.get('JournalIssue', {})
                        pub_date_fallback = journal_issue.get('PubDate', {})
                        year = pub_date_fallback.get('Year', 'Unknown')
                        published_date = str(year)
                    
                    # Extract DOI
                    doi = None
                    article_ids = article.get('PubmedData', {}).get('ArticleIdList', [])
                    for aid in article_ids:
                        if aid.attributes.get('IdType') == 'doi':
                            doi = str(aid)
                            break
                    
                    # Create paper object
                    paper = PubMedPaper(
                        pmid=pmid,
                        title=title,
                        authors=authors,
                        abstract=abstract,
                        journal=journal,
                        published_date=published_date,
                        doi=doi,
                        url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    )
                    
                    papers.append(paper)
                    
                except Exception as e:
                    # Skip malformed entries
                    continue
            
        except Exception as e:
            raise Exception(f"PubMed search error: {str(e)}")
        
        return papers
    
    def get_paper(self, pmid: str) -> Optional[PubMedPaper]:
        """
        Get a specific paper by PMID
        
        Args:
            pmid: PubMed ID
            
        Returns:
            PubMedPaper object or None
        """
        results = self.search(f"{pmid}[PMID]", max_results=1)
        return results[0] if results else None
