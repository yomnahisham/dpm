"""
cache.py - for saving fetched data so we don't download it again
"""

import os
import json
import hashlib
import time
import logging
from typing import Optional, Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)


class Cache:
    """for saving fetched data so we don't download it again"""
    
    def __init__(self, cache_dir: Optional[str] = None, ttl_hours: int = 24, max_size_mb: int = 100, enable_size_limit: bool = False):
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # default to ~/.dpm/cache
            home = Path.home()
            self.cache_dir = home / ".dpm" / "cache"
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_hours = ttl_hours
        self.max_size_mb = max_size_mb
        self.enable_size_limit = enable_size_limit  # disable by default for performance
        self.memory_cache: Dict[str, str] = {}  # in-memory cache for speed
        self._cached_size: Optional[int] = None  # cache the size calculation
        self._size_check_counter = 0  # only check size every N writes
    
    def _get_key_path(self, key: str) -> Path:
        """get file path for a cache key"""
        # hash the key to avoid filesystem issues with special chars
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
    
    def get(self, key: str) -> Optional[str]:
        """get something from cache (with TTL check)"""
        # check memory first (fastest)
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # check disk
        cache_file = self._get_key_path(key)
        if not cache_file.exists():
            return None
        
        try:
            # check TTL (only if TTL is enabled)
            if self.ttl_hours > 0:
                try:
                    age_seconds = time.time() - cache_file.stat().st_mtime
                    if age_seconds > self.ttl_hours * 3600:
                        # expired - remove it
                        try:
                            cache_file.unlink()
                        except Exception:
                            pass
                        if key in self.memory_cache:
                            del self.memory_cache[key]
                        return None
                except (OSError, FileNotFoundError):
                    # file might have been deleted, just return None
                    return None
            
            # read the file
            with open(cache_file, 'r') as f:
                data = json.load(f)
                value = data.get('value')
                if value:
                    # also store in memory for faster access
                    self.memory_cache[key] = value
                    return value
        except (json.JSONDecodeError, IOError, OSError) as e:
            # silently ignore cache read errors - just return None
            # don't log warnings for normal cache misses
            pass
        
        return None
    
    def set(self, key: str, value: str):
        """save something to cache (with optional size limit check)"""
        # size limit check is disabled by default for performance
        # only check if explicitly enabled and only periodically (every 100 writes)
        if self.enable_size_limit:
            self._size_check_counter += 1
            if self._size_check_counter >= 100:
                self._size_check_counter = 0
                # check cache size before writing (only periodically)
                try:
                    current_size = self._cache_size()
                    if current_size > self.max_size_mb * 1024 * 1024:
                        logger.info(f"Cache size limit reached ({self.max_size_mb}MB), evicting oldest entries")
                        self._evict_oldest()
                        self._cached_size = None  # invalidate cached size
                except Exception as e:
                    # don't fail on size check errors
                    logger.debug(f"Error checking cache size: {e}")
        
        # store in memory
        self.memory_cache[key] = value
        
        # store on disk (atomically)
        cache_file = self._get_key_path(key)
        try:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            # write atomically: write to temp file first, then rename
            temp_file = cache_file.with_suffix('.tmp')
            try:
                with open(temp_file, 'w') as f:
                    json.dump({'value': value}, f)
                # atomic rename
                temp_file.replace(cache_file)
            except Exception as e:
                # cleanup temp file on error
                if temp_file.exists():
                    try:
                        temp_file.unlink()
                    except Exception:
                        pass
                raise
        except Exception as e:
            logger.error(f"Failed to cache {key}: {e}")
    
    def _cache_size(self) -> int:
        """calculate total cache size in bytes (cached for performance)"""
        # use cached value if available and recent
        if self._cached_size is not None:
            return self._cached_size
        
        total = 0
        try:
            # only count actual cache files, not temp files
            for cache_file in self.cache_dir.glob("*.json"):
                if cache_file.is_file() and cache_file.suffix != '.tmp':
                    try:
                        total += cache_file.stat().st_size
                    except (OSError, FileNotFoundError):
                        # file might have been deleted
                        continue
        except Exception as e:
            logger.warning(f"Error calculating cache size: {e}")
        
        self._cached_size = total
        return total
    
    def _evict_oldest(self, target_size_mb: Optional[float] = None):
        """evict oldest cache entries until under size limit"""
        if target_size_mb is None:
            target_size_mb = self.max_size_mb * 0.8  # evict to 80% of limit
        
        try:
            # get all cache files with their modification times
            files = []
            for cache_file in self.cache_dir.glob("*.json"):
                if cache_file.is_file() and cache_file.suffix != '.tmp':
                    try:
                        mtime = cache_file.stat().st_mtime
                        size = cache_file.stat().st_size
                        files.append((mtime, size, cache_file))
                    except Exception:
                        continue
            
            # sort by modification time (oldest first)
            files.sort(key=lambda x: x[0])
            
            # remove oldest files until under target size
            current_size = self._cache_size()
            target_size = target_size_mb * 1024 * 1024
            
            for mtime, size, cache_file in files:
                if current_size <= target_size:
                    break
                try:
                    cache_file.unlink()
                    current_size -= size
                    # also remove from memory cache if present
                    # (we don't know the key, but that's ok - it will be reloaded if needed)
                    logger.debug(f"Evicted cache entry: {cache_file.name}")
                except Exception:
                    pass
            
            # invalidate cached size after eviction
            self._cached_size = None
        except Exception as e:
            logger.warning(f"Error evicting cache: {e}")
    
    def exists(self, key: str) -> bool:
        """check if something is in the cache"""
        if key in self.memory_cache:
            return True
        
        cache_file = self._get_key_path(key)
        return cache_file.exists()
    
    def clear(self):
        """clear the cache"""
        self.memory_cache.clear()
        self._cached_size = 0
        self._size_check_counter = 0
        if self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    cache_file.unlink()
                except Exception:
                    pass
    
    def get_info(self) -> Dict[str, any]:
        """get cache information"""
        cache_files = list(self.cache_dir.glob("*.json")) if self.cache_dir.exists() else []
        total_size = sum(f.stat().st_size for f in cache_files if f.exists())
        
        return {
            "location": str(self.cache_dir),
            "file_count": len(cache_files),
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
    
    def list_cached(self) -> List[str]:
        """list cached package names"""
        if not self.cache_dir.exists():
            return []
        
        cached = []
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    # try to extract package name from cache key (stored in filename hash)
                    # for now, just return file names
                    cached.append(cache_file.stem)
            except Exception:
                pass
        
        return cached

