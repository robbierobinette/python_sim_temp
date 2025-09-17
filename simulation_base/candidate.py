"""
Candidate representation for elections.
"""
from dataclasses import dataclass
from typing import Dict, Optional
from .population_tag import PopulationTag


@dataclass
class Candidate:
    """Represents a political candidate."""
    name: str
    tag: PopulationTag
    ideology: float
    money: float
    quality: float
    incumbent: bool = False
    affinity: Optional[Dict[PopulationTag, float]] = None
    median_voter: bool = False
    
    def __post_init__(self):
        """Initialize affinity dict if not provided."""
        if self.affinity is None:
            self.affinity = {}
    
    def __hash__(self) -> int:
        """Make Candidate hashable."""
        affinity_tuple = tuple(sorted(self.affinity.items())) if self.affinity else ()
        return hash((self.name, self.tag, self.ideology, self.money, self.quality, 
                    self.incumbent, self.median_voter, affinity_tuple))
