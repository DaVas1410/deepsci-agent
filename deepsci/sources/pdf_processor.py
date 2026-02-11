"""
PDF processing module for downloading and extracting text from research papers
"""

import os
import requests
from pathlib import Path
from typing import Optional, Dict, Any
import fitz  # PyMuPDF
from rich.console import Console

console = Console()


class PDFProcessor:
    """Download and process PDF files from arXiv and other sources"""
    
    def __init__(self, cache_dir: str = "./data/pdfs"):
        """
        Initialize PDF processor
        
        Args:
            cache_dir: Directory to cache downloaded PDFs
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def download_pdf(self, url: str, paper_id: str, force_download: bool = False) -> Optional[Path]:
        """
        Download PDF from URL
        
        Args:
            url: URL of the PDF
            paper_id: Unique identifier for the paper (used for filename)
            force_download: Force re-download even if cached
            
        Returns:
            Path to downloaded PDF or None if failed
        """
        # Sanitize paper_id for filename
        safe_id = paper_id.replace('/', '_').replace(':', '_')
        pdf_path = self.cache_dir / f"{safe_id}.pdf"
        
        # Check cache
        if pdf_path.exists() and not force_download:
            return pdf_path
        
        try:
            console.print(f"[cyan]Downloading PDF:[/cyan] {paper_id}")
            
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            
            with open(pdf_path, 'wb') as f:
                if total_size == 0:
                    f.write(response.content)
                else:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            # Simple progress indicator
                            progress = (downloaded / total_size) * 100
                            if downloaded % (total_size // 10 + 1) == 0:
                                console.print(f"[dim]  {progress:.0f}%...[/dim]", end='\r')
            
            console.print(f"[green]✓[/green] PDF downloaded: {pdf_path.name}")
            return pdf_path
            
        except requests.exceptions.RequestException as e:
            console.print(f"[red]✗[/red] Download failed: {str(e)[:100]}")
            if pdf_path.exists():
                pdf_path.unlink()  # Remove partial download
            return None
        except Exception as e:
            console.print(f"[red]✗[/red] Error: {str(e)[:100]}")
            return None
    
    def extract_text(self, pdf_path: Path, max_pages: Optional[int] = None) -> Optional[str]:
        """
        Extract text from PDF
        
        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum number of pages to extract (None = all)
            
        Returns:
            Extracted text or None if failed
        """
        if not pdf_path.exists():
            console.print(f"[red]Error:[/red] PDF not found: {pdf_path}")
            return None
        
        try:
            doc = fitz.open(pdf_path)
            text_parts = []
            
            num_pages = len(doc)
            if max_pages:
                num_pages = min(num_pages, max_pages)
            
            for page_num in range(num_pages):
                page = doc[page_num]
                text_parts.append(page.get_text())
            
            doc.close()
            
            full_text = "\n\n".join(text_parts)
            return full_text
            
        except Exception as e:
            console.print(f"[red]Error extracting text:[/red] {str(e)[:100]}")
            return None
    
    def extract_sections(self, pdf_path: Path) -> Dict[str, str]:
        """
        Extract common paper sections (Abstract, Introduction, etc.)
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with section names as keys and text as values
        """
        text = self.extract_text(pdf_path)
        if not text:
            return {}
        
        sections = {}
        
        # Common section headers in academic papers
        section_headers = [
            "abstract",
            "introduction",
            "background",
            "related work",
            "methodology",
            "methods",
            "experiments",
            "results",
            "discussion",
            "conclusion",
            "references"
        ]
        
        # Simple section extraction (case-insensitive)
        text_lower = text.lower()
        
        for i, header in enumerate(section_headers):
            # Find section start
            patterns = [
                f"\n{header}\n",
                f"\n{header}.",
                f"\n{header.upper()}\n",
                f"\n{header.title()}\n",
                f"\n{i+1}. {header}\n",  # Numbered sections
            ]
            
            start_pos = -1
            for pattern in patterns:
                pos = text_lower.find(pattern)
                if pos != -1:
                    start_pos = pos
                    break
            
            if start_pos == -1:
                continue
            
            # Find next section or end of text
            end_pos = len(text)
            for next_header in section_headers[i+1:]:
                for pattern in [f"\n{next_header}\n", f"\n{next_header}.", f"\n{next_header.upper()}\n"]:
                    pos = text_lower.find(pattern, start_pos + len(header))
                    if pos != -1 and pos < end_pos:
                        end_pos = pos
            
            # Extract section text
            section_text = text[start_pos:end_pos].strip()
            # Remove the header itself
            section_text = section_text.split('\n', 1)[-1] if '\n' in section_text else section_text
            
            if section_text:
                sections[header.title()] = section_text[:2000]  # Limit length
        
        return sections
    
    def search_in_pdf(self, pdf_path: Path, query: str, context_chars: int = 200) -> list:
        """
        Search for a query string in PDF and return matches with context
        
        Args:
            pdf_path: Path to PDF file
            query: Search query
            context_chars: Number of characters to show before/after match
            
        Returns:
            List of matches with context
        """
        text = self.extract_text(pdf_path)
        if not text:
            return []
        
        matches = []
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Find all occurrences
        start = 0
        while True:
            pos = text_lower.find(query_lower, start)
            if pos == -1:
                break
            
            # Extract context
            context_start = max(0, pos - context_chars)
            context_end = min(len(text), pos + len(query) + context_chars)
            
            context = text[context_start:context_end]
            
            # Add ellipsis if truncated
            if context_start > 0:
                context = "..." + context
            if context_end < len(text):
                context = context + "..."
            
            matches.append({
                'position': pos,
                'context': context,
                'query': query
            })
            
            start = pos + 1
        
        return matches
    
    def get_paper_metadata(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract metadata from PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with metadata
        """
        try:
            doc = fitz.open(pdf_path)
            metadata = {
                'num_pages': len(doc),
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', ''),
                'creator': doc.metadata.get('creator', ''),
                'producer': doc.metadata.get('producer', ''),
                'creation_date': doc.metadata.get('creationDate', ''),
                'size_kb': pdf_path.stat().st_size / 1024
            }
            doc.close()
            return metadata
        except Exception as e:
            console.print(f"[red]Error reading metadata:[/red] {str(e)[:100]}")
            return {}
