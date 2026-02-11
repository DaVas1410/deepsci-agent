"""
Citation cache to store and reuse citation data
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class CitationCache:
    """Cache citation data to avoid repeated API calls"""
    
    def __init__(self, cache_file: str = "./data/citation_cache.json", cache_days: int = 7):
        """
        Initialize citation cache
        
        Args:
            cache_file: Path to cache file
            cache_days: Number of days to keep cache entries
        """
        self.cache_file = Path(cache_file)
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache_days = cache_days
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from disk"""
        if not self.cache_file.exists():
            return {}
        
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_cache(self):
        """Save cache to disk"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save citation cache: {e}")
    
    def get(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached citation data
        
        Args:
            paper_id: Paper identifier (arXiv ID, DOI, etc.)
            
        Returns:
            Cached data or None if not found/expired
        """
        if paper_id not in self.cache:
            return None
        
        entry = self.cache[paper_id]
        
        # Check if expired
        cached_time = datetime.fromisoformat(entry['cached_at'])
        if datetime.now() - cached_time > timedelta(days=self.cache_days):
            del self.cache[paper_id]
            self._save_cache()
            return None
        
        return entry['data']
    
    def set(self, paper_id: str, data: Dict[str, Any]):
        """
        Cache citation data
        
        Args:
            paper_id: Paper identifier
            data: Citation data to cache
        """
        self.cache[paper_id] = {
            'data': data,
            'cached_at': datetime.now().isoformat()
        }
        self._save_cache()
    
    def clear_expired(self):
        """Remove expired entries from cache"""
        now = datetime.now()
        expired_keys = []
        
        for key, entry in self.cache.items():
            cached_time = datetime.fromisoformat(entry['cached_at'])
            if now - cached_time > timedelta(days=self.cache_days):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self._save_cache()
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        total = len(self.cache)
        
        # Count expired
        now = datetime.now()
        expired = 0
        for entry in self.cache.values():
            cached_time = datetime.fromisoformat(entry['cached_at'])
            if now - cached_time > timedelta(days=self.cache_days):
                expired += 1
        
        return {
            'total_entries': total,
            'valid_entries': total - expired,
            'expired_entries': expired
        }
