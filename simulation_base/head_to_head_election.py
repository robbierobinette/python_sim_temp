"""
Head-to-head election implementation.
"""
from typing import List, Dict
from dataclasses import dataclass
from .candidate import Candidate
from .ballot import RCVBallot
from .election_result import ElectionResult, CandidateResult
from .election_process import ElectionProcess


@dataclass
class PairwiseOutcome:
    """Represents the outcome of a head-to-head matchup between two candidates."""
    candidate_a: Candidate
    candidate_b: Candidate
    votes_for_a: float
    votes_for_b: float
    winner: Candidate  # Store the actual winner (determined randomly for ties)
    
    @property
    def margin(self) -> float:
        """Return the margin of victory."""
        return abs(self.votes_for_a - self.votes_for_b)
    
    def __str__(self) -> str:
        return f"{self.candidate_a.name} vs {self.candidate_b.name}: {self.votes_for_a:.1f} - {self.votes_for_b:.1f}"


class HeadToHeadAccumulator:
    """Accumulates head-to-head results from ballots."""
    
    def __init__(self, candidates: List[Candidate], ballots: List[RCVBallot], gaussian_generator=None):
        """Initialize accumulator and compute all head-to-head matchups."""
        self.candidates = candidates
        self.pairwise_outcomes: List[PairwiseOutcome] = []
        self.gaussian_generator = gaussian_generator
        
        # Compute all head-to-head matchups
        # Only compute A vs B (not B vs A) for each unique pair
        n_candidates = len(candidates)
        for i in range(n_candidates):
            for j in range(i + 1, n_candidates):
                candidate_a = candidates[i]
                candidate_b = candidates[j]
                
                # Go through ballots once for this pair
                votes_for_a = 0.0
                votes_for_b = 0.0
                
                for ballot in ballots:
                    # Find positions of candidates A and B on this ballot
                    pos_a = len(ballot.sorted_candidates)
                    pos_b = pos_a
                    
                    for idx, candidate_score in enumerate(ballot.sorted_candidates):
                        if candidate_score.candidate.name == candidate_a.name:
                            pos_a = idx
                        elif candidate_score.candidate.name == candidate_b.name:
                            pos_b = idx
                    
                    # Determine winner of this matchup on this ballot
                    if pos_a < pos_b:
                        votes_for_a += 1.0
                    elif pos_a > pos_b:
                        votes_for_b += 1.0
                
                # Determine winner (randomly for ties)
                if votes_for_a > votes_for_b:
                    winner = candidate_a
                elif votes_for_b > votes_for_a:
                    winner = candidate_b
                else:
                    # Tie - randomly choose winner
                    if self.gaussian_generator:
                        winner = candidate_a if self.gaussian_generator.next_boolean() else candidate_b
                    else:
                        # Fallback to alphabetical order if no generator provided
                        winner = candidate_a if candidate_a.name < candidate_b.name else candidate_b
                
                # Store outcome
                outcome = PairwiseOutcome(candidate_a, candidate_b, votes_for_a, votes_for_b, winner)
                self.pairwise_outcomes.append(outcome)


@dataclass
class CandidateStats:
    """Statistics for a candidate in head-to-head matchups."""
    candidate: Candidate
    wins: int
    losses: int
    ties: int
    smallest_loss_margin: float
    
    def __lt__(self, other: 'CandidateStats') -> bool:
        """Compare candidates: most wins first, then smallest loss as tiebreaker."""
        if self.wins != other.wins:
            return self.wins > other.wins  # More wins is better
        elif self.smallest_loss_margin != other.smallest_loss_margin:
            return self.smallest_loss_margin < other.smallest_loss_margin  # Smaller loss is better
        else:
            return self.candidate.name < other.candidate.name  # Alphabetical as final tiebreaker


def determine_winner_from_pairwise_outcomes(pairwise_outcomes: List[PairwiseOutcome],
                                            candidates: List[Candidate]) -> Candidate:
    """Determine the winner based on head-to-head wins, with smallest loss as tiebreaker."""
    # Count wins, losses, and track smallest loss for each candidate
    stats_dict: Dict[str, CandidateStats] = {}
    
    for candidate in candidates:
        stats_dict[candidate.name] = CandidateStats(
            candidate=candidate,
            wins=0,
            losses=0,
            ties=0,
            smallest_loss_margin=float('inf')
        )
    
    # Process each pairwise outcome
    for outcome in pairwise_outcomes:
        if outcome.winner == outcome.candidate_a:
            # A wins (including random tiebreaker)
            stats_dict[outcome.candidate_a.name].wins += 1
            stats_dict[outcome.candidate_b.name].losses += 1
            loss_margin = outcome.votes_for_a - outcome.votes_for_b
            stats_dict[outcome.candidate_b.name].smallest_loss_margin = min(
                stats_dict[outcome.candidate_b.name].smallest_loss_margin,
                loss_margin
            )
        elif outcome.winner == outcome.candidate_b:
            # B wins (including random tiebreaker)
            stats_dict[outcome.candidate_b.name].wins += 1
            stats_dict[outcome.candidate_a.name].losses += 1
            loss_margin = outcome.votes_for_b - outcome.votes_for_a
            stats_dict[outcome.candidate_a.name].smallest_loss_margin = min(
                stats_dict[outcome.candidate_a.name].smallest_loss_margin,
                loss_margin
            )
        else:
            # This shouldn't happen with the new design, but keeping for safety
            stats_dict[outcome.candidate_a.name].ties += 1
            stats_dict[outcome.candidate_b.name].ties += 1
    
    # Sort candidates by stats (most wins, then smallest loss)
    sorted_stats = sorted(stats_dict.values())
    
    return sorted_stats[0].candidate


