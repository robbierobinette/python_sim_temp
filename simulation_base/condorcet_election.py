"""
Condorcet election implementation using pairwise SimplePlurality elections.
"""
from typing import List, Dict
from dataclasses import dataclass
from .candidate import Candidate
from .ballot import RCVBallot
from .election_result import ElectionResult, CandidateResult
from .election_process import ElectionProcess
from .simple_plurality import SimplePlurality, SimplePluralityResult


@dataclass
class PairwiseComparison:
    """Represents a pairwise comparison between two candidates.
    
    winner is always the winner of this pairwise comparison.
    Stores a SimplePluralityResult and accesses data via properties.
    """
    result: SimplePluralityResult
    
    @property
    def winner(self) -> Candidate:
        return self.result.ordered_results()[0].candidate
    
    @property
    def loser(self) -> Candidate:
        return self.result.ordered_results()[1].candidate
    
    @property
    def winner_votes(self) -> float:
        return self.result.ordered_results()[0].votes
    
    @property
    def loser_votes(self) -> float:
        return self.result.ordered_results()[1].votes
    
    @property
    def margin(self) -> float:
        return self.winner_votes - self.loser_votes
    
    def print_details(self) -> None:
        print(f"  {self.winner.name} defeats {self.loser.name}: "
              f"{self.winner_votes:.0f} - {self.loser_votes:.0f} (margin: {self.margin:.0f})")
        self.result.print_details()


@dataclass
class CondorcetStats:
    """Statistics for a candidate in Condorcet election."""
    candidate: Candidate
    wins: int
    smallest_loss_margin: float
    
    def __lt__(self, other: 'CondorcetStats') -> bool:
        """Compare candidates: most wins first, then smallest loss as tiebreaker."""
        if self.wins != other.wins:
            return self.wins > other.wins  # More wins is better
        elif self.smallest_loss_margin != other.smallest_loss_margin:
            return self.smallest_loss_margin < other.smallest_loss_margin  # Smaller loss is better
        else:
            return self.candidate.name < other.candidate.name  # Alphabetical as final tiebreaker


class CondorcetResult(ElectionResult):
    """Result of a Condorcet election."""
    
    def __init__(self, comparisons: List[PairwiseComparison], candidates: List[Candidate],
                 voter_satisfaction: float = 0.0):
        """Initialize Condorcet result."""
        self.comparisons = comparisons
        self.candidates = candidates
        self._winner = self._determine_winner()
        self._voter_satisfaction = voter_satisfaction
    
    def _determine_winner(self) -> Candidate:
        """Determine the winner based on pairwise wins and smallest loss."""
        stats = self._compute_stats()
        sorted_stats = sorted(stats.values())
        self._stats = sorted_stats
        return sorted_stats[0].candidate
    
    def _compute_stats(self) -> Dict[str, CondorcetStats]:
        """Compute statistics for all candidates."""
        stats_dict: Dict[str, CondorcetStats] = {}
        
        # Initialize stats for each candidate
        for candidate in self.candidates:
            stats_dict[candidate.name] = CondorcetStats(
                candidate=candidate,
                wins=0,
                smallest_loss_margin=float('inf')
            )
        
        # Process each comparison (winner always wins)
        for comparison in self.comparisons:
            # A wins
            stats_dict[comparison.winner.name].wins += 1
            # B loses - track the margin
            stats_dict[comparison.loser.name].smallest_loss_margin = min(
                stats_dict[comparison.loser.name].smallest_loss_margin,
                comparison.margin
            )
        
        return stats_dict
    
    def winner(self) -> Candidate:
        """Get the winner."""
        return self._winner
    
    def voter_satisfaction(self) -> float:
        """Return the voter satisfaction score."""
        return self._voter_satisfaction
    
    # this is wrong.  it should rerun the entire algorithm recursively on 
    # the pairwise comparisons w/o the prior winners.  But we don't use 
    # anything beyond the first winner anyway.

    def ordered_results(self) -> List[CandidateResult]:
        """Get ordered results based on Condorcet wins."""
        stats = self._compute_stats()
        sorted_stats = sorted(stats.values())
        return [CandidateResult(candidate=stats.candidate, votes=float(stats.wins))
                for stats in sorted_stats][0:1]
    
    @property
    def n_votes(self) -> float:
        """Total votes (not applicable for Condorcet)."""
        return 0.0
    
    def print_details(self) -> None:
        """Print all pairwise comparisons for this election."""
        print("\n  Pairwise Comparisons:")
        for comparison in self.comparisons:
            comparison.print_details()

class CondorcetElection(ElectionProcess):
    """Condorcet election process using pairwise SimplePlurality elections."""
    
    def __init__(self, debug: bool):
        """Initialize Condorcet election."""
        self.debug = debug
    
    @property
    def name(self) -> str:
        """Name of the election process."""
        return "condorcet"
    
    def run(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> CondorcetResult:
        """Run Condorcet election with the given candidates and ballots."""
        # Compute all pairwise comparisons using SimplePlurality
        comparisons = []
        
        for i, candidate_i in enumerate(candidates):
            for j, candidate_j in enumerate(candidates):
                if j > i:
                    # Run a SimplePlurality election between these two candidates
                    plurality = SimplePlurality(debug=self.debug)
                    result = plurality.run([candidate_i, candidate_j], ballots)
                    comparison = PairwiseComparison(result=result)
                    comparisons.append(comparison)
        
        # Calculate voter satisfaction
        condorcet_result = CondorcetResult(comparisons, candidates, 0.0)
        winner = condorcet_result.winner()
        left_voter_count = sum(1 for ballot in ballots if ballot.voter.ideology < winner.ideology)
        voter_satisfaction = 1 - abs((2.0 * left_voter_count / len(ballots)) - 1)
        condorcet_result._voter_satisfaction = voter_satisfaction
        
        return condorcet_result

