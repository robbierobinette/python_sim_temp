"""
Simulation configuration for congressional elections.
"""
from dataclasses import dataclass
from typing import Optional
from .election_config import ElectionConfig
from .candidate_generator import CandidateGenerator
from .gaussian_generator import GaussianGenerator


@dataclass
class PopulationConfiguration:
    """Configuration for population generation."""
    partisanship: float
    stddev: float
    population_skew: float


class CongressionalSimulationConfig:
    """Configuration for congressional simulation."""
    
    def __init__(self, label: str, config: ElectionConfig, pop_config: PopulationConfiguration,
                 candidate_generator: CandidateGenerator, primary_skew: float, nvoters: int = 1000):
        """Initialize simulation configuration."""
        self.label = label
        self.config = config
        self.pop_config = pop_config
        self.candidate_generator = candidate_generator
        self.primary_skew = primary_skew
        self.nvoters = nvoters
    
    def describe(self) -> str:
        """Get description of the configuration."""
        return (f"label: {self.label} "
                f"primarySkew: {self.primary_skew} "
                f"qualityNoise: {self.candidate_generator.quality_variance} "
                f"uncertainty: {self.config.uncertainty} " )


class UnitSimulationConfig(CongressionalSimulationConfig):
    """Unit simulation configuration."""
    
    def generate_definition(self, dvr, gaussian_generator: Optional[GaussianGenerator] = None):
        """Generate election definition for a district."""
        from .unit_population import UnitPopulation
        from .election_definition import ElectionDefinition
        
        if gaussian_generator is None:
            gaussian_generator = GaussianGenerator()
        
        district_pop = UnitPopulation.create_with_params(
            dvr, self.pop_config.partisanship, self.pop_config.stddev, 
            self.pop_config.population_skew, self.nvoters)
        
        candidates = self.candidate_generator.candidates(district_pop)
        candidates.sort(key=lambda c: c.ideology)
        
        return ElectionDefinition(candidates, district_pop, self.config, gaussian_generator)


class CongressionalSimulationConfigFactory:
    """Factory for creating simulation configurations."""
    
    @staticmethod
    def create_config(params: dict) -> UnitSimulationConfig:
        """Create simulation configuration."""
        # Extract parameters directly from params (no defaults; will raise KeyError if missing)
        candidates = params['candidates']
        gaussian_generator = params['gaussian_generator']
        nvoters = params['nvoters']
        uncertainty = params['uncertainty']
        primary_skew = params['primary_skew']
        candidate_generator_type = params['candidate_generator_type']
        election_type = params['election_type']
        ideology_variance = params['ideology_variance']
        spread = params['spread']
        quality_variance = params['quality_variance']
        condorcet_variance = params['condorcet_variance']
        partisan_shift = params['partisan_shift']
        
        election_config = ElectionConfig(
            uncertainty=uncertainty,
        )
        
        population_config = PopulationConfiguration(1, 1, partisan_shift)
        
        # Create candidate generator based on type
        if candidate_generator_type == "condorcet":
            from .candidate_generator import CondorcetCandidateGenerator
            candidate_generator = CondorcetCandidateGenerator(
                n_candidates=candidates,  # Total number of candidates for Condorcet
                ideology_variance=condorcet_variance,
                quality_variance=quality_variance,
                gaussian_generator=gaussian_generator
            )
        elif candidate_generator_type == "random":
            from .candidate_generator import RandomCandidateGenerator
            candidate_generator = RandomCandidateGenerator(
                n_candidates=candidates,  # Total number of candidates for Random
                quality_variance=quality_variance,
                median_variance=condorcet_variance,
                n_median_candidates=0,  # No median candidates for random
                gaussian_generator=gaussian_generator
            )
        elif candidate_generator_type == "normal-partisan":
            from .candidate_generator import NormalPartisanCandidateGenerator
            effective_primary_skew = primary_skew if election_type == "primary" else 0.0
            candidate_generator = NormalPartisanCandidateGenerator(
                n_partisan_candidates=candidates,  # Number per party for normal-partisan
                ideology_variance=ideology_variance,
                quality_variance=quality_variance,
                primary_skew=effective_primary_skew,
                median_variance=condorcet_variance,
                gaussian_generator=gaussian_generator
            )
        else:  # partisan (default)
            from .candidate_generator import PartisanCandidateGenerator
            # Only use primary_skew for primary elections
            effective_primary_skew = primary_skew if election_type == "primary" else 0.0
            candidate_generator = PartisanCandidateGenerator(
                n_party_candidates=candidates,  # Number per party for partisan
                spread=spread, 
                ideology_variance=ideology_variance, 
                median_variance=condorcet_variance,
                quality_variance=quality_variance,
                primary_skew=effective_primary_skew,
                gaussian_generator=gaussian_generator
            )
        
        return UnitSimulationConfig(
            label="unitConfig",
            config=election_config,
            pop_config=population_config,
            candidate_generator=candidate_generator,
            primary_skew=primary_skew,
            nvoters=nvoters
        )
