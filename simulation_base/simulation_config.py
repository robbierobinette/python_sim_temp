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
                 candidate_generator: CandidateGenerator, primary_skew: float):
        """Initialize simulation configuration."""
        self.label = label
        self.config = config
        self.pop_config = pop_config
        self.candidate_generator = candidate_generator
        self.primary_skew = primary_skew
    
    def describe(self) -> str:
        """Get description of the configuration."""
        return (f"label: {self.label} "
                f"primarySkew: {self.primary_skew} "
                f"qualityNoise: {self.candidate_generator.quality_variance} "
                f"wastedVoteFactor: {self.config.wasted_vote_factor} "
                f"uncertainty: {self.config.uncertainty} "
                f"partyLoyalty: {self.config.party_loyalty} "
                f"qualityScale: {self.config.quality_scale} "
                f"partyBonus: {self.config.party_bonus_scale}")


class UnitSimulationConfig(CongressionalSimulationConfig):
    """Unit simulation configuration."""
    
    def __init__(self, label: str, config: ElectionConfig, pop_config: PopulationConfiguration,
                 candidate_generator: CandidateGenerator, primary_skew: float, n_voters: int = 1000):
        """Initialize unit simulation configuration."""
        super().__init__(label, config, pop_config, candidate_generator, primary_skew)
        self.n_voters = n_voters
    
    def generate_definition(self, dvr, gaussian_generator: Optional[GaussianGenerator] = None):
        """Generate election definition for a district."""
        from .unit_population import UnitPopulation
        from .election_definition import ElectionDefinition
        
        if gaussian_generator is None:
            gaussian_generator = GaussianGenerator()
        
        district_pop = UnitPopulation.create_with_params(
            dvr, self.pop_config.partisanship, self.pop_config.stddev, 
            self.pop_config.population_skew, self.n_voters
        )
        
        candidates = self.candidate_generator.candidates(district_pop)
        candidates.sort(key=lambda c: c.ideology)
        
        return ElectionDefinition(candidates, district_pop, self.config, gaussian_generator)


class CongressionalSimulationConfigFactory:
    """Factory for creating simulation configurations."""
    
    @staticmethod
    def create_config(n_party_candidates: int, 
                     gaussian_generator: Optional[GaussianGenerator] = None,
                     n_voters: int = 1000,
                     uncertainty: float = 0.5) -> UnitSimulationConfig:
        """Create simulation configuration."""
        if gaussian_generator is None:
            gaussian_generator = GaussianGenerator()
        
        election_config = ElectionConfig(
            uncertainty=uncertainty,
            party_loyalty=1.0,
            quality_scale=1.0,
            party_bonus_scale=1.0,
            wasted_vote_factor=0.0
        )
        
        population_config = PopulationConfiguration(1, 1, 0.5 / 30)
        
        from .candidate_generator import RankCandidateGenerator
        # candidate_generator = RankCandidateGenerator(
        #     n_party_candidates, spread=0.16, offset=0.24, 
        #     ideology_variance=0.06, quality_variance=0,
        #     gaussian_generator=gaussian_generator
        # )

        from .candidate_generator import PartisanCandidateGenerator
        candidate_generator = PartisanCandidateGenerator(
            n_party_candidates, 
            spread=0.2, 
            ideology_variance=0.1, 
            quality_variance=0.001,
            primary_skew = 0,
            gaussian_generator=gaussian_generator
        )
        
        return UnitSimulationConfig(
            label="unitConfig",
            config=election_config,
            pop_config=population_config,
            candidate_generator=candidate_generator,
            primary_skew=0.5,
            n_voters=n_voters
        )
