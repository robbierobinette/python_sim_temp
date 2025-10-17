"""
Simple plurality voting implementation for primaries.
"""
from typing import List, Dict

from simulation_base.population_tag import INDEPENDENTS, DEMOCRATS, REPUBLICANS
from .election_result import ElectionResult, CandidateResult
from .ballot import RCVBallot
from .candidate import Candidate
from .population_tag import PopulationTag
from .election_process import ElectionProcess


class SimplePluralityResult(ElectionResult):
    """Result of a simple plurality election."""
    
    def __init__(self, results: Dict[Candidate, float], breakdown: Dict[Candidate, Dict[str, float]], voter_satisfaction: float = 0.0):
        """Initialize simple plurality result."""
        self._results = results
        self._breakdown = breakdown
        self._voter_satisfaction = voter_satisfaction
        self._candidate_map = {c.name: c for c in results.keys()}
    
    def winner(self) -> Candidate:
        """Return the winning candidate."""
        return self.ordered_results()[0].candidate
    
    def voter_satisfaction(self) -> float:
        """Return the voter satisfaction score."""
        return self._voter_satisfaction

    def print_details(self):
        """Print details of the simple plurality result."""
        print("Simple plurality result:")
        for cr in self.ordered_results():
            c = cr.candidate
            print(f"  {c.name:12s} {c.ideology:5.2f} {c.quality:5.2f} {cr.votes:8.0f} {c.affinity_string()}", end=" ")
            print("\tBreakdown:", end=" ")
            for t in [DEMOCRATS.short_name, REPUBLICANS.short_name, INDEPENDENTS.short_name]:
                print(f" {t:5s}: {self._breakdown[c.name][t]:5.2f}", end=" ")
            print()

    def ordered_results(self) -> List[CandidateResult]:
        """Return results ordered by vote count (descending)."""
        return sorted([CandidateResult(candidate=c, votes=v) 
                      for c, v in self._results.items()],
                     key=lambda x: x.votes, reverse=True)
    
    @property
    def n_votes(self) -> float:
        """Total votes in the election."""
        return sum(self._results.values())


class SimplePlurality(ElectionProcess):
    """Simple plurality voting election process."""
    
    def __init__(self, debug: bool = False):
        """Initialize simple plurality election."""
        self.debug = debug
    
    @property
    def name(self) -> str:
        """Name of the election process."""
        return "simplePlurality"
    
    def run(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> SimplePluralityResult:
        """Run simple plurality election with the given candidates and ballots."""
        # Count first-choice votes


        # use string based dicts because hashing objects is slow 
        raw_results = {}
        breakdown = {}
        for c in candidates:
            raw_results[c.name] = 0.0
            breakdown[c.name] = {DEMOCRATS.short_name: 0.0, REPUBLICANS.short_name: 0.0, INDEPENDENTS.short_name: 0.0}


        for ballot in ballots:
            # Get first choice candidate
            first_choice = ballot.candidate(candidates).name
            breakdown[first_choice][ballot.voter.party.tag.short_name] += 1.0
            raw_results[first_choice] += 1.0
        
        results = {}
        cmap = {c.name: c for c in candidates}
        for name, count in raw_results.items():
            results[cmap[name]] = count


        return SimplePluralityResult(results, breakdown)
    
