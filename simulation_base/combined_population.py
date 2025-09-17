"""
Combined population representing multiple voter groups.
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
import random
from .population_group import PopulationGroup
from .population_tag import PopulationTag, DEMOCRATS, REPUBLICANS, INDEPENDENTS
from .voter import Voter
from .gaussian_generator import GaussianGenerator


@dataclass
class CombinedPopulation:
    """Combined population of multiple voter groups."""
    populations: List[PopulationGroup]
    desired_samples: int = 1000
    
    def __post_init__(self):
        """Initialize population after creation."""
        self.party_map: Dict[PopulationTag, PopulationGroup] = {
            p.tag: p for p in self.populations
        }
        self.summed_weight: float = sum(p.weight for p in self.populations)
        self.sample_population: List[Voter] = self._population_sample(self.desired_samples)
        self.sample_population.sort(key=lambda v: v.ideology)
        self.median_voter: float = self.sample_population[len(self.sample_population) // 2].ideology
    
    @property
    def n_samples(self) -> int:
        """Number of samples in the population."""
        return len(self.sample_population)
    
    @property
    def voters(self) -> List[Voter]:
        """Get all voters in the population."""
        return self.sample_population
    
    def dominant_party(self, gaussian_generator: Optional[GaussianGenerator] = None) -> PopulationTag:
        """Determine the dominant party in the population."""
        if gaussian_generator is None:
            gaussian_generator = GaussianGenerator()
        
        dem_weight = self.democrats.weight
        rep_weight = self.republicans.weight
        
        if dem_weight > rep_weight:
            return DEMOCRATS
        elif rep_weight > dem_weight:
            return REPUBLICANS
        else:
            return DEMOCRATS if gaussian_generator.next_boolean() else REPUBLICANS
    
    def stats(self) -> str:
        """Get statistics for all population groups."""
        return " ".join(p.stats() for p in self.populations)
    
    def __getitem__(self, tag: PopulationTag) -> PopulationGroup:
        """Get population group by tag."""
        return self.party_map[tag]
    
    def party_for_tag(self, tag: PopulationTag) -> PopulationGroup:
        """Get population group by tag."""
        return self.party_map[tag]
    
    def party_for_name(self, name: str) -> PopulationGroup:
        """Get population group by name."""
        for p in self.populations:
            if p.name == name:
                return p
        raise KeyError(f"No population group found with name: {name}")
    
    def tag_for_name(self, name: str) -> PopulationTag:
        """Get population tag by name."""
        for p in self.populations:
            if p.name == name:
                return p.tag
        raise KeyError(f"No population tag found with name: {name}")
    
    def percent_weight(self, tag: PopulationTag) -> float:
        """Get percentage weight of a population group."""
        return self.party_for_tag(tag).weight / self.summed_weight
    
    @property
    def democrats(self) -> PopulationGroup:
        """Get Democratic population group."""
        return self.party_for_tag(DEMOCRATS)
    
    @property
    def republicans(self) -> PopulationGroup:
        """Get Republican population group."""
        return self.party_for_tag(REPUBLICANS)
    
    @property
    def independents(self) -> PopulationGroup:
        """Get Independent population group."""
        return self.party_for_tag(INDEPENDENTS)
    
    def ideology_for_percentile(self, percentile: float) -> float:
        """Get ideology value for a given percentile."""
        idx = max(0, min(self.n_samples - 1, int(percentile * self.n_samples + 0.5)))
        return self.sample_population[idx].ideology
    
    def approximate_median_ideology(self) -> float:
        """Calculate approximate median ideology."""
        return sum(p.weight * p.mean / self.summed_weight for p in self.populations)
    
    def random_voter(self, gaussian_generator: Optional[GaussianGenerator] = None) -> Voter:
        """Generate a random voter from the population."""
        if gaussian_generator is None:
            gaussian_generator = GaussianGenerator()
        return self._weighted_population().random_voter(gaussian_generator)
    
    def _weighted_population(self) -> PopulationGroup:
        """Select a population group based on weights."""
        r = random.random() * self.summed_weight
        for p in self.populations:
            if r <= p.weight:
                return p
            else:
                r -= p.weight
        # Should never get here, but return last population as fallback
        print("Warning: returning last population in weighted selection")
        return self.populations[-1]
    
    def _population_sample(self, n_samples: int) -> List[Voter]:
        """Generate a sample of voters from all population groups."""
        voters = []
        for p in self.populations:
            n_group_samples = int(p.weight * n_samples / self.summed_weight)
            voters.extend(p.population_sample(n_group_samples))
        return voters
