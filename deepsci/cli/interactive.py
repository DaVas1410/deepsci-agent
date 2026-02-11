"""
Interactive chatbot interface for DeepSci Agent
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import box
from datetime import datetime
from typing import List, Optional
import re

from deepsci.sources.arxiv_client import ArxivClient, Paper
from deepsci.sources.citation_client import CitationClient
from deepsci.sources.scholar_client import ScholarClient
from deepsci.sources.pdf_processor import PDFProcessor
from deepsci.llm.local_llm import LocalLLM, ModelDownloader
from deepsci.search.vector_store import VectorStore
from deepsci import __version__


class DeepSciChat:
    """Interactive chatbot interface for research assistance"""
    
    def __init__(self, use_llm: bool = True):
        self.console = Console()
        self.arxiv_client = ArxivClient(max_results=10)
        self.citation_client = CitationClient()
        self.scholar_client = ScholarClient()
        self.pdf_processor = PDFProcessor()
        self.vector_store = None  # Initialize lazily on first use
        self.conversation_history = []
        self.current_papers = []
        self.llm = None
        self.use_llm = use_llm
        self.fetch_citations = True  # Enable citations by default
        
        # Initialize LLM if requested
        if self.use_llm:
            self._initialize_llm()
        
    def _initialize_llm(self):
        """Initialize the local LLM"""
        try:
            self.console.print("\n[cyan]Initializing AI assistant...[/cyan]")
            
            # Check if model exists
            downloader = ModelDownloader()
            model_path = downloader.models_dir / "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
            
            if not model_path.exists():
                self.console.print("[yellow]First time setup: Downloading AI model (669MB)[/yellow]")
                proceed = Confirm.ask("Download TinyLlama model?", default=True)
                
                if not proceed:
                    self.console.print("[yellow]Continuing without AI features...[/yellow]")
                    self.use_llm = False
                    return
            
            self.llm = LocalLLM()
            self.console.print("[green]✓[/green] AI assistant ready!\n")
            
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not load AI model: {str(e)}[/yellow]")
            self.console.print("[yellow]Continuing without AI features...[/yellow]")
            self.use_llm = False
    
    def _initialize_vector_store(self):
        """Initialize vector store (lazy loading)"""
        if self.vector_store is None:
            try:
                self.console.print("[cyan]Loading vector search...[/cyan]")
                self.vector_store = VectorStore()
                stats = self.vector_store.get_stats()
                self.console.print(f"[green]✓[/green] Library loaded: {stats['total_papers']} papers")
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not load vector store: {str(e)}[/yellow]")
    
    def show_welcome(self):
        """Display welcome message"""
        ai_status = "✓ AI Enabled" if (self.use_llm and self.llm) else "⊘ AI Disabled"
        
        welcome_text = f"""
# 🔬 Welcome to DeepSci Agent v{__version__}

Your AI-powered physics research assistant. I can help you:

• **Search** arXiv for physics papers with citation metrics
• **Compare** multiple papers side-by-side with AI analysis {' 🤖' if self.use_llm else ' (requires AI)'}
• **Summarize** research papers and extract key findings {' 🤖' if self.use_llm else ' (requires AI)'}
• **Rank** papers by citation impact and influence
• **Analyze** full PDF text, not just abstracts
• **Answer** questions about physics topics

**Quick Commands:**
- `search <query>` - Search arXiv with citation rankings
- `show <number>` - Show details of a paper from results
- `compare <numbers>` - Compare papers (e.g., "compare 1 2 3") {' 🤖' if self.use_llm else ' (requires AI)'}
- `download <number>` - Download PDF for offline reading
- `fulltext <number>` - Extract and view full PDF text
- `search pdf <number> <query>` - Search within a PDF
- `save <numbers>` - Save papers to your library (e.g., "save 1 2 3")
- `library search <query>` - Semantic search in your saved papers
- `similar to <number>` - Find papers similar to one from results
- `library stats` - Show your library statistics
- `summarize <number>` - Get AI summary {' 🤖' if self.use_llm else ' (requires AI)'}
- `help` - Show all commands
- `exit` - Exit the chat

**Just type naturally!** Try: *"find papers on quantum entanglement"*

**Status:** {ai_status} | Citations: {'✓ Enabled' if self.fetch_citations else '⊘ Disabled'}

