#!/usr/bin/env python3
"""
Main CLI entry point for DeepSci Agent
"""

import click
from rich.console import Console
from rich.panel import Panel
from deepsci import __version__

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
    console.print(f"[yellow]Sources:[/yellow] {', '.join(sources) if sources else 'all'}")
    console.print(f"[yellow]Limit:[/yellow] {limit}")
    console.print("\n[red]Note:[/red] Search functionality not yet implemented")


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
    """Start interactive mode"""
    console.print(Panel(
        "[bold green]Welcome to DeepSci Agent![/bold green]\n\n"
        "Available commands:\n"
        "  • search <query>     - Search for papers\n"
        "  • summarize <id>     - Summarize a paper\n"
        "  • compare <id1> <id2> - Compare papers\n"
        "  • ask <question>     - Ask a question\n"
        "  • exit               - Exit interactive mode",
        title=f"DeepSci Agent v{__version__}"
    ))
    console.print("\n[red]Note:[/red] Interactive mode not yet implemented")


if __name__ == '__main__':
    cli()
