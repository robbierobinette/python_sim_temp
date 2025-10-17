"""
Candidate generation for elections.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import json
import os
from .candidate import Candidate
from .combined_population import CombinedPopulation
from .population_group import PopulationGroup
from .population_tag import PopulationTag, DEMOCRATS, REPUBLICANS, INDEPENDENTS
from .gaussian_generator import GaussianGenerator
from .district_voting_record import DistrictVotingRecord


class CandidateGenerator(ABC):
    """Abstract base class for candidate generators."""
    
    # Class-level attribute to hold election types map
    _election_types_by_state: Dict[str, Dict[str, Any]] = {}
    
    def _load_election_types(self) -> None:
        """Load election types from JSON file if not already loaded."""
        if not self._election_types_by_state:
            # Get the path to election_types.json relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(os.path.dirname(current_dir), 'election_types.json')
            
            with open(json_path, 'r') as f:
                election_data = json.load(f)
            
            # Create a map by state abbreviation
            for _, state_info in election_data.items():
                abbr = state_info.get('abbr')
                if abbr:
                    self._election_types_by_state[abbr] = state_info
    
    def __init__(self, quality_variance: float):
        """Initialize candidate generator."""
        self.quality_variance = quality_variance
        # Ensure election types are loaded
        self._load_election_types()
    
    def get_primary_offset(self, state_abbr: str, party_tag: PopulationTag) -> float:
        """
        Get the primary offset for a given state and party.
        
        Returns -0.2 for Republicans and 0.2 for Democrats if the state has:
        - A top-2 primary, OR
        - An open primary with no runoff
        
        Otherwise returns 0.0.
        
        Args:
            state_abbr: Two-letter state abbreviation (e.g., "CA", "WA")
            party_tag: The party tag (DEMOCRATS or REPUBLICANS)
        
        Returns:
            The offset value for the primary
        """
        self._load_election_types()
        
        # Get election info for the state
        state_info = self._election_types_by_state.get(state_abbr)
        if not state_info:
            return 0.0
        
        primary_type = state_info.get('primary', '')
        has_runoff = state_info.get('primary_runoff', False)
        
        # Check if condition applies: top-2 OR (open AND no runoff)
        is_top2 = primary_type == 'top-2'
        is_open_no_runoff = 'open' in primary_type and not has_runoff
        
        if is_top2 or is_open_no_runoff:
            if party_tag == REPUBLICANS:
                return -0.2
            elif party_tag == DEMOCRATS:
                return 0.2
        
        return 0.0
    
    @abstractmethod
    def candidates(self, population: CombinedPopulation) -> List[Candidate]:
        """Generate candidates for a population."""
        pass
    
    def candidates_for_ideologies(self, ideologies: List[float], party: PopulationGroup,
                                 gaussian_generator: GaussianGenerator) -> List[Candidate]:
        """Generate candidates for specific ideologies."""
        
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
                             median_variance: float,
                           gaussian_generator: GaussianGenerator) -> Candidate:
        """Generate a median voter candidate."""
        
        mv_tag = population.dominant_party()
        return Candidate(
            name=f"{mv_tag.initial}-V",
            tag=mv_tag,
            ideology=population.median_voter + gaussian_generator() * median_variance,
            quality=gaussian_generator() * self.quality_variance,
            incumbent=False,
        )


class PartisanCandidateGenerator(CandidateGenerator):
    """Generates partisan candidates."""
    
    def __init__(self, 
                    n_party_candidates: int, 
                    spread: float, 
                    ideology_variance: float, 
                    median_variance: float,
                    quality_variance: float, 
                    primary_skew: float,
                    gaussian_generator: GaussianGenerator):
        """Initialize partisan candidate generator."""
        super().__init__(quality_variance)
        self.n_party_candidates = n_party_candidates
        self.spread = spread
        self.ideology_variance = ideology_variance
        self.primary_skew = primary_skew
        self.median_variance = median_variance
        self.gaussian_generator = gaussian_generator
    
    def get_partisan_candidates(self, population_group: PopulationGroup, dvr: DistrictVotingRecord, n_candidates: int) -> List[Candidate]:
        """Generate partisan candidates for a population group."""
        skew = self.primary_skew if population_group.tag == REPUBLICANS else -self.primary_skew
        party_base = population_group.mean + skew + self.get_primary_offset(dvr.state, population_group.tag)
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
        reps = self.get_partisan_candidates(population.republicans, population.district, self.n_party_candidates)
        dems = self.get_partisan_candidates(population.democrats, population.district, self.n_party_candidates)
        median = self.get_median_candidate(population, self.median_variance, self.gaussian_generator)

        if median.tag == DEMOCRATS:
            dems = dems[1:]
        elif median.tag == REPUBLICANS:
            reps = reps[1:]
        else:
            raise ValueError(f"Median candidate has invalid tag: {median.tag}")
        
        return dems + [median] + reps


class NormalPartisanCandidateGenerator(CandidateGenerator):
    """Generates partisan candidates from normal distributions with a median candidate."""
    
    def __init__(self, n_partisan_candidates: int, 
                ideology_variance: float, 
                quality_variance: float,
                primary_skew: float,
                median_variance: float,
                gaussian_generator: GaussianGenerator,
):
        """Initialize normal partisan candidate generator."""
        super().__init__(quality_variance)
        self.n_partisan_candidates = n_partisan_candidates
        self.ideology_variance = ideology_variance
        self.primary_skew = primary_skew
        self.median_variance = median_variance
        self.gaussian_generator = gaussian_generator
    
    def candidates(self, population: CombinedPopulation) -> List[Candidate]:
        """Generate all candidates for the population."""
        candidates = []


        median_candidate = self.get_median_candidate(population, self.median_variance, self.gaussian_generator)
        n_dems = self.n_partisan_candidates
        n_reps = self.n_partisan_candidates
        # if median_candidate.tag == DEMOCRATS:
        #     n_dems -= 1
        # elif median_candidate.tag == REPUBLICANS:
        #     n_reps -= 1
        # else:
        #     raise ValueError(f"Median candidate has invalid tag: {median_candidate.tag}")
            
        
        # Generate Democratic candidates from normal distribution
        for i in range(n_dems):
            # Draw from normal distribution centered at Democratic mean
            ideology = population.democrats.mean - self.primary_skew + self.gaussian_generator() * self.ideology_variance 
            ideology += self.get_primary_offset(population.district.state, DEMOCRATS)
            candidate = Candidate(
                name=f"D-{i + 1}",
                tag=DEMOCRATS,
                ideology=ideology,
                quality=self.gaussian_generator() * self.quality_variance,
                incumbent=False,
            )
            candidates.append(candidate)
        
        # Add median candidate
        candidates.append(median_candidate)
        
        # Generate Republican candidates from normal distribution
        for i in range(n_reps):
            # Draw from normal distribution centered at Republican mean
            ideology = population.republicans.mean + self.primary_skew + self.gaussian_generator() * self.ideology_variance
            ideology += self.get_primary_offset(population.district.state, REPUBLICANS)
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
                 ideology_variance: float, quality_variance: float, median_variance: float,
                 gaussian_generator: GaussianGenerator):
        """Initialize rank candidate generator."""
        super().__init__(quality_variance)
        self.n_party_candidates = n_party_candidates
        self.spread = spread
        self.offset = offset
        self.ideology_variance = ideology_variance
        self.median_variance = median_variance
        self.gaussian_generator = gaussian_generator
    
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
        median = self.get_median_candidate(population, self.median_variance, self.gaussian_generator)
        
        return dems + [median] + reps


class RandomCandidateGenerator(CandidateGenerator):
    """Generates random candidates."""
    
    def __init__(self, n_candidates: int, quality_variance: float, median_variance: float, n_median_candidates: int,
                 gaussian_generator: GaussianGenerator):
        """Initialize random candidate generator."""
        super().__init__(quality_variance)
        self.n_candidates = n_candidates
        self.n_median_candidates = n_median_candidates
        self.median_variance = median_variance
        self.gaussian_generator = gaussian_generator
    
    def candidates(self, population: CombinedPopulation) -> List[Candidate]:
        """Generate random candidates."""
        candidates = []
        
        # Generate random candidates
        for i in range(self.n_candidates):
            voter = population.random_voter()
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
            median_candidate = self.get_median_candidate(population, self.median_variance, self.gaussian_generator)
            candidates.append(median_candidate)
        
        return candidates

class CondorcetCandidateGenerator(CandidateGenerator):
    """Generates Condorcet candidates distributed around the median voter."""
    
    def __init__(self, n_candidates: int, ideology_variance: float, quality_variance: float,
                 gaussian_generator: GaussianGenerator):
        """Initialize Condorcet candidate generator."""
        super().__init__(quality_variance)
        self.n_candidates = n_candidates
        self.ideology_variance = ideology_variance
        self.gaussian_generator = gaussian_generator
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
            if ideology < -self.party_switch_point:  # More very liberal
                party_tag = DEMOCRATS
                party_initial = "D"
            elif ideology > self.party_switch_point:  # More very conservative
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
        # Rename candidates to be their party-letter and then their order from very liberal to very conservative (1-based)
        for idx, candidate in enumerate(candidates):
            candidate.name = f"{candidate.tag.short_name[0]}-{idx + 1}"

        return candidates