**💡 Tip:** Download PDFs for full-text analysis beyond abstracts!
        """
        self.console.print(Panel(
            Markdown(welcome_text),
            title="DeepSci Agent",
            border_style="cyan",
            box=box.DOUBLE
        ))
    
    def parse_command(self, user_input: str) -> tuple[str, str]:
        """
        Parse user input into command and arguments
        Supports both natural language and explicit commands
        """
        user_input = user_input.strip()
        
        # Check for explicit commands
        if user_input.startswith('/'):
            parts = user_input[1:].split(' ', 1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            return cmd, args
        
        # Natural language parsing
        lower_input = user_input.lower()
        
        # Search patterns
        search_patterns = [
            r'^(?:search|find|look for|show me)\s+(?:papers?\s+)?(?:on|about)?\s*(.+)',
            r'^(?:what|papers)\s+(?:about|on)\s+(.+)',
        ]
        
        for pattern in search_patterns:
            match = re.match(pattern, lower_input)
            if match:
                return 'search', match.group(1).strip()
        
        # Show paper details
        if re.match(r'^show\s+(?:paper\s+)?(\d+)', lower_input):
            match = re.match(r'^show\s+(?:paper\s+)?(\d+)', lower_input)
            return 'show', match.group(1)
        
        # Summarize patterns
        if re.match(r'^summarize\s+(?:paper\s+)?(\d+)', lower_input):
            match = re.match(r'^summarize\s+(?:paper\s+)?(\d+)', lower_input)
            return 'summarize', match.group(1)
        
        # Save papers
        if re.match(r'^save\s+([\d\s]+)', lower_input):
            match = re.match(r'^save\s+([\d\s]+)', lower_input)
            return 'save', match.group(1)
        
        # Library search
        if lower_input.startswith('library search '):
            return 'library_search', lower_input[15:].strip()
        
        # Similar papers
        if re.match(r'^similar\s+(?:to\s+)?(\d+)', lower_input):
            match = re.match(r'^similar\s+(?:to\s+)?(\d+)', lower_input)
            return 'similar', match.group(1)
        
        # Compare papers
        if re.match(r'^compare\s+([\d\s]+)', lower_input):
            match = re.match(r'^compare\s+([\d\s]+)', lower_input)
            return 'compare', match.group(1)
        
        # PDF download
        if re.match(r'^download\s+(?:pdf\s+)?(\d+)', lower_input):
            match = re.match(r'^download\s+(?:pdf\s+)?(\d+)', lower_input)
            return 'download_pdf', match.group(1)
        
        # PDF full text
        if re.match(r'^fulltext\s+(\d+)', lower_input):
            match = re.match(r'^fulltext\s+(\d+)', lower_input)
            return 'fulltext', match.group(1)
        
        # Search in PDF
        if re.match(r'^search pdf\s+(\d+)\s+(.+)', lower_input):
            match = re.match(r'^search pdf\s+(\d+)\s+(.+)', lower_input)
            return 'search_pdf', f"{match.group(1)}|{match.group(2)}"
        
        # Library stats
        if 'library stats' in lower_input or 'library status' in lower_input:
            return 'library_stats', ''
        
        # Citations toggle
        if 'citations on' in lower_input:
            return 'citations', 'on'
        if 'citations off' in lower_input:
            return 'citations', 'off'
        
        # Help patterns
        if lower_input in ['help', 'help me', 'what can you do', 'commands']:
            return 'help', ''
        
        # Exit patterns
        if lower_input in ['exit', 'quit', 'bye', 'goodbye']:
            return 'exit', ''
        
        # Default: treat as search
        if len(user_input) > 3:
            return 'search', user_input
        
        return 'unknown', user_input
    
    def display_papers(self, papers: List[Paper]):
        """Display search results in a formatted table"""
        if not papers:
            self.console.print("[yellow]No papers found.[/yellow]")
            return
        
        self.current_papers = papers
        
        table = Table(
            title=f"Found {len(papers)} papers",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan",
            padding=(1, 2)  # Add vertical and horizontal padding
        )
        
        table.add_column("#", style="dim", width=3)
        table.add_column("Title", style="bold")
        table.add_column("Authors", style="green")
        table.add_column("Year", style="blue", width=6)
        table.add_column("Citations", style="yellow", width=10)
        table.add_column("Source", style="cyan", width=8)
        
        for idx, paper in enumerate(papers, 1):
            authors = ", ".join(paper.authors[:2])
            if len(paper.authors) > 2:
                authors += f" et al."
            
            # Truncate title if too long
            title = paper.title if len(paper.title) <= 80 else paper.title[:77] + "..."
            
            # Get year from paper
            if hasattr(paper, 'published') and paper.published:
                year = str(paper.published.year)
            else:
                # For PubMed papers, extract year from published_date string
                year = getattr(paper, 'published_date', 'N/A')
                if isinstance(year, str) and '-' in year:
                    year = year.split('-')[0]
            
            # Citation count
            citations = str(getattr(paper, 'citation_count', 0))
            if hasattr(paper, 'influential_citations') and paper.influential_citations > 0:
                citations += f" ({paper.influential_citations}⭐)"
            
            # Source
            source = getattr(paper, 'source', 'unknown').upper()
            
            table.add_row(
                str(idx),
                title,
                authors,
                year,
                citations,
                source
            )
        
        self.console.print(table)
        self.console.print("\n[dim]Type 'show <number>' to see details | Citations with ⭐ are highly influential[/dim]")
    
    def display_paper_details(self, paper: Paper):
        """Display detailed information about a single paper"""
        details = f"""
