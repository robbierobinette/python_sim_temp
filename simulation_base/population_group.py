"""
Population group representing a segment of voters.
"""
from dataclasses import dataclass
from typing import List, TYPE_CHECKING
from .population_tag import PopulationTag
from .candidate import Candidate
from .gaussian_generator import GaussianGenerator

if TYPE_CHECKING:
    from .voter import Voter


@dataclass
class PopulationGroup:
    """Represents a group of voters with similar characteristics."""
    tag: PopulationTag
    party_bonus: float = 0.0
    mean: float = 0.0
    stddev: float = 15.0
    skew: float = 0.0
    weight: float = 100.0
    
    @property
    def plural_name(self) -> str:
        """Plural name of the population group."""
        return self.tag.plural_name
    
    @property
    def name(self) -> str:
        """Name of the population group."""
        return self.tag.name
    
    def stats(self) -> str:
        """String representation of group statistics."""
        return f"{self.tag.short_name}: {self.weight:5.2f} {self.mean:6.2f} {self.stddev:5.2f}"
    
    def shift_out(self, shift_amount: float) -> 'PopulationGroup':
        """Shift the group outward from center."""
        if self.tag.short_name == "Rep":
            return self.shift(shift_amount)
        elif self.tag.short_name == "Dem":
            return self.shift(-shift_amount)
        else:
            return PopulationGroup(
                tag=self.tag,
                party_bonus=self.party_bonus,
                mean=self.mean,
                stddev=self.stddev,
                skew=self.skew,
                weight=self.weight
            )
    
    def shift(self, shift_amount: float) -> 'PopulationGroup':
        """Shift the group mean by the given amount."""
        return PopulationGroup(
            tag=self.tag,
            party_bonus=self.party_bonus,
            mean=self.mean + shift_amount,
            stddev=self.stddev,
            skew=self.skew,
            weight=self.weight
        )
    
    def reweight(self, scale_factor: float) -> 'PopulationGroup':
        """Rescale the group weight."""
        return PopulationGroup(
            tag=self.tag,
            party_bonus=self.party_bonus,
            mean=self.mean,
            stddev=self.stddev,
            skew=self.skew,
            weight=self.weight * scale_factor
        )
    
    def party_bonus_for(self, other: PopulationTag) -> float:
        """Get party bonus for another party."""
        return self.tag.party_affinity(other)
    
    def party_bonus_for_group(self, other: 'PopulationGroup') -> float:
        """Get party bonus for another population group."""
        return self.tag.party_affinity(other.tag)
    
    def population_sample(self, n_samples: int, gaussian_generator: GaussianGenerator) -> List['Voter']:
        """Generate a sample of voters from this population group."""
        from .voter import Voter
        voters = []
        for _ in range(n_samples):
            # Generate Gaussian sample
            sample = gaussian_generator() * self.stddev + self.mean
            voters.append(Voter(party=self, ideology=sample))
        return voters
    
    def random_voter(self, gaussian_generator: GaussianGenerator) -> 'Voter':
        """Generate a random voter from this group."""
        from .voter import Voter
        ideology = gaussian_generator() * self.stddev + self.mean
        return Voter(party=self, ideology=ideology)
    
    def random_candidate(self, name: str, ideology_stddev: float, 
                        quality_stddev: float,
                        gaussian_generator: GaussianGenerator) -> Candidate:
        """Generate a random candidate from this group."""
        return Candidate(
            name=name,
            tag=self.tag,
            ideology=self.mean + gaussian_generator() * ideology_stddev,
            quality=gaussian_generator() * quality_stddev,
            incumbent=False
        )
