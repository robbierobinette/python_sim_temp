"""
Election definition containing all components needed for an election.
"""
from dataclasses import dataclass
from typing import List
from .candidate import Candidate
from .combined_population import CombinedPopulation
from .election_config import ElectionConfig
from .gaussian_generator import GaussianGenerator


@dataclass
class ElectionDefinition:
    """Complete definition of an election."""
    candidates: List[Candidate]
    population: CombinedPopulation
    config: ElectionConfig
    gaussian_generator: GaussianGenerator