## {paper.title}

**Authors:** {', '.join(paper.authors)}

**Published:** {paper.published.strftime('%B %d, %Y')}

**Categories:** {', '.join(paper.categories)}

**arXiv ID:** {paper.id}

**URL:** {paper.url}

### Abstract
{paper.abstract}
        """
        
        self.console.print(Panel(
            Markdown(details),
            title=f"Paper Details",
            border_style="green",
            box=box.ROUNDED
        ))
    
    def show_help(self):
        """Display help information"""
        help_text = """
# Available Commands

## Natural Language (just type!)
- *"find papers on quantum mechanics"*
- *"search for dark matter research"*
- *"what about string theory"*

## Search Commands
- `search <query>` - Search arXiv for papers
- `library search <query>` - Semantic search in your saved papers
- `similar to <number>` - Find papers similar to one from results

## Analysis Commands
- `show <number>` - Show details of paper from results
- `summarize <number>` - Get AI summary of a paper (requires AI)
- `compare <numbers>` - Compare multiple papers (e.g., "compare 1 2 3") (requires AI)

## PDF Commands (NEW!)
- `download <number>` - Download PDF for offline access
- `fulltext <number>` - Extract and view full text from PDF
- `search pdf <number> <query>` - Search for text within a PDF

## Library Commands
- `save <numbers>` - Save papers to your library (e.g., "save 1 2 3")
- `library stats` - Show your library statistics

## Settings
- `citations on/off` - Enable/disable citation fetching
- `help` - Show this help message
- `exit` - Exit the chat
        """
        self.console.print(Panel(
            Markdown(help_text),
            title="Help",
            border_style="yellow"
        ))
    
    def handle_search(self, query: str):
        """Handle search command for arXiv"""
        self.console.print(f"\n[cyan]🔍 Searching arXiv:[/cyan] {query}\n")
        
        try:
            with self.console.status("[bold cyan]Searching arXiv and fetching citations...", spinner="dots"):
                papers = self.arxiv_client.search(
                    query, 
                    fetch_citations=self.fetch_citations
                )
            
            if papers:
                # Sort by citations if available
                if self.fetch_citations:
                    papers.sort(key=lambda p: getattr(p, 'citation_count', 0), reverse=True)
                
                self.console.print(f"[green]✓[/green] Found {len(papers)} papers from arXiv")
            
            self.display_papers(papers)
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate limit" in error_msg.lower():
                self.console.print("\n[yellow]⚠️  arXiv Rate Limit Warning[/yellow]")
                self.console.print("[dim]arXiv limits requests to prevent server overload.[/dim]")
                self.console.print("[dim]The system will automatically wait 3 seconds between requests.[/dim]")
                self.console.print("\n[cyan]💡 Tip:[/cyan] Wait 10 seconds and try again.")
            else:
                self.console.print(f"[red]Error:[/red] {error_msg}")
    
    def handle_show(self, paper_num: str):
        """Handle show paper details command"""
        try:
            num = int(paper_num)
            if num < 1 or num > len(self.current_papers):
                self.console.print(f"[red]Error:[/red] Paper number must be between 1 and {len(self.current_papers)}")
                return
            
            paper = self.current_papers[num - 1]
            self.display_paper_details(paper)
            
        except ValueError:
            self.console.print(f"[red]Error:[/red] Invalid paper number")
    
    def handle_summarize(self, paper_num: str):
        """Handle summarize paper command"""
        if not self.use_llm or not self.llm:
            self.console.print("[yellow]AI features are not available. Enable AI to use summarization.[/yellow]")
            return
        
        try:
            num = int(paper_num)
            if num < 1 or num > len(self.current_papers):
                self.console.print(f"[red]Error:[/red] Paper number must be between 1 and {len(self.current_papers)}")
                return
            
            paper = self.current_papers[num - 1]
            
            self.console.print(f"\n[cyan]🤖 Generating AI summary for:[/cyan] {paper.title}\n")
            
            with self.console.status("[bold cyan]AI is analyzing the paper...", spinner="dots"):
                summary = self.llm.summarize_abstract(paper.title, paper.abstract)
                key_points = self.llm.extract_key_points(paper.title, paper.abstract)
            
            summary_text = f"""
