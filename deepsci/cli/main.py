#!/usr/bin/env python3
"""
Main CLI entry point for DeepSci Agent
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from deepsci import __version__
from deepsci.sources.arxiv_client import ArxivClient
from deepsci.cli.interactive import start_chat

console = Console()


@click.group()
@click.version_option(version=__version__)
def cli():
    """DeepSci Agent - AI-powered physics research assistant"""
    pass


@cli.command()
@click.argument('query')
@click.option('--sources', '-s', multiple=True, help='Specific sources to search (arxiv, pubmed, scholar)')
@click.option('--limit', '-l', default=10, help='Maximum number of results')
def search(query, sources, limit):
    """Search for physics papers across multiple sources"""
    console.print(Panel(f"[bold cyan]Searching for:[/bold cyan] {query}", title="DeepSci Search"))
    
    # For now, only arXiv is implemented
    if sources and 'arxiv' not in sources:
        console.print("[yellow]Currently only arXiv is supported. Searching arXiv...[/yellow]\n")
    
    try:
        arxiv_client = ArxivClient(max_results=limit)
        
        with console.status("[bold cyan]Searching arXiv...", spinner="dots"):
            papers = arxiv_client.search(query, max_results=limit)
        
        if not papers:
            console.print("[yellow]No papers found.[/yellow]")
            return
        
        # Display results in a table
        table = Table(
            title=f"Found {len(papers)} papers",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan"
        )
        
        table.add_column("#", style="dim", width=3)
        table.add_column("Title", style="bold", width=60)
        table.add_column("Authors", style="green", width=30)
        table.add_column("Year", style="blue", width=6)
        
        for idx, paper in enumerate(papers, 1):
            authors = ", ".join(paper.authors[:2])
            if len(paper.authors) > 2:
                authors += f" et al."
            
            title = paper.title if len(paper.title) <= 60 else paper.title[:57] + "..."
            
            table.add_row(
                str(idx),
                title,
                authors,
                str(paper.published.year)
            )
        
        console.print("\n")
        console.print(table)
        console.print(f"\n[dim]Use 'deepsci interactive' for a better research experience![/dim]")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")


@cli.command()
@click.argument('paper_id')
def summarize(paper_id):
    """Generate a summary of a specific paper"""
    console.print(Panel(f"[bold cyan]Summarizing:[/bold cyan] {paper_id}", title="DeepSci Summarize"))
    console.print("\n[red]Note:[/red] Summarize functionality not yet implemented")


@cli.command()
@click.argument('paper_ids', nargs=-1)
def compare(paper_ids):
    """Compare multiple papers"""
    if len(paper_ids) < 2:
        console.print("[red]Error:[/red] Please provide at least 2 paper IDs to compare")
        return
    
    console.print(Panel(f"[bold cyan]Comparing {len(paper_ids)} papers[/bold cyan]", title="DeepSci Compare"))
    for pid in paper_ids:
        console.print(f"  • {pid}")
    console.print("\n[red]Note:[/red] Compare functionality not yet implemented")


@cli.command()
@click.argument('question')
def ask(question):
    """Ask a question about your research corpus"""
    console.print(Panel(f"[bold cyan]Question:[/bold cyan] {question}", title="DeepSci Ask"))
    console.print("\n[red]Note:[/red] Ask functionality not yet implemented")


@cli.command()
def interactive():
    """Start interactive chatbot mode"""
    start_chat()


if __name__ == '__main__':
    cli()
