"""
resolver.py - hybrid dependency resolver (greedy first, backtracking fallback)
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from .greedy import GreedyResolver, GreedyResult
from .backtrack import BacktrackResolver, BacktrackResult
from ..sources.source import Source


@dataclass
class ResolutionResult:
    """result from dependency resolution"""
    success: bool
    selected_versions: Dict[str, str]
    used_backtracking: bool = False
    error_message: str = ""
    conflict_details: Dict[str, List[str]] = None  # package -> list of conflicting requirements
    dependency_graph: Optional[object] = None  # reference to dependency graph for visualization


class DependencyResolver:
    """hybrid dependency resolver - tries greedy first, falls back to backtracking"""
    
    def __init__(self):
        self.greedy_resolver = GreedyResolver()
        self.backtrack_resolver = BacktrackResolver()
    
    def resolve(self, requested_packages: List[str], sources: List[Source], 
                timeout_seconds: int = 60) -> ResolutionResult:
        """resolve dependencies using hybrid approach with timeout"""
        import time
        import logging
        
        logger = logging.getLogger(__name__)
        start_time = time.time()
        
        def check_timeout():
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                raise TimeoutError(f"Resolution timed out after {timeout_seconds}s")
        
        try:
            # try greedy first (fast)
            check_timeout()
            greedy_result = self.greedy_resolver.resolve(requested_packages, sources)
            
            if greedy_result.success:
                elapsed = time.time() - start_time
                logger.debug(f"Greedy resolution completed in {elapsed:.2f}s")
                return ResolutionResult(
                    success=True,
                    selected_versions=greedy_result.selected_versions,
                    used_backtracking=False,
                    conflict_details={}
                )
            
            # greedy failed, try backtracking (slower but more thorough)
            check_timeout()
            logger.info("Greedy resolution failed, trying backtracking...")
            initial_selections = greedy_result.selected_versions.copy()
            backtrack_result = self.backtrack_resolver.resolve(
                requested_packages, initial_selections, sources
            )
            
            elapsed = time.time() - start_time
            logger.debug(f"Backtracking resolution completed in {elapsed:.2f}s")
            
            if backtrack_result.success:
                return ResolutionResult(
                    success=True,
                    selected_versions=backtrack_result.selected_versions,
                    used_backtracking=True,
                    conflict_details={}
                )
            
            # both failed - provide detailed conflict information
            error_msg = greedy_result.conflict_reason
            if not error_msg:
                error_msg = backtrack_result.failure_reason
            if not error_msg:
                error_msg = "Failed to resolve dependencies"
            
            return ResolutionResult(
                success=False,
                selected_versions={},
                used_backtracking=True,
                error_message=error_msg,
                conflict_details=greedy_result.conflict_details or {}
            )
        except TimeoutError as e:
            logger.error(str(e))
            return ResolutionResult(
                success=False,
                selected_versions={},
                used_backtracking=True,
                error_message=str(e)
            )


"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from .greedy import GreedyResolver, GreedyResult
from .backtrack import BacktrackResolver, BacktrackResult
from ..sources.source import Source


@dataclass
class ResolutionResult:
    """result from dependency resolution"""
    success: bool
    selected_versions: Dict[str, str]
    used_backtracking: bool = False
    error_message: str = ""
    conflict_details: Dict[str, List[str]] = None  # package -> list of conflicting requirements
    dependency_graph: Optional[object] = None  # reference to dependency graph for visualization


class DependencyResolver:
    """hybrid dependency resolver - tries greedy first, falls back to backtracking"""
    
    def __init__(self):
        self.greedy_resolver = GreedyResolver()
        self.backtrack_resolver = BacktrackResolver()
    
    def resolve(self, requested_packages: List[str], sources: List[Source], 
                timeout_seconds: int = 60) -> ResolutionResult:
        """resolve dependencies using hybrid approach with timeout"""
        import time
        import logging
        
        logger = logging.getLogger(__name__)
        start_time = time.time()
        
        def check_timeout():
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                raise TimeoutError(f"Resolution timed out after {timeout_seconds}s")
        
        try:
            # try greedy first (fast)
            check_timeout()
            greedy_result = self.greedy_resolver.resolve(requested_packages, sources)
            
            if greedy_result.success:
                elapsed = time.time() - start_time
                logger.debug(f"Greedy resolution completed in {elapsed:.2f}s")
                return ResolutionResult(
                    success=True,
                    selected_versions=greedy_result.selected_versions,
                    used_backtracking=False,
                    conflict_details={}
                )
            
            # greedy failed, try backtracking (slower but more thorough)
            check_timeout()
            logger.info("Greedy resolution failed, trying backtracking...")
            initial_selections = greedy_result.selected_versions.copy()
            backtrack_result = self.backtrack_resolver.resolve(
                requested_packages, initial_selections, sources
            )
            
            elapsed = time.time() - start_time
            logger.debug(f"Backtracking resolution completed in {elapsed:.2f}s")
            
            if backtrack_result.success:
                return ResolutionResult(
                    success=True,
                    selected_versions=backtrack_result.selected_versions,
                    used_backtracking=True,
                    conflict_details={}
                )
            
            # both failed - provide detailed conflict information
            error_msg = greedy_result.conflict_reason
            if not error_msg:
                error_msg = backtrack_result.failure_reason
            if not error_msg:
                error_msg = "Failed to resolve dependencies"
            
            return ResolutionResult(
                success=False,
                selected_versions={},
                used_backtracking=True,
                error_message=error_msg,
                conflict_details=greedy_result.conflict_details or {}
            )
        except TimeoutError as e:
            logger.error(str(e))
            return ResolutionResult(
                success=False,
                selected_versions={},
                used_backtracking=True,
                error_message=str(e)
            )


"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from .greedy import GreedyResolver, GreedyResult
from .backtrack import BacktrackResolver, BacktrackResult
from ..sources.source import Source


@dataclass
class ResolutionResult:
    """result from dependency resolution"""
    success: bool
    selected_versions: Dict[str, str]
    used_backtracking: bool = False
    error_message: str = ""
    conflict_details: Dict[str, List[str]] = None  # package -> list of conflicting requirements
    dependency_graph: Optional[object] = None  # reference to dependency graph for visualization


class DependencyResolver:
    """hybrid dependency resolver - tries greedy first, falls back to backtracking"""
    
    def __init__(self):
        self.greedy_resolver = GreedyResolver()
        self.backtrack_resolver = BacktrackResolver()
    
    def resolve(self, requested_packages: List[str], sources: List[Source], 
                timeout_seconds: int = 60) -> ResolutionResult:
        """resolve dependencies using hybrid approach with timeout"""
        import time
        import logging
        
        logger = logging.getLogger(__name__)
        start_time = time.time()
        
        def check_timeout():
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                raise TimeoutError(f"Resolution timed out after {timeout_seconds}s")
        
        try:
            # try greedy first (fast)
            check_timeout()
            greedy_result = self.greedy_resolver.resolve(requested_packages, sources)
            
            if greedy_result.success:
                elapsed = time.time() - start_time
                logger.debug(f"Greedy resolution completed in {elapsed:.2f}s")
                return ResolutionResult(
                    success=True,
                    selected_versions=greedy_result.selected_versions,
                    used_backtracking=False,
                    conflict_details={}
                )
            
            # greedy failed, try backtracking (slower but more thorough)
            check_timeout()
            logger.info("Greedy resolution failed, trying backtracking...")
            initial_selections = greedy_result.selected_versions.copy()
            backtrack_result = self.backtrack_resolver.resolve(
                requested_packages, initial_selections, sources
            )
            
            elapsed = time.time() - start_time
            logger.debug(f"Backtracking resolution completed in {elapsed:.2f}s")
            
            if backtrack_result.success:
                return ResolutionResult(
                    success=True,
                    selected_versions=backtrack_result.selected_versions,
                    used_backtracking=True,
                    conflict_details={}
                )
            
            # both failed - provide detailed conflict information
            error_msg = greedy_result.conflict_reason
            if not error_msg:
                error_msg = backtrack_result.failure_reason
            if not error_msg:
                error_msg = "Failed to resolve dependencies"
            
            return ResolutionResult(
                success=False,
                selected_versions={},
                used_backtracking=True,
                error_message=error_msg,
                conflict_details=greedy_result.conflict_details or {}
            )
        except TimeoutError as e:
            logger.error(str(e))
            return ResolutionResult(
                success=False,
                selected_versions={},
                used_backtracking=True,
                error_message=str(e)
            )


"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from .greedy import GreedyResolver, GreedyResult
from .backtrack import BacktrackResolver, BacktrackResult
from ..sources.source import Source


@dataclass
class ResolutionResult:
    """result from dependency resolution"""
    success: bool
    selected_versions: Dict[str, str]
    used_backtracking: bool = False
    error_message: str = ""
    conflict_details: Dict[str, List[str]] = None  # package -> list of conflicting requirements
    dependency_graph: Optional[object] = None  # reference to dependency graph for visualization


class DependencyResolver:
    """hybrid dependency resolver - tries greedy first, falls back to backtracking"""
    
    def __init__(self):
        self.greedy_resolver = GreedyResolver()
        self.backtrack_resolver = BacktrackResolver()
    
    def resolve(self, requested_packages: List[str], sources: List[Source], 
                timeout_seconds: int = 60) -> ResolutionResult:
        """resolve dependencies using hybrid approach with timeout"""
        import time
        import logging
        
        logger = logging.getLogger(__name__)
        start_time = time.time()
        
        def check_timeout():
            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                raise TimeoutError(f"Resolution timed out after {timeout_seconds}s")
        
        try:
            # try greedy first (fast)
            check_timeout()
            greedy_result = self.greedy_resolver.resolve(requested_packages, sources)
            
            if greedy_result.success:
                elapsed = time.time() - start_time
                logger.debug(f"Greedy resolution completed in {elapsed:.2f}s")
                return ResolutionResult(
                    success=True,
                    selected_versions=greedy_result.selected_versions,
                    used_backtracking=False,
                    conflict_details={}
                )
            
            # greedy failed, try backtracking (slower but more thorough)
            check_timeout()
            logger.info("Greedy resolution failed, trying backtracking...")
            initial_selections = greedy_result.selected_versions.copy()
            backtrack_result = self.backtrack_resolver.resolve(
                requested_packages, initial_selections, sources
            )
            
            elapsed = time.time() - start_time
            logger.debug(f"Backtracking resolution completed in {elapsed:.2f}s")
            
            if backtrack_result.success:
                return ResolutionResult(
                    success=True,
                    selected_versions=backtrack_result.selected_versions,
                    used_backtracking=True,
                    conflict_details={}
                )
            
            # both failed - provide detailed conflict information
            error_msg = greedy_result.conflict_reason
            if not error_msg:
                error_msg = backtrack_result.failure_reason
            if not error_msg:
                error_msg = "Failed to resolve dependencies"
            
            return ResolutionResult(
                success=False,
                selected_versions={},
                used_backtracking=True,
                error_message=error_msg,
                conflict_details=greedy_result.conflict_details or {}
            )
        except TimeoutError as e:
            logger.error(str(e))
            return ResolutionResult(
                success=False,
                selected_versions={},
                used_backtracking=True,
                error_message=str(e)
            )