## {paper.title}

**Authors:** {', '.join(paper.authors[:5])}{'...' if len(paper.authors) > 5 else ''}

**Published:** {paper.published.strftime('%B %Y')}

### 🤖 AI Summary
{summary}

### 🔑 Key Points
{key_points}

---
*Summary generated by local AI (TinyLlama)*
            """
            
            self.console.print(Panel(
                Markdown(summary_text),
                title="AI-Powered Summary",
                border_style="magenta",
                box=box.ROUNDED
            ))
            
        except ValueError:
            self.console.print(f"[red]Error:[/red] Invalid paper number")
        except Exception as e:
            self.console.print(f"[red]Error generating summary:[/red] {str(e)}")
    
    def handle_save(self, paper_numbers: str):
        """Handle save papers to library command"""
        self._initialize_vector_store()
        
        if not self.vector_store:
            self.console.print("[red]Error:[/red] Vector store not available")
            return
        
        if not self.current_papers:
            self.console.print("[yellow]No papers to save. Search for papers first.[/yellow]")
            return
        
        try:
            # Parse paper numbers
            numbers = [int(n.strip()) for n in paper_numbers.split()]
            
            saved_count = 0
            for num in numbers:
                if num < 1 or num > len(self.current_papers):
                    self.console.print(f"[yellow]Skipping invalid number: {num}[/yellow]")
                    continue
                
                paper = self.current_papers[num - 1]
                
                # Check if already exists
                if self.vector_store.paper_exists(paper.id):
                    self.console.print(f"[dim]Paper {num} already in library[/dim]")
                    continue
                
                # Convert Paper object to dict
                paper_dict = {
                    'id': paper.id,
                    'title': paper.title,
                    'abstract': paper.abstract,
                    'authors': paper.authors,
                    'year': paper.published.year if hasattr(paper, 'published') else '',
                    'categories': getattr(paper, 'categories', []),
                    'citation_count': getattr(paper, 'citation_count', 0),
                    'url': getattr(paper, 'url', '')
                }
                
                if self.vector_store.add_paper(paper_dict):
                    saved_count += 1
                    self.console.print(f"[green]✓[/green] Saved paper {num}: {paper.title[:60]}...")
            
            if saved_count > 0:
                stats = self.vector_store.get_stats()
                self.console.print(f"\n[cyan]Library now has {stats['total_papers']} papers[/cyan]")
            
        except ValueError:
            self.console.print(f"[red]Error:[/red] Invalid paper numbers")
        except Exception as e:
            self.console.print(f"[red]Error saving papers:[/red] {str(e)}")
    
    def handle_library_search(self, query: str):
        """Handle semantic search in library"""
        self._initialize_vector_store()
        
        if not self.vector_store:
            self.console.print("[red]Error:[/red] Vector store not available")
            return
        
        stats = self.vector_store.get_stats()
        if stats['total_papers'] == 0:
            self.console.print("[yellow]Your library is empty. Save some papers first![/yellow]")
            self.console.print("[dim]Use 'save <number>' after searching for papers[/dim]")
            return
        
        self.console.print(f"\n[cyan]🔍 Searching your library ({stats['total_papers']} papers):[/cyan] {query}\n")
        
        try:
            with self.console.status("[bold cyan]Semantic search...", spinner="dots"):
                papers = self.vector_store.search(query, n_results=10)
            
            if papers:
                self.console.print(f"[green]✓[/green] Found {len(papers)} relevant papers")
                # Convert dict to Paper-like objects
                self.current_papers = []
                for p in papers:
                    paper_obj = Paper(
                        id=p.get('id', ''),
                        title=p.get('title', ''),
                        authors=p.get('authors', []),
                        published=p.get('year', ''),
                        summary=p.get('abstract', ''),
                        pdf_url=p.get('url', ''),
                        categories=p.get('categories', [])
                    )
                    # Add citation count if available
                    paper_obj.citation_count = int(p.get('citation_count', 0))
                    paper_obj.similarity = p.get('similarity', 0)
                    self.current_papers.append(paper_obj)
                self.display_papers(self.current_papers)
            else:
                self.console.print("[yellow]No matching papers found in your library[/yellow]")
                
        except Exception as e:
            self.console.print(f"[red]Error:[/red] {str(e)}")
    
    def handle_similar(self, paper_num: str):
        """Handle find similar papers command"""
        self._initialize_vector_store()
        
        if not self.vector_store:
            self.console.print("[red]Error:[/red] Vector store not available")
            return
        
        if not self.current_papers:
            self.console.print("[yellow]No papers to compare. Search for papers first.[/yellow]")
            return
        
        try:
            num = int(paper_num)
            if num < 1 or num > len(self.current_papers):
                self.console.print(f"[red]Error:[/red] Paper number must be between 1 and {len(self.current_papers)}")
                return
            
            paper = self.current_papers[num - 1]
            paper_id = paper.id if hasattr(paper, 'id') else None
            
            if not paper_id:
                self.console.print("[red]Error:[/red] Could not get paper ID")
                return
            
            # Check if paper is in library
            if not self.vector_store.paper_exists(paper_id):
                self.console.print(f"[yellow]Paper {num} not in library yet. Searching arXiv instead...[/yellow]")
                # TODO: Could search arXiv for similar papers by keywords
                self.console.print("[dim]Save papers to library first to use similarity search[/dim]")
                return
            
            self.console.print(f"\n[cyan]Finding papers similar to:[/cyan] {paper.title[:60]}...\n")
            
            with self.console.status("[bold cyan]Finding similar papers...", spinner="dots"):
                similar_papers = self.vector_store.find_similar(paper_id, n_results=10)
            
            if similar_papers:
                self.console.print(f"[green]✓[/green] Found {len(similar_papers)} similar papers")
                # Convert dict to Paper-like objects
                self.current_papers = []
                for p in similar_papers:
                    paper_obj = Paper(
                        id=p.get('id', ''),
                        title=p.get('title', ''),
                        authors=p.get('authors', []),
                        published=p.get('year', ''),
                        summary=p.get('abstract', ''),
                        pdf_url=p.get('url', ''),
                        categories=p.get('categories', [])
                    )
                    # Add citation count if available
                    paper_obj.citation_count = int(p.get('citation_count', 0))
                    paper_obj.similarity = p.get('similarity', 0)
                    self.current_papers.append(paper_obj)
                self.display_papers(self.current_papers)
            else:
                self.console.print("[yellow]No similar papers found in library[/yellow]")
                
        except ValueError:
            self.console.print(f"[red]Error:[/red] Invalid paper number")
        except Exception as e:
            self.console.print(f"[red]Error finding similar papers:[/red] {str(e)}")
    
    def _generate_simple_comparison(self, papers: List[Paper]) -> str:
        """Generate a simple rule-based comparison as fallback"""
        analysis = "**Overview:**\n"
        analysis += f"Comparing {len(papers)} papers on related topics.\n\n"
        
        analysis += "**Papers:**\n"
        for i, paper in enumerate(papers, 1):
            year = paper.published.year if hasattr(paper.published, 'year') else str(paper.published)[:4]
            citations = paper.citation_count if paper.citation_count > 0 else 0
            analysis += f"{i}. *{paper.title[:60]}...* ({year}, {citations} citations)\n"
        
        analysis += "\n**Basic Comparison:**\n"
        
        # Compare by year
        years = [p.published.year if hasattr(p.published, 'year') else int(str(p.published)[:4]) for p in papers]
        if max(years) - min(years) > 2:
            analysis += f"- Time span: {max(years) - min(years)} years ({min(years)}-{max(years)})\n"
        
        # Compare by citations
        citations = [p.citation_count for p in papers]
        if max(citations) > 0:
            most_cited = papers[citations.index(max(citations))]
            analysis += f"- Most cited: Paper {citations.index(max(citations)) + 1} ({max(citations)} citations)\n"
        
        # Common authors
        all_authors = set()
        for p in papers:
            all_authors.update(p.authors)
        analysis += f"- Total unique authors: {len(all_authors)}\n"
        
        analysis += "\n**Recommendation:**\n"
        # Recommend reading order by year (oldest first for foundational)
        oldest_idx = years.index(min(years))
        analysis += f"Start with Paper {oldest_idx + 1} ({min(years)}) for foundational concepts.\n"
        
        return analysis
    
    def handle_compare(self, paper_numbers: str):
        """Handle paper comparison command"""
        if not self.use_llm or not self.llm:
            self.console.print("[yellow]Paper comparison requires AI to be enabled[/yellow]")
            self.console.print("[dim]Start with AI enabled or use --ai flag[/dim]")
            return
        
        if not self.current_papers:
            self.console.print("[yellow]No papers to compare. Search for papers first.[/yellow]")
            return
        
        try:
            # Parse paper numbers
            numbers = [int(n.strip()) for n in paper_numbers.split()]
            
            if len(numbers) < 2:
                self.console.print("[yellow]Please specify at least 2 papers to compare (e.g., 'compare 1 2')[/yellow]")
                return
            
            if len(numbers) > 4:
                self.console.print("[yellow]Comparing more than 4 papers at once may be slow. Using first 4...[/yellow]")
                numbers = numbers[:4]
            
            # Validate paper numbers
            papers_to_compare = []
            for num in numbers:
                if num < 1 or num > len(self.current_papers):
                    self.console.print(f"[yellow]Invalid paper number: {num}[/yellow]")
                    return
                papers_to_compare.append(self.current_papers[num - 1])
            
            self.console.print(f"\n[cyan]🔍 Comparing {len(papers_to_compare)} papers with AI...[/cyan]\n")
            
            # Create comparison prompt with proper chat template
            papers_info = ""
            for i, paper in enumerate(papers_to_compare, 1):
                authors_str = ', '.join(paper.authors[:3])
                if len(paper.authors) > 3:
                    authors_str += f" et al."
                papers_info += f"Paper {i}:\n"
                papers_info += f"Title: {paper.title}\n"
                papers_info += f"Authors: {authors_str}\n"
                # Limit abstract to avoid token overflow
                abstract = paper.abstract[:400] if len(paper.abstract) > 400 else paper.abstract
                papers_info += f"Abstract: {abstract}\n\n"
            
            # Use proper chat template format like in summarize_abstract
            comparison_prompt = f"""<|system|>
