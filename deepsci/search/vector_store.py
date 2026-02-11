"""
Vector search engine using ChromaDB and sentence-transformers
Enables semantic paper discovery and personal research library
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib


class VectorStore:
    """Vector database for semantic paper search"""
    
    def __init__(self, persist_directory: str = "./data/vectordb"):
        """
        Initialize vector store
        
        Args:
            persist_directory: Directory to persist the database
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="physics_papers",
            metadata={"description": "Physics research papers from arXiv"}
        )
        
        # Initialize embedding model (lightweight model for CPU)
        # all-MiniLM-L6-v2: 384 dimensions, ~23MB, fast on CPU
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def _create_paper_id(self, paper_id: str) -> str:
        """Create a unique ID for a paper"""
        return hashlib.md5(paper_id.encode()).hexdigest()
    
    def _create_embedding_text(self, paper: Dict[str, Any]) -> str:
        """
        Create text for embedding from paper metadata
        
        Args:
            paper: Paper dictionary with title, abstract, authors
            
        Returns:
            Combined text for embedding
        """
        title = paper.get('title', '')
        abstract = paper.get('abstract', '')
        authors = ', '.join(paper.get('authors', [])[:5])
        
        # Combine with weights (title is more important)
        text = f"{title}. {title}. {abstract}"
        return text
    
    def add_paper(self, paper: Dict[str, Any]) -> bool:
        """
        Add a paper to the vector store
        
        Args:
            paper: Paper dictionary with id, title, abstract, authors, etc.
            
        Returns:
            True if added successfully
        """
        try:
            paper_id = paper.get('id', '')
            if not paper_id:
                return False
            
            # Create embedding text
            text = self._create_embedding_text(paper)
            
            # Generate embedding
            embedding = self.model.encode(text).tolist()
            
            # Prepare metadata
            metadata = {
                'arxiv_id': paper_id,
                'title': paper.get('title', '')[:500],  # Limit length
                'authors': ', '.join(paper.get('authors', [])[:5])[:300],
                'year': str(paper.get('year', '')),
                'categories': ', '.join(paper.get('categories', [])[:5])[:200],
                'citation_count': paper.get('citation_count', 0),
                'url': paper.get('url', '')
            }
            
            # Add to collection
            unique_id = self._create_paper_id(paper_id)
            self.collection.add(
                ids=[unique_id],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[paper.get('abstract', '')[:1000]]  # Store abstract snippet
            )
            
            return True
            
        except Exception as e:
            print(f"Error adding paper: {e}")
            return False
    
    def add_papers(self, papers: List[Dict[str, Any]]) -> int:
        """
        Add multiple papers to the vector store
        
        Args:
            papers: List of paper dictionaries
            
        Returns:
            Number of papers added successfully
        """
        count = 0
        for paper in papers:
            if self.add_paper(paper):
                count += 1
        return count
    
    def search(self, query: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Semantic search for papers
        
        Args:
            query: Search query (can be a question or topic)
            n_results: Number of results to return
            
        Returns:
            List of matching papers with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.model.encode(query).tolist()
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Format results
            papers = []
            if results['ids'] and len(results['ids']) > 0:
                for i in range(len(results['ids'][0])):
                    paper = {
                        'id': results['metadatas'][0][i].get('arxiv_id', ''),
                        'title': results['metadatas'][0][i].get('title', ''),
                        'authors': results['metadatas'][0][i].get('authors', '').split(', '),
                        'year': results['metadatas'][0][i].get('year', ''),
                        'categories': results['metadatas'][0][i].get('categories', '').split(', '),
                        'citation_count': results['metadatas'][0][i].get('citation_count', 0),
                        'url': results['metadatas'][0][i].get('url', ''),
                        'abstract': results['documents'][0][i] if results['documents'] else '',
                        'similarity': 1 - results['distances'][0][i],  # Convert distance to similarity
                        'source': 'library'
                    }
                    papers.append(paper)
            
            return papers
            
        except Exception as e:
            print(f"Error searching: {e}")
            return []
    
    def find_similar(self, paper_id: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Find papers similar to a given paper
        
        Args:
            paper_id: arXiv ID of the paper
            n_results: Number of similar papers to return
            
        Returns:
            List of similar papers
        """
        try:
            unique_id = self._create_paper_id(paper_id)
            
            # Get the paper's embedding
            result = self.collection.get(
                ids=[unique_id],
                include=['embeddings']
            )
            
            if not result['embeddings'] or len(result['embeddings']) == 0:
                return []
            
            embedding = result['embeddings'][0]
            
            # Search for similar papers
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=n_results + 1  # +1 because it will include the paper itself
            )
            
            # Format and filter out the original paper
            papers = []
            if results['ids'] and len(results['ids']) > 0:
                for i in range(len(results['ids'][0])):
                    arxiv_id = results['metadatas'][0][i].get('arxiv_id', '')
                    if arxiv_id != paper_id:  # Skip the original paper
                        paper = {
                            'id': arxiv_id,
                            'title': results['metadatas'][0][i].get('title', ''),
                            'authors': results['metadatas'][0][i].get('authors', '').split(', '),
                            'year': results['metadatas'][0][i].get('year', ''),
                            'categories': results['metadatas'][0][i].get('categories', '').split(', '),
                            'citation_count': results['metadatas'][0][i].get('citation_count', 0),
                            'url': results['metadatas'][0][i].get('url', ''),
                            'abstract': results['documents'][0][i] if results['documents'] else '',
                            'similarity': 1 - results['distances'][0][i],
                            'source': 'library'
                        }
                        papers.append(paper)
            
            return papers[:n_results]
            
        except Exception as e:
            print(f"Error finding similar papers: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store
        
        Returns:
            Dictionary with stats
        """
        try:
            count = self.collection.count()
            return {
                'total_papers': count,
                'model': 'all-MiniLM-L6-v2',
                'dimensions': 384,
                'collection_name': self.collection.name
            }
        except:
            return {'total_papers': 0}
    
    def paper_exists(self, paper_id: str) -> bool:
        """Check if a paper is already in the store"""
        try:
            unique_id = self._create_paper_id(paper_id)
            result = self.collection.get(ids=[unique_id])
            return len(result['ids']) > 0
        except:
            return False
    
    def delete_paper(self, paper_id: str) -> bool:
        """Delete a paper from the store"""
        try:
            unique_id = self._create_paper_id(paper_id)
            self.collection.delete(ids=[unique_id])
            return True
        except:
            return False
    
    def clear_all(self) -> bool:
        """Clear all papers from the store"""
        try:
            self.client.delete_collection(name="physics_papers")
            self.collection = self.client.create_collection(
                name="physics_papers",
                metadata={"description": "Physics research papers from arXiv"}
            )
            return True
        except:
            return False
