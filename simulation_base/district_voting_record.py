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
    
    @staticmethod
    def create_dummy(lean: float = 0.0, district_name: str = "TEST-00") -> "DistrictVotingRecord":
        """Create a dummy district voting record with specified lean.
        
        Args:
            lean: The expected lean of the district (positive = Republican, negative = Democratic)
            district_name: Name of the district (default: "TEST-00")
        
        Returns:
            A DistrictVotingRecord with appropriate percentages based on the lean
        """
        # Convert lean to party percentages
        # lean = 100 * (0.5 - d_pct / (d_pct + r_pct))
        # Solve for d_pct and r_pct
        r_pct = 0.5 + (lean / 200)  # lean/200 because lean is in percentage points
        d_pct = 0.5 - (lean / 200)
        
        return DistrictVotingRecord(
            district=district_name,
            incumbent="Test Incumbent",
            expected_lean=lean,
            d_pct1=d_pct,
            r_pct1=r_pct,
            d_pct2=d_pct,
            r_pct2=r_pct
        )