You are a research assistant helping to compare scientific papers. Provide clear, structured comparative analysis.
</s>
<|user|>
Compare these {len(papers_to_compare)} research papers:

{papers_info}

Provide a comparative analysis with these sections:

**Similarities:** What approaches or findings do these papers share?

**Differences:** What unique contributions does each paper make?

**Reading Order:** Which paper should be read first and why?

**Relationship:** How do these papers relate to each other?

Write a clear analysis:
</s>
<|assistant|>
"""
            
            with self.console.status("[bold cyan]AI analyzing papers...", spinner="dots"):
                response = self.llm.generate(
                    comparison_prompt,
                    max_tokens=1000,
                    temperature=0.4
                )
            
            # Clean up response - remove any prompt artifacts
            response = response.strip()
            # Remove common artifacts
            for prefix in ["Write your analysis now:", "TASK:", "Here is", "Analysis:"]:
                if response.startswith(prefix):
                    response = response[len(prefix):].strip()
            
            # If response is suspiciously short or contains prompt text, provide fallback
            if len(response) < 100 or any(x in response.lower() for x in ["provide a comparative", "covering:", "task:"]):
                response = self._generate_simple_comparison(papers_to_compare)
            
            # Display comparison
            self.console.print(Panel(
                Markdown(f"## 📊 Comparative Analysis\n\n{response}"),
                title=f"Comparison of {len(papers_to_compare)} Papers",
                border_style="cyan",
                box=box.ROUNDED
            ))
            
            # Show side-by-side summary table
            table = Table(title="Side-by-Side Summary", box=box.ROUNDED)
            table.add_column("#", style="cyan", width=3)
            table.add_column("Title", style="white", width=35)
            table.add_column("Year", style="yellow", width=6)
            table.add_column("Citations", style="green", width=10)
            table.add_column("Authors", style="dim", width=25)
            
            for i, paper in enumerate(papers_to_compare, 1):
                year = paper.published.year if hasattr(paper.published, 'year') else str(paper.published)[:4]
                citations = str(paper.citation_count) if paper.citation_count > 0 else "-"
                authors = ", ".join(paper.authors[:2])
                if len(paper.authors) > 2:
                    authors += " et al."
                
                table.add_row(
                    str(i),
                    paper.title[:35] + ("..." if len(paper.title) > 35 else ""),
                    str(year),
                    citations,
                    authors
                )
            
            self.console.print("\n")
            self.console.print(table)
            
        except ValueError:
            self.console.print(f"[red]Error:[/red] Invalid paper numbers. Use format: 'compare 1 2 3'")
        except Exception as e:
            self.console.print(f"[red]Error comparing papers:[/red] {str(e)}")
    
    def handle_download_pdf(self, paper_num: str):
        """Handle PDF download command"""
        if not self.current_papers:
            self.console.print("[yellow]No papers to download. Search for papers first.[/yellow]")
            return
        
        try:
            num = int(paper_num)
            if num < 1 or num > len(self.current_papers):
                self.console.print(f"[yellow]Invalid paper number: {num}[/yellow]")
                return
            
            paper = self.current_papers[num - 1]
            
            # Download PDF
            pdf_path = self.pdf_processor.download_pdf(paper.pdf_url, paper.id)
            
            if pdf_path:
                # Show metadata
                metadata = self.pdf_processor.get_paper_metadata(pdf_path)
                self.console.print(f"\n[green]✓[/green] PDF ready: {pdf_path.name}")
                self.console.print(f"[dim]  Pages: {metadata.get('num_pages', 'unknown')}")
                self.console.print(f"  Size: {metadata.get('size_kb', 0):.1f} KB[/dim]")
            
        except ValueError:
            self.console.print(f"[red]Error:[/red] Invalid paper number")
        except Exception as e:
            self.console.print(f"[red]Error downloading PDF:[/red] {str(e)}")
    
    def handle_fulltext(self, paper_num: str):
        """Handle full-text extraction and display"""
        if not self.current_papers:
            self.console.print("[yellow]No papers available. Search for papers first.[/yellow]")
            return
        
        try:
            num = int(paper_num)
            if num < 1 or num > len(self.current_papers):
                self.console.print(f"[yellow]Invalid paper number: {num}[/yellow]")
                return
            
            paper = self.current_papers[num - 1]
            
            # Download if needed
            safe_id = paper.id.replace('/', '_').replace(':', '_')
            pdf_path = self.pdf_processor.cache_dir / f"{safe_id}.pdf"
            
            if not pdf_path.exists():
                self.console.print(f"[cyan]Downloading PDF first...[/cyan]")
                pdf_path = self.pdf_processor.download_pdf(paper.pdf_url, paper.id)
                if not pdf_path:
                    return
            
            # Extract sections
            self.console.print(f"\n[cyan]Extracting text from PDF...[/cyan]")
            sections = self.pdf_processor.extract_sections(pdf_path)
            
            if sections:
                self.console.print(f"[green]✓[/green] Extracted {len(sections)} sections\n")
                
                for section_name, content in list(sections.items())[:5]:  # Show first 5 sections
                    self.console.print(Panel(
                        content[:500] + ("..." if len(content) > 500 else ""),
                        title=f"📄 {section_name}",
                        border_style="blue",
                        box=box.ROUNDED
                    ))
                    self.console.print()
                
                if len(sections) > 5:
                    self.console.print(f"[dim]... and {len(sections) - 5} more sections[/dim]\n")
            else:
                # Fallback: show first page
                text = self.pdf_processor.extract_text(pdf_path, max_pages=1)
                if text:
                    self.console.print(Panel(
                        text[:1000] + ("..." if len(text) > 1000 else ""),
                        title="📄 First Page",
                        border_style="blue"
                    ))
                
        except ValueError:
            self.console.print(f"[red]Error:[/red] Invalid paper number")
        except Exception as e:
            self.console.print(f"[red]Error extracting text:[/red] {str(e)}")
    
    def handle_search_pdf(self, args: str):
        """Handle search within PDF"""
        try:
            parts = args.split('|')
            if len(parts) != 2:
                self.console.print("[yellow]Usage: search pdf <number> <query>[/yellow]")
                return
            
            num = int(parts[0])
            query = parts[1].strip()
            
            if not self.current_papers or num < 1 or num > len(self.current_papers):
                self.console.print(f"[yellow]Invalid paper number: {num}[/yellow]")
                return
            
            paper = self.current_papers[num - 1]
            
            # Download if needed
            safe_id = paper.id.replace('/', '_').replace(':', '_')
            pdf_path = self.pdf_processor.cache_dir / f"{safe_id}.pdf"
            
            if not pdf_path.exists():
                self.console.print(f"[cyan]Downloading PDF first...[/cyan]")
                pdf_path = self.pdf_processor.download_pdf(paper.pdf_url, paper.id)
                if not pdf_path:
                    return
            
            # Search
            self.console.print(f"\n[cyan]🔍 Searching PDF for:[/cyan] '{query}'\n")
            matches = self.pdf_processor.search_in_pdf(pdf_path, query, context_chars=150)
            
            if matches:
                self.console.print(f"[green]✓[/green] Found {len(matches)} matches\n")
                
                for i, match in enumerate(matches[:10], 1):  # Show first 10 matches
                    self.console.print(f"[cyan]Match {i}:[/cyan]")
                    # Highlight the query in context
                    context = match['context'].replace(query, f"[bold yellow]{query}[/bold yellow]")
                    context = context.replace(query.lower(), f"[bold yellow]{query.lower()}[/bold yellow]")
                    context = context.replace(query.upper(), f"[bold yellow]{query.upper()}[/bold yellow]")
                    self.console.print(f"  {context}\n")
                
                if len(matches) > 10:
                    self.console.print(f"[dim]... and {len(matches) - 10} more matches[/dim]")
            else:
                self.console.print(f"[yellow]No matches found for '{query}'[/yellow]")
                
        except ValueError:
            self.console.print(f"[red]Error:[/red] Invalid paper number")
        except Exception as e:
            self.console.print(f"[red]Error searching PDF:[/red] {str(e)}")
    
    def handle_library_stats(self):
        """Handle library statistics command"""
        self._initialize_vector_store()
        
        if not self.vector_store:
            self.console.print("[red]Error:[/red] Vector store not available")
            return
        
        stats = self.vector_store.get_stats()
        
        stats_text = f"""
