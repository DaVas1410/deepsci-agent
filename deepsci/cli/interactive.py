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
from deepsci.llm.local_llm import LocalLLM, ModelDownloader
from deepsci import __version__


class DeepSciChat:
    """Interactive chatbot interface for research assistance"""
    
    def __init__(self, use_llm: bool = True):
        self.console = Console()
        self.arxiv_client = ArxivClient(max_results=10)
        self.pubmed_client = PubMedClient()
        self.citation_client = CitationClient()
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
    
    def show_welcome(self):
        """Display welcome message"""
        ai_status = "✓ AI Enabled" if (self.use_llm and self.llm) else "⊘ AI Disabled"
        
        welcome_text = f"""
# 🔬 Welcome to DeepSci Agent v{__version__}

Your AI-powered physics research assistant. I can help you:

• **Search** arXiv for physics papers with citation metrics
• **Summarize** research papers and extract key findings {' 🤖' if self.use_llm else ' (requires AI)'}
• **Rank** papers by citation impact and influence
• **Answer** questions about physics topics

**Quick Commands:**
- `search <query>` - Search arXiv with citation rankings
- `show <number>` - Show details of a paper from results
- `summarize <number>` - Get AI summary of a paper {' 🤖' if self.use_llm else ' (requires AI)'}
- `citations on/off` - Toggle citation fetching
- `help` - Show all commands
- `exit` - Exit the chat

**Just type naturally!** Try: *"find papers on quantum entanglement"*

**Status:** {ai_status} | Citations: {'✓ Enabled' if self.fetch_citations else '⊘ Disabled'}

**💡 Tip:** Citations are fetched in parallel for speed!
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
            header_style="bold cyan"
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

## Explicit Commands
- `search <query>` - Search for papers
- `show <number>` - Show details of paper from results
- `summarize <number>` - Get AI summary of a paper
- `help` - Show this help message
- `exit` - Exit the chat

## Coming Soon
- `compare <id1> <id2>` - Compare two papers
- `ask <question>` - Ask questions about papers
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
