"""
Election configuration parameters.
"""
from dataclasses import dataclass


@dataclass
class ElectionConfig:
    """Configuration for election simulation."""
    uncertainty: float
    party_loyalty: float
    quality_scale: float
    party_bonus_scale: float
    wasted_vote_factor: float = 0.0