class HeadToHeadResult(ElectionResult):
    """Result of a head-to-head election."""
    
    def __init__(self, pairwise_outcomes: List[PairwiseOutcome], candidates: List[Candidate],
                 voter_satisfaction: float = 0.0):
        """Initialize head-to-head result."""
        self.pairwise_outcomes = pairwise_outcomes
        self.candidates = candidates
        self._winner = determine_winner_from_pairwise_outcomes(pairwise_outcomes, candidates)
        self._voter_satisfaction = voter_satisfaction
    
    def winner(self) -> Candidate:
        """Get the winner."""
        return self._winner
    
    def voter_satisfaction(self) -> float:
        """Return the voter satisfaction score."""
        return self._voter_satisfaction
    
    def ordered_results(self) -> List[CandidateResult]:
        """Get ordered results based on head-to-head wins."""
        # Calculate stats for all candidates
        stats_dict: Dict[str, CandidateStats] = {}
        
        for candidate in self.candidates:
            stats_dict[candidate.name] = CandidateStats(
                candidate=candidate,
                wins=0,
                losses=0,
                ties=0,
                smallest_loss_margin=float('inf')
            )
        
        # Process outcomes
        for outcome in self.pairwise_outcomes:
            if outcome.winner == outcome.candidate_a:
                # A wins (including random tiebreaker)
                stats_dict[outcome.candidate_a.name].wins += 1
                stats_dict[outcome.candidate_b.name].losses += 1
                loss_margin = outcome.votes_for_a - outcome.votes_for_b
                stats_dict[outcome.candidate_b.name].smallest_loss_margin = min(
                    stats_dict[outcome.candidate_b.name].smallest_loss_margin, loss_margin
                )
            elif outcome.winner == outcome.candidate_b:
                # B wins (including random tiebreaker)
                stats_dict[outcome.candidate_b.name].wins += 1
                stats_dict[outcome.candidate_a.name].losses += 1
                loss_margin = outcome.votes_for_b - outcome.votes_for_a
                stats_dict[outcome.candidate_a.name].smallest_loss_margin = min(
                    stats_dict[outcome.candidate_a.name].smallest_loss_margin, loss_margin
                )
            else:
                # This shouldn't happen with the new design, but keeping for safety
                stats_dict[outcome.candidate_a.name].ties += 1
                stats_dict[outcome.candidate_b.name].ties += 1
        
        # Sort by stats and return results
        sorted_stats = sorted(stats_dict.values())
        return [CandidateResult(candidate=stats.candidate, votes=float(stats.wins))
                for stats in sorted_stats]
    
    @property
    def n_votes(self) -> float:
        """Total votes (not applicable for head-to-head)."""
        return 0.0
    
    def print_pairwise_outcomes(self) -> None:
        """Print all pairwise outcomes for this election."""
        print("\n  Pairwise Outcomes:")
        for outcome in self.pairwise_outcomes:
            winner_marker = f" (Winner: {outcome.winner.name})"
            if outcome.votes_for_a == outcome.votes_for_b:
                winner_marker += " [Random tiebreaker]"
            
            print(f"    {outcome.candidate_a.name} vs {outcome.candidate_b.name}: "
                  f"{outcome.votes_for_a:.0f} - {outcome.votes_for_b:.0f}{winner_marker}")


class HeadToHeadElection(ElectionProcess):
    """Head-to-head election process."""
    
    def __init__(self, debug: bool = False):
        """Initialize head-to-head election."""
        self.debug = debug
    
    @property
    def name(self) -> str:
        """Name of the election process."""
        return "headToHead"
    
    def run(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> HeadToHeadResult:
        """Run head-to-head election with the given candidates and ballots."""
        # Run the election (accumulator computes all matchups during initialization)
        accumulator = HeadToHeadAccumulator(candidates, ballots, ballots[0].gaussian_generator if ballots else None)
        
        # Calculate voter satisfaction
        winner = determine_winner_from_pairwise_outcomes(accumulator.pairwise_outcomes, candidates)
        left_voter_count = sum(1 for ballot in ballots if ballot.voter.ideology < winner.ideology)
        voter_satisfaction = 1 - abs((2.0 * left_voter_count / len(ballots)) - 1)
        
        result = HeadToHeadResult(accumulator.pairwise_outcomes, candidates, voter_satisfaction)
        
        return result
    
    def run_with_ballots(self, candidates: List[Candidate], ballots: List[RCVBallot], gaussian_generator=None) -> HeadToHeadResult:
        """Run head-to-head election (legacy method)."""
        accumulator = HeadToHeadAccumulator(candidates, ballots, gaussian_generator)
        return HeadToHeadResult(accumulator.pairwise_outcomes, candidates, 0.0)
    
    def run_with_voters(self, voters: List, candidates: List[Candidate], 
                       ballots: List[RCVBallot], gaussian_generator=None) -> HeadToHeadResult:
        """Run head-to-head election and calculate voter satisfaction (legacy method)."""
        accumulator = HeadToHeadAccumulator(candidates, ballots, gaussian_generator)
        
        # Calculate voter satisfaction
        winner = determine_winner_from_pairwise_outcomes(accumulator.pairwise_outcomes, candidates)
        left_voter_count = sum(1 for v in voters if v.ideology < winner.ideology)
        voter_satisfaction = 1 - abs((2.0 * left_voter_count / len(voters)) - 1)
        
        result = HeadToHeadResult(accumulator.pairwise_outcomes, candidates, voter_satisfaction)
        
        return result
