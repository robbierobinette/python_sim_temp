"""
Abstract base class for election processes.
"""
from abc import ABC, abstractmethod
from .election_result import ElectionResult
from .election_definition import ElectionDefinition


class ElectionProcess(ABC):
    """Abstract base class for all election processes."""
    
    @abstractmethod
    def run(self, election_def: ElectionDefinition) -> ElectionResult:
        """Run an election with the given election definition.
        
        Args:
            election_def: Complete election definition with candidates, population, config, etc.
            
        Returns:
            ElectionResult with winner, voter_satisfaction, and ordered_results
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the election process."""
        pass

