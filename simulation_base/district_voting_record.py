"""
District voting record representation.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class DistrictVotingRecord:
    """Represents voting history and characteristics of a district."""
    district: str
    incumbent: str
    expected_lean: float
    d_pct1: float
    r_pct1: float
    d_pct2: float
    r_pct2: float
    
    @property
    def state(self) -> str:
        """Extract state from district name."""
        return self.district.split("-")[0]
    
    @property
    def lean(self) -> float:
        """Calculate lean from voting percentages."""
        l1 = 0.5 - self.d_pct1 / (self.d_pct1 + self.r_pct1)
        l2 = 0.5 - self.d_pct2 / (self.d_pct2 + self.r_pct2)
        return 100 * (l1 + l2) / 2
    
    @property
    def direction(self) -> str:
        """Get political direction of the district."""
        return "right" if self.lean > 0 else "left"
    
    def __str__(self) -> str:
        """String representation of the district."""
        return f"{self.district:5s} {self.incumbent:30s} {self.lean:6.2f}"
