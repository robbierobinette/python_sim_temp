"""
Population tags representing different political parties and groups.
"""
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class PopulationTag:
    """Represents a political party or group."""
    name: str
    short_name: str
    plural_name: str
    hex_color: str
    affinity: Dict[str, float]
    
    def __hash__(self) -> int:
        """Make PopulationTag hashable."""
        return hash((self.name, self.short_name, self.plural_name, self.hex_color, tuple(sorted(self.affinity.items()))))
    
    @property
    def initial(self) -> str:
        """First letter of short name."""
        return self.short_name[0]
    
    def party_affinity(self, other: 'PopulationTag') -> float:
        """Get affinity score for another party."""
        return self.affinity.get(other.short_name, 0.0)
    
    def __str__(self) -> str:
        return self.name
    
    def __lt__(self, other: 'PopulationTag') -> bool:
        return self.short_name < other.short_name


# Standard political parties
DEMOCRATS = PopulationTag(
    name="Democratic",
    short_name="Dem",
    plural_name="Democrats",
    hex_color="#0000ff",
    affinity={
        "Rep": 0.0,
        "Ind": 0.75,
        "Dem": 1.5,
        "Maga": -1.0,
        "Pro": 1.5
    }
)

REPUBLICANS = PopulationTag(
    name="Republican",
    short_name="Rep",
    plural_name="Republicans",
    hex_color="#ff0000",
    affinity={
        "Rep": 1.5,
        "Ind": 0.75,
        "Dem": 0.0,
        "Maga": 1.5,
        "Pro": -1.0
    }
)

INDEPENDENTS = PopulationTag(
    name="Independent",
    short_name="Ind",
    plural_name="Independents",
    hex_color="#ff00ff",
    affinity={
        "Rep": 0.0,
        "Ind": 0.0,
        "Dem": 0.0,
        "Maga": 0.0,
        "Pro": 0.0
    }
)

MAGA = PopulationTag(
    name="MAGA",
    short_name="Maga",
    plural_name="Magas",
    hex_color="#ff8888",
    affinity={
        "Rep": 1.0,
        "Ind": 0.5,
        "Dem": 0.0,
        "Maga": 1.25,
        "Pro": -1.0
    }
)

PROGRESSIVE = PopulationTag(
    name="Progressive",
    short_name="Pro",
    plural_name="Progressives",
    hex_color="#8888ff",
    affinity={
        "Rep": 0.0,
        "Ind": 0.5,
        "Dem": 1.0,
        "Maga": -1.0,
        "Pro": 1.25
    }
)


def get_party_by_short_name(short_name: str) -> PopulationTag:
    """Get party by short name."""
    party_map = {
        "Rep": REPUBLICANS,
        "Dem": DEMOCRATS,
        "Ind": INDEPENDENTS,
        "Maga": MAGA,
        "Pro": PROGRESSIVE
    }
    return party_map.get(short_name, INDEPENDENTS)
