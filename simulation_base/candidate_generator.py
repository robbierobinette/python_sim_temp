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
    
    def get_primary_offset(self, state_abbr: str, party_tag: PopulationTag, election_type: str) -> float:
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

        if election_type == "custom":
            self._load_election_types()
            state_info = self._election_types_by_state.get(state_abbr)
            primary_type = state_info['primary']
            has_runoff = state_info['primary_runoff']
        elif election_type == "top-2":
            primary_type = "top-2"
            has_runoff = False
        else:
            return 0.0

        
        if primary_type == "top-2" or (primary_type == "open" and not has_runoff):
            if party_tag == REPUBLICANS:
                return -0.2
            elif party_tag == DEMOCRATS:
                return 0.2
        
        return 0.0
    
    @abstractmethod
    def candidates(self, population: CombinedPopulation, election_type: str) -> List[Candidate]:
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



class NormalPartisanCandidateGenerator(CandidateGenerator):
    """Generates partisan candidates from normal distributions with a median candidate."""
    
    def __init__(self, n_partisan_candidates: int, 
                ideology_variance: float, 
                quality_variance: float,
                primary_skew: float,
                median_variance: float,
                gaussian_generator: GaussianGenerator,
                n_condorcet: int):
        """Initialize normal partisan candidate generator."""
        super().__init__(quality_variance)
        self.n_partisan_candidates = n_partisan_candidates
        self.ideology_variance = ideology_variance
        self.primary_skew = primary_skew
        self.median_variance = median_variance
        self.gaussian_generator = gaussian_generator
        self.n_condorcet = n_condorcet
    
    def candidates(self, population: CombinedPopulation, election_type: str) -> List[Candidate]:
        """Generate all candidates for the population."""
        candidates = []

        # Generate Democratic candidates from normal distribution
        for i in range(self.n_partisan_candidates):
            # Draw from normal distribution centered at Democratic mean
            ideology = population.democrats.mean - self.primary_skew + self.gaussian_generator() * self.ideology_variance 
            ideology += self.get_primary_offset(population.district.state, DEMOCRATS, election_type)
            candidate = Candidate(
                name=f"D-{i + 1}",
                tag=DEMOCRATS,
                ideology=ideology,
                quality=self.gaussian_generator() * self.quality_variance,
                incumbent=False,
            )
            candidates.append(candidate)
        
        # Generate median/condorcet candidates
        for i in range(self.n_condorcet):
            median_candidate = self.get_median_candidate(population, self.median_variance, self.gaussian_generator)
            median_candidate.name = f"C-{i + 1}"  # Rename to distinguish multiple condorcet candidates
            candidates.append(median_candidate)
        
        # Generate Republican candidates from normal distribution
        for i in range(self.n_partisan_candidates):
            # Draw from normal distribution centered at Republican mean
            ideology = population.republicans.mean + self.primary_skew + self.gaussian_generator() * self.ideology_variance
            ideology += self.get_primary_offset(population.district.state, REPUBLICANS, election_type)
            candidate = Candidate(
                name=f"R-{i + 1}",
                tag=REPUBLICANS,
                ideology=ideology,
                quality=self.gaussian_generator() * self.quality_variance,
                incumbent=False,
            )
            candidates.append(candidate)
        
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
    

    def candidates(self, population: CombinedPopulation, _election_type: str) -> List[Candidate]:
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
            elif ideology > self.party_switch_point:  # More very conservative
                party_tag = REPUBLICANS
            else:  # Centrist
                party_tag = INDEPENDENTS
            
            candidate = Candidate(
                name="XX",
                tag=party_tag,
                ideology=ideology,
                quality=self.gaussian_generator() * self.quality_variance,
                incumbent=False,
            )
            candidates.append(candidate)
        
        # Sort candidates by ideology
        candidates.sort(key=lambda c: abs(c.ideology))
        # Rename candidates to be their party-letter and then their order from the center out to extreme
        for idx, candidate in enumerate(candidates):
            candidate.name = f"{candidate.tag.short_name[0]}-{idx + 1}"

        return candidates
