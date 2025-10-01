"""
Candidate representation for elections.
"""
from dataclasses import dataclass, field
from typing import Dict, Optional
from .population_tag import PopulationTag


@dataclass
class Candidate:
    """Represents a political candidate."""
    name: str
    tag: PopulationTag
    ideology: float
    quality: float
    incumbent: bool = False
    _affinity_map: Optional[Dict[str, float]] = field(default=None, init=False)
    
    def __post_init__(self):
        """Initialize affinity dict if not provided."""
        if self._affinity_map is None:
            # Initialize with party's affinity map
            self._affinity_map = self.tag.affinity.copy()
    
    def affinity(self, group: str) -> float:
        """Get affinity for a specific group.
        
        Args:
            group: The group name (e.g., "Dem", "Rep", "Ind")
            
        Returns:
            The affinity value for the group
            
        Raises:
            KeyError: If the group is not found in the affinity map
        """
        if group not in self._affinity_map:
            raise KeyError(f"Unknown group '{group}' in affinity map. Available groups: {list(self._affinity_map.keys())}")
        return self._affinity_map[group]
    
    def __hash__(self) -> int:
        """Make Candidate hashable."""
        affinity_tuple = tuple(sorted(self._affinity_map.items())) if self._affinity_map else ()
        return hash((self.name, self.tag, self.ideology, self.quality, 
                    self.incumbent, affinity_tuple))
    
    def affinity_string(self) -> str:
        """Return a string representation of the candidate's affinity."""
        return ", ".join([f"{k:5s}: {v: 6.2f}" for k, v in self._affinity_map.items()])
