"""
Candidate generation for elections.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from .candidate import Candidate
from .combined_population import CombinedPopulation
from .population_group import PopulationGroup
from .population_tag import PopulationTag, DEMOCRATS, REPUBLICANS, INDEPENDENTS
from .gaussian_generator import GaussianGenerator


class CandidateGenerator(ABC):
    """Abstract base class for candidate generators."""
    
    def __init__(self, quality_variance: float):
        """Initialize candidate generator."""
        self.quality_variance = quality_variance
    
    @abstractmethod
    def candidates(self, population: CombinedPopulation) -> List[Candidate]:
        """Generate candidates for a population."""
        pass
    
    def candidates_for_ideologies(self, ideologies: List[float], party: PopulationGroup,
                                 gaussian_generator: Optional[GaussianGenerator] = None) -> List[Candidate]:
        """Generate candidates for specific ideologies."""
        if gaussian_generator is None:
            gaussian_generator = GaussianGenerator()
        
        # Sort ideologies from inside to outside
        if party.tag == DEMOCRATS:
            ideologies.sort(reverse=True)
        else:
            ideologies.sort()
        
        candidates = []
        for i, ideology in enumerate(ideologies):
            name = f"{party.tag.short_name[0]}-{i + 1}"
            candidate = Candidate(
                name=name,
                tag=party.tag,
                ideology=ideology,
                quality=gaussian_generator() * self.quality_variance,
                incumbent=False
            )
            candidates.append(candidate)
        
        return candidates
    
    def get_median_candidate(self, population: CombinedPopulation,
                           gaussian_generator: Optional[GaussianGenerator] = None) -> Candidate:
        """Generate a median voter candidate."""
        if gaussian_generator is None:
            gaussian_generator = GaussianGenerator()
        
        mv_tag = population.dominant_party(gaussian_generator)
        return Candidate(
            name=f"{mv_tag.initial}-V",
            tag=mv_tag,
            ideology=population.median_voter + gaussian_generator() * 0.05,
            quality=gaussian_generator() * self.quality_variance,
            incumbent=False,
        )


class PartisanCandidateGenerator(CandidateGenerator):
    """Generates partisan candidates."""
    
    def __init__(self, n_party_candidates: int, spread: float, ideology_variance: float,
                 quality_variance: float, primary_skew: float,
                 gaussian_generator: Optional[GaussianGenerator] = None):
        """Initialize partisan candidate generator."""
        super().__init__(quality_variance)
        self.n_party_candidates = n_party_candidates
        self.spread = spread
        self.ideology_variance = ideology_variance
        self.primary_skew = primary_skew
        self.gaussian_generator = gaussian_generator or GaussianGenerator()
    
    def get_partisan_candidates(self, population_group: PopulationGroup, 
                               population: CombinedPopulation, n_candidates: int) -> List[Candidate]:
        """Generate partisan candidates for a population group."""
        skew = self.primary_skew if population_group.tag == REPUBLICANS else -self.primary_skew
        party_base = population_group.mean + skew
        offset = self.spread * population_group.stddev * (1 if population_group.tag == REPUBLICANS else -1)
        
        # Generate ideologies based on number of candidates
        if n_candidates == 1:
            ideologies = [party_base]
        elif n_candidates == 2:
            ideologies = [party_base - offset, party_base + offset]
        else:  # 3 or more candidates
            ideologies = [party_base - offset, party_base, party_base + offset]
            # Add more candidates if needed
            if n_candidates > 3:
                step = (2 * offset) / (n_candidates - 1)
                ideologies = [party_base - offset + i * step for i in range(n_candidates)]
        
        candidates = []
        for idx, ideology in enumerate(ideologies):
            candidate = Candidate(
                name=f"{population_group.tag.initial}-{idx + 1}",
                tag=population_group.tag,
                ideology=ideology + self.gaussian_generator() * self.ideology_variance,
                quality=self.gaussian_generator() * self.quality_variance,
                incumbent=False,
            )
            candidates.append(candidate)
        
        return candidates
    
    def candidates(self, population: CombinedPopulation) -> List[Candidate]:
        """Generate all candidates for the population."""
        reps = self.get_partisan_candidates(population.republicans, population, self.n_party_candidates)
        dems = self.get_partisan_candidates(population.democrats, population, self.n_party_candidates)
        median = self.get_median_candidate(population, self.gaussian_generator)
        
        return dems + [median] + reps


class NormalPartisanCandidateGenerator(CandidateGenerator):
    """Generates partisan candidates from normal distributions with a median candidate."""
    
    def __init__(self, n_partisan_candidates: int, ideology_variance: float, quality_variance: float,
                 gaussian_generator: Optional[GaussianGenerator] = None):
        """Initialize normal partisan candidate generator."""
        super().__init__(quality_variance)
        self.n_partisan_candidates = n_partisan_candidates
        self.ideology_variance = ideology_variance
        self.gaussian_generator = gaussian_generator or GaussianGenerator()
    
    def candidates(self, population: CombinedPopulation) -> List[Candidate]:
        """Generate all candidates for the population."""
        candidates = []
        
        # Generate Democratic candidates from normal distribution
        for i in range(self.n_partisan_candidates):
            # Draw from normal distribution centered at Democratic mean
            ideology = population.democrats.mean + self.gaussian_generator() * self.ideology_variance
            candidate = Candidate(
                name=f"D-{i + 1}",
                tag=DEMOCRATS,
                ideology=ideology,
                quality=self.gaussian_generator() * self.quality_variance,
                incumbent=False,
            )
            candidates.append(candidate)
        
        # Add median candidate
        median_candidate = self.get_median_candidate(population, self.gaussian_generator)
        candidates.append(median_candidate)
        
        # Generate Republican candidates from normal distribution
        for i in range(self.n_partisan_candidates):
            # Draw from normal distribution centered at Republican mean
            ideology = population.republicans.mean + self.gaussian_generator() * self.ideology_variance
            candidate = Candidate(
                name=f"R-{i + 1}",
                tag=REPUBLICANS,
                ideology=ideology,
                quality=self.gaussian_generator() * self.quality_variance,
                incumbent=False,
            )
            candidates.append(candidate)
        
        return candidates


class RankCandidateGenerator(CandidateGenerator):
    """Generates candidates based on rank distribution."""
    
    def __init__(self, n_party_candidates: int, spread: float, offset: float,
                 ideology_variance: float, quality_variance: float,
                 gaussian_generator: Optional[GaussianGenerator] = None):
        """Initialize rank candidate generator."""
        super().__init__(quality_variance)
        self.n_party_candidates = n_party_candidates
        self.spread = spread
        self.offset = offset
        self.ideology_variance = ideology_variance
        self.gaussian_generator = gaussian_generator or GaussianGenerator()
    
    def compute_ranks(self, tag: PopulationTag, offset: float, spread: float, 
                     noise: float, n_candidates: int) -> List[float]:
        """Compute rank positions for candidates."""
        if n_candidates <= 1:
            raise ValueError("Number of candidates must be greater than 1")
        
        step = spread / (n_candidates - 1)
        ranks = [i * step - spread / 2 for i in range(n_candidates)]
        
        # Add noise
        ranks = [r + noise * self.gaussian_generator() for r in ranks]
        
        # Adjust for party
        if tag == REPUBLICANS:
            ranks = [r + offset + 0.5 for r in ranks]
        elif tag == DEMOCRATS:
            ranks = [0.5 - offset - r for r in ranks]
        
        # Filter valid ranks
        ranks = [r for r in ranks if 0 < r < 1]
        return ranks
    
    def get_candidates_rank(self, party: PopulationGroup, population: CombinedPopulation,
                           n_candidates: int) -> List[Candidate]:
        """Generate candidates using rank distribution."""
        ranks = self.compute_ranks(party.tag, self.offset, self.spread, 
                                  self.ideology_variance, n_candidates)
        ideologies = [population.ideology_for_percentile(r) for r in ranks]
        ideologies.sort()
        return self.candidates_for_ideologies(ideologies, party, self.gaussian_generator)
    
    def candidates(self, population: CombinedPopulation) -> List[Candidate]:
        """Generate all candidates for the population."""
        reps = self.get_candidates_rank(population.republicans, population, self.n_party_candidates)
        dems = self.get_candidates_rank(population.democrats, population, self.n_party_candidates)
        median = self.get_median_candidate(population, self.gaussian_generator)
        
        return dems + [median] + reps


class RandomCandidateGenerator(CandidateGenerator):
    """Generates random candidates."""
    
    def __init__(self, n_candidates: int, quality_variance: float, n_median_candidates: int = 0,
                 gaussian_generator: Optional[GaussianGenerator] = None):
        """Initialize random candidate generator."""
        super().__init__(quality_variance)
        self.n_candidates = n_candidates
        self.n_median_candidates = n_median_candidates
        self.gaussian_generator = gaussian_generator or GaussianGenerator()
    
    def candidates(self, population: CombinedPopulation) -> List[Candidate]:
        """Generate random candidates."""
        candidates = []
        
        # Generate random candidates
        for i in range(self.n_candidates):
            voter = population.random_voter(self.gaussian_generator)
            candidate = Candidate(
                name=f"C-{i}",
                tag=voter.party.tag,
                ideology=voter.ideology,
                quality=self.gaussian_generator() * self.quality_variance,
                incumbent=False
            )
            candidates.append(candidate)
        
        # Add median candidates
        for _ in range(self.n_median_candidates):
            median_candidate = self.get_median_candidate(population, self.gaussian_generator)
            candidates.append(median_candidate)
        
        return candidates


class CondorcetCandidateGenerator(CandidateGenerator):
    """Generates Condorcet candidates distributed around the median voter."""
    
    def __init__(self, n_candidates: int, ideology_variance: float, quality_variance: float,
                 gaussian_generator: Optional[GaussianGenerator] = None):
        """Initialize Condorcet candidate generator."""
        super().__init__(quality_variance)
        self.n_candidates = n_candidates
        self.ideology_variance = ideology_variance
        self.gaussian_generator = gaussian_generator or GaussianGenerator()
        self.party_switch_point = 0.1
    

    def candidates(self, population: CombinedPopulation) -> List[Candidate]:
        """Generate Condorcet candidates distributed around the median voter."""
        candidates = []
        median_voter_ideology = population.median_voter
        
        # Generate candidates distributed around the median voter
        for i in range(self.n_candidates):
            # Create ideology centered around median voter with specified variance
            ideology = median_voter_ideology + self.gaussian_generator() * self.ideology_variance
            
            # Determine party affiliation based on ideology
            if ideology < -self.party_switch_point:  # More liberal
                party_tag = DEMOCRATS
                party_initial = "D"
            elif ideology > self.party_switch_point:  # More conservative
                party_tag = REPUBLICANS
                party_initial = "R"
            else:  # Centrist
                party_tag = INDEPENDENTS
                party_initial = "I"
            
            candidate = Candidate(
                name=f"{party_initial}-{i + 1}",
                tag=party_tag,
                ideology=ideology,
                quality=self.gaussian_generator() * self.quality_variance,
                incumbent=False,
            )
            candidates.append(candidate)
        
        # Sort candidates by ideology
        candidates.sort(key=lambda c: c.ideology)
        # Rename candidates to be their party-letter and then their order from most liberal to most conservative (1-based)
        for idx, candidate in enumerate(candidates):
            candidate.name = f"{candidate.tag.short_name[0]}-{idx + 1}"

        return candidates
