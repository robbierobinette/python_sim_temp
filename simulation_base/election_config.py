"""
Election configuration parameters.
"""
from dataclasses import dataclass


@dataclass
class ElectionConfig:
    """Configuration for election simulation."""
    uncertainty: float