## 📚 Your Research Library

**Total Papers:** {stats['total_papers']}

**Embedding Model:** {stats.get('model', 'all-MiniLM-L6-v2')}

**Vector Dimensions:** {stats.get('dimensions', 384)}

**Capabilities:**
- Semantic search by meaning
- Find similar papers
- Build research connections

**Storage:** `./data/vectordb/`
        """
        
        self.console.print(Panel(
            Markdown(stats_text),
            title="Library Statistics",
            border_style="cyan"
        ))
    
    def run(self):
        """Main chat loop"""
        self.show_welcome()
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
                
                if not user_input.strip():
                    continue
                
                # Parse and execute command
                cmd, args = self.parse_command(user_input)
                
                if cmd == 'exit':
                    self.console.print("\n[green]👋 Goodbye! Happy researching![/green]\n")
                    break
                
                elif cmd == 'help':
                    self.show_help()
                
                elif cmd == 'search':
                    if not args:
                        self.console.print("[yellow]Please provide a search query[/yellow]")
                    else:
                        self.handle_search(args)
                
                elif cmd == 'show':
                    if not self.current_papers:
                        self.console.print("[yellow]No papers to show. Search for papers first.[/yellow]")
                    else:
                        self.handle_show(args)
                
                elif cmd == 'summarize':
                    if not self.current_papers:
                        self.console.print("[yellow]No papers to summarize. Search for papers first.[/yellow]")
                    else:
                        self.handle_summarize(args)
                
                elif cmd == 'save':
                    self.handle_save(args)
                
                elif cmd == 'library_search':
                    if not args:
                        self.console.print("[yellow]Please provide a search query[/yellow]")
                    else:
                        self.handle_library_search(args)
                
                elif cmd == 'similar':
                    self.handle_similar(args)
                
                elif cmd == 'compare':
                    self.handle_compare(args)
                
                elif cmd == 'download_pdf':
                    self.handle_download_pdf(args)
                
                elif cmd == 'fulltext':
                    self.handle_fulltext(args)
                
                elif cmd == 'search_pdf':
                    self.handle_search_pdf(args)
                
                elif cmd == 'library_stats':
                    self.handle_library_stats()
                
                elif cmd == 'citations':
                    if args == 'on':
                        self.fetch_citations = True
                        self.console.print("[green]✓[/green] Citation fetching enabled")
                    elif args == 'off':
                        self.fetch_citations = False
                        self.console.print("[yellow]⊘[/yellow] Citation fetching disabled (faster searches)")
                
                elif cmd == 'unknown':
                    self.console.print("[yellow]I didn't understand that. Type 'help' for available commands.[/yellow]")
                
            except KeyboardInterrupt:
                self.console.print("\n\n[yellow]Use 'exit' to quit[/yellow]")
            except EOFError:
                self.console.print("\n[green]👋 Goodbye![/green]\n")
                break
            except Exception as e:
                self.console.print(f"\n[red]Error:[/red] {str(e)}")


def start_chat(use_llm: bool = True):
    """Start the interactive chat interface"""
    chat = DeepSciChat(use_llm=use_llm)
    chat.run()
