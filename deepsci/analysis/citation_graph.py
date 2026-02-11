"""
Citation Graph Builder - Build and analyze citation networks
Fetches citations and references from Semantic Scholar to create relationship graphs
"""

import networkx as nx
from semanticscholar import SemanticScholar
from typing import List, Dict, Optional, Set, Tuple
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import logging

logger = logging.getLogger(__name__)
console = Console()


class CitationGraph:
    """Build and analyze citation networks from paper relationships"""
    
    def __init__(self, delay_seconds: float = 1.0, max_depth: int = 1):
        """
        Initialize citation graph builder
        
        Args:
            delay_seconds: Delay between API requests
            max_depth: Maximum citation depth (1 = direct citations only)
        """
        self.sch = SemanticScholar(timeout=10)
        self.delay_seconds = delay_seconds
        self.max_depth = max_depth
        self.last_request_time = 0
        self.graph = nx.DiGraph()
        self.paper_metadata = {}  # Store paper details
        
    def _wait_for_rate_limit(self):
        """Ensure we don't exceed rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)
        self.last_request_time = time.time()
    
    def _fetch_paper_details(self, arxiv_id: str) -> Optional[Dict]:
        """
        Fetch paper details from Semantic Scholar
        
        Args:
            arxiv_id: arXiv ID of the paper
            
        Returns:
            Dictionary with paper metadata or None
        """
        try:
            self._wait_for_rate_limit()
            
            # Clean arxiv ID
            arxiv_id = arxiv_id.replace('arxiv:', '').replace('arXiv:', '')
            for version in ['v1', 'v2', 'v3', 'v4', 'v5']:
                arxiv_id = arxiv_id.replace(version, '')
            
            paper = self.sch.get_paper(
                f'arXiv:{arxiv_id}',
                fields=[
                    'title', 'year', 'authors', 'citationCount',
                    'referenceCount', 'citations', 'references',
                    'influentialCitationCount', 'abstract'
                ]
            )
            
            if not paper:
                return None
            
            # Handle authors (can be dict or object)
            authors = []
            if paper.authors:
                for a in paper.authors:
                    if isinstance(a, dict):
                        authors.append(a.get('name', 'Unknown'))
                    elif hasattr(a, 'name'):
                        authors.append(a.name)
                    else:
                        authors.append(str(a))
            
            return {
                'arxiv_id': arxiv_id,
                'title': paper.title,
                'year': paper.year,
                'authors': authors,
                'citation_count': paper.citationCount or 0,
                'reference_count': paper.referenceCount or 0,
                'influential_citations': paper.influentialCitationCount or 0,
                'abstract': paper.abstract or '',
                'citations': paper.citations or [],
                'references': paper.references or []
            }
            
        except Exception as e:
            logger.warning(f"Failed to fetch paper {arxiv_id}: {e}")
            return None
    
    def build_graph(self, arxiv_ids: List[str], include_references: bool = True) -> nx.DiGraph:
        """
        Build citation graph for given papers
        
        Args:
            arxiv_ids: List of arXiv IDs to analyze
            include_references: Whether to include papers that these papers cite
            
        Returns:
            NetworkX directed graph
        """
        self.graph = nx.DiGraph()
        self.paper_metadata = {}
        processed_ids = set()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"Building citation network for {len(arxiv_ids)} papers...",
                total=None
            )
            
            for arxiv_id in arxiv_ids:
                if arxiv_id in processed_ids:
                    continue
                
                progress.update(task, description=f"Fetching: {arxiv_id}")
                paper = self._fetch_paper_details(arxiv_id)
                
                if not paper:
                    continue
                
                # Add paper as node
                self.graph.add_node(
                    arxiv_id,
                    title=paper['title'],
                    year=paper['year'],
                    authors=paper['authors'],
                    citation_count=paper['citation_count'],
                    influential_citations=paper['influential_citations']
                )
                
                self.paper_metadata[arxiv_id] = paper
                processed_ids.add(arxiv_id)
                
                # Add citations (papers that cite this paper)
                for citation in paper['citations'][:50]:  # Limit to avoid explosion
                    citing_arxiv = self._extract_arxiv_id(citation)
                    if citing_arxiv and citing_arxiv not in processed_ids:
                        self.graph.add_node(citing_arxiv, partial=True)
                        self.graph.add_edge(citing_arxiv, arxiv_id, type='cites')
                
                # Add references (papers this paper cites)
                if include_references:
                    for reference in paper['references'][:50]:
                        ref_arxiv = self._extract_arxiv_id(reference)
                        if ref_arxiv and ref_arxiv not in processed_ids:
                            self.graph.add_node(ref_arxiv, partial=True)
                            self.graph.add_edge(arxiv_id, ref_arxiv, type='cites')
        
        console.print(f"[green]✓[/green] Graph built: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")
        return self.graph
    
    def _extract_arxiv_id(self, paper_obj) -> Optional[str]:
        """Extract arXiv ID from Semantic Scholar paper object"""
        if not paper_obj:
            return None
        
        try:
            # Handle both dict and object formats
            if isinstance(paper_obj, dict):
                external_ids = paper_obj.get('externalIds', {})
            elif hasattr(paper_obj, 'externalIds'):
                external_ids = paper_obj.externalIds or {}
            else:
                return None
            
            if external_ids and 'ArXiv' in external_ids:
                arxiv_id = external_ids['ArXiv']
                # Clean version numbers
                for version in ['v1', 'v2', 'v3', 'v4', 'v5']:
                    arxiv_id = arxiv_id.replace(version, '')
                return arxiv_id
        except:
            pass
        
        return None
    
    def find_seminal_papers(self, min_citations: int = 10) -> List[Tuple[str, Dict]]:
        """
        Identify influential papers in the graph
        
        Args:
            min_citations: Minimum citation count to consider
            
        Returns:
            List of (arxiv_id, metadata) tuples sorted by influence
        """
        seminal = []
        
        for node, data in self.graph.nodes(data=True):
            if data.get('partial'):  # Skip incomplete nodes
                continue
            
            citation_count = data.get('citation_count', 0)
            influential = data.get('influential_citations', 0)
            
            if citation_count >= min_citations:
                # Calculate influence score
                in_degree = self.graph.in_degree(node)  # How many papers cite it
                score = citation_count * 0.5 + influential * 2 + in_degree * 10
                
                seminal.append((
                    node,
                    {
                        'title': data.get('title', 'Unknown'),
                        'year': data.get('year', 'N/A'),
                        'citations': citation_count,
                        'influential': influential,
                        'in_graph_citations': in_degree,
                        'influence_score': score
                    }
                ))
        
        # Sort by influence score
        seminal.sort(key=lambda x: x[1]['influence_score'], reverse=True)
        return seminal
    
    def find_citation_path(self, from_id: str, to_id: str) -> Optional[List[str]]:
        """
        Find citation path between two papers
        
        Args:
            from_id: Starting paper arXiv ID
            to_id: Target paper arXiv ID
            
        Returns:
            List of arXiv IDs showing the path, or None if no path exists
        """
        try:
            path = nx.shortest_path(self.graph, from_id, to_id)
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None
    
    def get_paper_neighbors(self, arxiv_id: str, direction: str = 'both') -> Dict[str, List]:
        """
        Get papers that cite or are cited by the given paper
        
        Args:
            arxiv_id: arXiv ID of the paper
            direction: 'in' (cited by), 'out' (cites), or 'both'
            
        Returns:
            Dictionary with 'citing' and 'cited_by' lists
        """
        result = {'citing': [], 'cited_by': []}
        
        if not self.graph.has_node(arxiv_id):
            return result
        
        if direction in ['out', 'both']:
            # Papers this paper cites
            result['citing'] = list(self.graph.successors(arxiv_id))
        
        if direction in ['in', 'both']:
            # Papers that cite this paper
            result['cited_by'] = list(self.graph.predecessors(arxiv_id))
        
        return result
    
    def calculate_centrality(self) -> Dict[str, float]:
        """
        Calculate centrality metrics for all papers
        
        Returns:
            Dictionary mapping arxiv_id to centrality score
        """
        try:
            # PageRank is good for citation networks
            centrality = nx.pagerank(self.graph)
            return centrality
        except:
            # Fallback to simple degree centrality
            return nx.degree_centrality(self.graph)
    
    def get_graph_stats(self) -> Dict[str, any]:
        """Get statistics about the citation graph"""
        num_nodes = self.graph.number_of_nodes()
        
        return {
            'nodes': num_nodes,
            'edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph) if num_nodes > 0 else 0,
            'is_connected': nx.is_weakly_connected(self.graph) if num_nodes > 0 else False,
            'components': nx.number_weakly_connected_components(self.graph) if num_nodes > 0 else 0,
            'avg_degree': sum(dict(self.graph.degree()).values()) / max(num_nodes, 1)
        }
    
    def export_to_dict(self) -> Dict:
        """Export graph data for visualization"""
        nodes = []
        edges = []
        
        for node, data in self.graph.nodes(data=True):
            nodes.append({
                'id': node,
                'label': data.get('title', node)[:50],
                'title': data.get('title', 'Unknown'),
                'year': data.get('year', 'N/A'),
                'citations': data.get('citation_count', 0),
                'partial': data.get('partial', False)
            })
        
        for source, target, data in self.graph.edges(data=True):
            edges.append({
                'from': source,
                'to': target,
                'type': data.get('type', 'cites')
            })
        
        return {'nodes': nodes, 'edges': edges}
