"""
Interactive chatbot interface for DeepSci Agent
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.prompt import Prompt
from rich import box
from datetime import datetime
from typing import List, Optional
import re

from deepsci.sources.arxiv_client import ArxivClient, Paper
from deepsci import __version__


class DeepSciChat:
    """Interactive chatbot interface for research assistance"""
    
    def __init__(self):
        self.console = Console()
        self.arxiv_client = ArxivClient(max_results=10)
        self.conversation_history = []
        self.current_papers = []
        
    def show_welcome(self):
        """Display welcome message"""
        welcome_text = f"""
# 🔬 Welcome to DeepSci Agent v{__version__}

Your AI-powered physics research assistant. I can help you:

• **Search** for papers across arXiv, PubMed, and more
• **Summarize** research papers and extract key findings  
• **Compare** multiple papers side-by-side
• **Answer** questions about physics topics

**Quick Commands:**
- `search <query>` - Search for papers
- `show <number>` - Show details of a paper from results
- `help` - Show all commands
- `exit` - Exit the chat

**Just type naturally!** Try: *"find papers on quantum entanglement"*
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
        
        for idx, paper in enumerate(papers, 1):
            authors = ", ".join(paper.authors[:2])
            if len(paper.authors) > 2:
                authors += f" et al."
            
            # Truncate title if too long
            title = paper.title if len(paper.title) <= 80 else paper.title[:77] + "..."
            
            table.add_row(
                str(idx),
                title,
                authors,
                str(paper.published.year)
            )
        
        self.console.print(table)
        self.console.print("\n[dim]Type 'show <number>' to see details of a specific paper[/dim]")
    
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
- `help` - Show this help message
- `exit` - Exit the chat

## Coming Soon
- `summarize <paper_id>` - Get AI summary of a paper
- `compare <id1> <id2>` - Compare two papers
- `ask <question>` - Ask questions about papers
        """
        self.console.print(Panel(
            Markdown(help_text),
            title="Help",
            border_style="yellow"
        ))
    
    def handle_search(self, query: str):
        """Handle search command"""
        self.console.print(f"\n[cyan]🔍 Searching for:[/cyan] {query}\n")
        
        try:
            with self.console.status("[bold cyan]Searching arXiv...", spinner="dots"):
                papers = self.arxiv_client.search(query)
            
            self.display_papers(papers)
            
        except Exception as e:
            self.console.print(f"[red]Error:[/red] {str(e)}")
    
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
                
                elif cmd == 'unknown':
                    self.console.print("[yellow]I didn't understand that. Type 'help' for available commands.[/yellow]")
                
            except KeyboardInterrupt:
                self.console.print("\n\n[yellow]Use 'exit' to quit[/yellow]")
            except EOFError:
                self.console.print("\n[green]👋 Goodbye![/green]\n")
                break
            except Exception as e:
                self.console.print(f"\n[red]Error:[/red] {str(e)}")


def start_chat():
    """Start the interactive chat interface"""
    chat = DeepSciChat()
    chat.run()
