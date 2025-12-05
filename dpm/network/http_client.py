"""
http_client.py - for making http requests with retry logic
"""

import urllib.request
import urllib.error
import time
import logging
from typing import Optional, List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

logger = logging.getLogger(__name__)


class HttpClient:
    """for making http requests with retry logic and proper error handling"""
    
    def __init__(self, offline: bool = False, max_retries: int = 3, timeout: int = 30, auth: Optional[Dict[str, str]] = None):
        self.timeout = timeout
        self.offline = offline
        self.max_retries = max_retries
        self.auth = auth  # {"username": "...", "password": "..."}
    
    def get(self, url: str) -> Optional[str]:
        """fetch a single url with retry logic"""
        if self.offline:
            logger.debug(f"Offline mode: skipping {url}")
            return None
        
        for attempt in range(self.max_retries):
            try:
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'DPM/1.0.0')
                
                # add authentication if provided
                if self.auth and "username" in self.auth and "password" in self.auth:
                    import base64
                    credentials = f"{self.auth['username']}:{self.auth['password']}"
                    encoded = base64.b64encode(credentials.encode()).decode()
                    req.add_header('Authorization', f'Basic {encoded}')
                
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    data = response.read().decode('utf-8')
                    if attempt > 0:
                        logger.info(f"Successfully fetched {url} on attempt {attempt + 1}")
                    return data
                    
            except urllib.error.HTTPError as e:
                # don't retry on client errors (4xx) except 429 (rate limit)
                if e.code == 429:
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limited (429) for {url}, retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries})")
                    if attempt < self.max_retries - 1:
                        time.sleep(wait_time)
                        continue
                elif 400 <= e.code < 500:
                    logger.error(f"Client error {e.code} for {url}: {e.reason}")
                    return None
                else:
                    # server error (5xx) - retry
                    wait_time = 2 ** attempt
                    logger.warning(f"Server error {e.code} for {url}, retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries})")
                    if attempt < self.max_retries - 1:
                        time.sleep(wait_time)
                        continue
                    logger.error(f"Failed to fetch {url} after {self.max_retries} attempts: HTTP {e.code}")
                    return None
                    
            except urllib.error.URLError as e:
                wait_time = 2 ** attempt
                logger.warning(f"URL error for {url}: {e.reason}, retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(wait_time)
                    continue
                logger.error(f"Failed to fetch {url} after {self.max_retries} attempts: {e.reason}")
                return None
                
            except Exception as e:
                logger.error(f"Unexpected error fetching {url}: {e}", exc_info=True)
                return None
        
        return None
    
    def get_parallel(self, urls: List[str], max_concurrent: int = 4) -> Dict[str, Optional[str]]:
        """fetch multiple urls at the same time"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            future_to_url = {executor.submit(self.get, url): url for url in urls}
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    results[url] = future.result()
                except Exception:
                    results[url] = None
        
        return results

