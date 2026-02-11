"""
Graph Visualization - Interactive and static citation network visualization
Supports interactive HTML (pyvis), static images (matplotlib), and terminal ASCII art
"""

import networkx as nx
from pathlib import Path
from typing import Optional, Dict
import webbrowser
from rich.console import Console
from rich.table import Table

console = Console()


class GraphVisualizer:
    """Visualize citation networks in multiple formats"""
    
    def __init__(self, output_dir: Path = None):
        """
        Initialize visualizer
        
        Args:
            output_dir: Directory to save visualizations (default: ./data/graphs/)
        """
        self.output_dir = output_dir or Path('./data/graphs')
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def visualize_interactive(
        self,
        graph: nx.DiGraph,
        paper_metadata: Dict = None,
        output_file: str = "citation_network.html",
        auto_open: bool = True
    ) -> Path:
        """
        Create interactive HTML visualization with pyvis
        
        Args:
            graph: NetworkX graph to visualize
            paper_metadata: Optional metadata for enriching visualization
            output_file: Output filename
            auto_open: Whether to open in browser automatically
            
        Returns:
            Path to generated HTML file
        """
        try:
            from pyvis.network import Network
        except ImportError:
            console.print("[red]✗[/red] pyvis not installed. Run: pip install pyvis")
            return None
        
        # Create pyvis network
        net = Network(
            height="800px",
            width="100%",
            directed=True,
            notebook=False,
            bgcolor="#ffffff",
            font_color="#000000"
        )
        
        # Configure physics for better layout
        net.set_options("""
        {
          "physics": {
            "enabled": true,
            "barnesHut": {
              "gravitationalConstant": -8000,
              "springLength": 200,
              "springConstant": 0.04
            }
          },
          "interaction": {
            "hover": true,
            "tooltipDelay": 100,
            "navigationButtons": true,
            "keyboard": true
          }
        }
        """)
        
        # Add nodes with sizing and coloring
        for node, data in graph.nodes(data=True):
            # Determine node properties
            title = data.get('title', 'Unknown')
            year = data.get('year', 'N/A')
            citations = data.get('citation_count', 0)
            is_partial = data.get('partial', False)
            
            # Size based on citations (log scale)
            import math
            size = 10 + math.log(max(citations, 1) + 1) * 5
            
            # Color based on year (gradient from blue to red)
            if year and year != 'N/A':
                year_int = int(year)
                # Map 2000-2024 to blue-red gradient
                if year_int >= 2020:
                    color = '#ff6b6b'  # Recent: Red
                elif year_int >= 2015:
                    color = '#ffa500'  # Mid: Orange
                elif year_int >= 2010:
                    color = '#4ecdc4'  # Older: Teal
                else:
                    color = '#95e1d3'  # Old: Light teal
            else:
                color = '#cccccc'  # Unknown: Gray
            
            if is_partial:
                color = '#eeeeee'  # Partial nodes: Very light gray
                size = 8
            
            # Create hover tooltip
            authors = data.get('authors', [])
            author_str = ', '.join(authors[:3]) if authors else 'Unknown'
            if len(authors) > 3:
                author_str += f' et al. ({len(authors)} total)'
            
            tooltip = f"""
            <b>{title}</b><br>
            Year: {year}<br>
            Authors: {author_str}<br>
            Citations: {citations:,}<br>
            arXiv: {node}
            """
            
            # Truncate label for display
            label = title[:40] + '...' if len(title) > 40 else title
            
            net.add_node(
                node,
                label=label,
                title=tooltip,
                size=size,
                color=color,
                borderWidth=2 if not is_partial else 1
            )
        
        # Add edges
        for source, target in graph.edges():
            net.add_edge(source, target, arrows="to", width=1, color="#888888")
        
        # Save to file
        output_path = self.output_dir / output_file
        net.save_graph(str(output_path))
        
        console.print(f"[green]✓[/green] Interactive graph saved: {output_path}")
        
        if auto_open:
            try:
                webbrowser.open(f'file://{output_path.absolute()}')
                console.print("[cyan]→[/cyan] Opening in browser...")
            except:
                console.print("[yellow]![/yellow] Open manually: {output_path}")
        
        return output_path
    
    def visualize_static(
        self,
        graph: nx.DiGraph,
        output_file: str = "citation_network.png",
        layout: str = "spring"
    ) -> Optional[Path]:
        """
        Create static image visualization with matplotlib
        
        Args:
            graph: NetworkX graph to visualize
            output_file: Output filename
            layout: Layout algorithm ('spring', 'circular', 'kamada_kawai')
            
        Returns:
            Path to generated image file
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            console.print("[red]✗[/red] matplotlib not installed")
            return None
        
        # Create figure
        plt.figure(figsize=(16, 12))
        
        # Choose layout
        if layout == "spring":
            pos = nx.spring_layout(graph, k=0.5, iterations=50)
        elif layout == "circular":
            pos = nx.circular_layout(graph)
        elif layout == "kamada_kawai":
            pos = nx.kamada_kawai_layout(graph)
        else:
            pos = nx.spring_layout(graph)
        
        # Prepare node sizes and colors
        node_sizes = []
        node_colors = []
        
        for node, data in graph.nodes(data=True):
            citations = data.get('citation_count', 0)
            is_partial = data.get('partial', False)
            
            if is_partial:
                node_sizes.append(100)
                node_colors.append('#eeeeee')
            else:
                import math
                size = 300 + math.log(max(citations, 1) + 1) * 200
                node_sizes.append(size)
                
                year = data.get('year', 2020)
                if isinstance(year, int) and year >= 2020:
                    node_colors.append('#ff6b6b')
                else:
                    node_colors.append('#4ecdc4')
        
        # Draw graph
        nx.draw_networkx_nodes(
            graph, pos,
            node_size=node_sizes,
            node_color=node_colors,
            alpha=0.7,
            edgecolors='#333333',
            linewidths=1.5
        )
        
        nx.draw_networkx_edges(
            graph, pos,
            edge_color='#888888',
            alpha=0.3,
            arrows=True,
            arrowsize=10,
            arrowstyle='->',
            connectionstyle='arc3,rad=0.1'
        )
        
        # Add labels for non-partial nodes
        labels = {}
        for node, data in graph.nodes(data=True):
            if not data.get('partial', False):
                title = data.get('title', node)
                labels[node] = title[:20] + '...' if len(title) > 20 else title
        
        nx.draw_networkx_labels(
            graph, pos,
            labels=labels,
            font_size=8,
            font_weight='bold'
        )
        
        plt.title("Citation Network", fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        
        # Save
        output_path = self.output_dir / output_file
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        console.print(f"[green]✓[/green] Static graph saved: {output_path}")
        return output_path
    
    def visualize_terminal(self, graph: nx.DiGraph, max_nodes: int = 20):
        """
        Simple ASCII visualization for terminal
        
        Args:
            graph: NetworkX graph to visualize
            max_nodes: Maximum number of nodes to display
        """
        console.print("\n[bold cyan]📊 Citation Network (Terminal View)[/bold cyan]\n")
        
        # Get stats
        stats_table = Table(title="Graph Statistics", show_header=False)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Total Papers", str(graph.number_of_nodes()))
        stats_table.add_row("Citation Links", str(graph.number_of_edges()))
        stats_table.add_row("Density", f"{nx.density(graph):.3f}")
        
        console.print(stats_table)
        
        # Show top papers by citations
        console.print("\n[bold]Top Papers by Citations:[/bold]\n")
        
        papers = []
        for node, data in graph.nodes(data=True):
            if not data.get('partial', False):
                papers.append((
                    node,
                    data.get('title', 'Unknown'),
                    data.get('citation_count', 0),
                    data.get('year', 'N/A'),
                    graph.in_degree(node)
                ))
        
        papers.sort(key=lambda x: x[2], reverse=True)
        
        paper_table = Table(show_header=True, header_style="bold magenta")
        paper_table.add_column("#", width=3)
        paper_table.add_column("Title", width=50)
        paper_table.add_column("Year", width=6)
        paper_table.add_column("Cites", justify="right", width=8)
        paper_table.add_column("In-Graph", justify="right", width=10)
        
        for i, (arxiv_id, title, citations, year, in_degree) in enumerate(papers[:max_nodes], 1):
            title_short = title[:47] + '...' if len(title) > 50 else title
            paper_table.add_row(
                str(i),
                title_short,
                str(year),
                f"{citations:,}",
                str(in_degree)
            )
        
        console.print(paper_table)
        
        # Show connections
        console.print("\n[bold]Citation Relationships:[/bold]\n")
        
        for i, (arxiv_id, title, citations, year, in_degree) in enumerate(papers[:5], 1):
            cited_by = list(graph.predecessors(arxiv_id))
            cites = list(graph.successors(arxiv_id))
            
            title_short = title[:40] + '...' if len(title) > 40 else title
            console.print(f"[cyan]{i}. {title_short}[/cyan]")
            
            if cited_by:
                console.print(f"   ← Cited by {len(cited_by)} papers in graph")
            if cites:
                console.print(f"   → Cites {len(cites)} papers in graph")
            console.print()
