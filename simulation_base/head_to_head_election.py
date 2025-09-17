"""
Head-to-head election implementation using Tideman's method.
"""
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from .candidate import Candidate
from .ballot import RCVBallot
from .election_result import ElectionResult, CandidateResult
from .gaussian_generator import GaussianGenerator


@dataclass
class TidemansRankPair:
    """Represents a pairwise comparison between two candidates."""
    c1: Candidate
    c2: Candidate
    v1: float
    v2: float
    
    @property
    def margin(self) -> float:
        """Margin of victory."""
        return self.v1 - self.v2
    
    @property
    def pct(self) -> float:
        """Percentage of votes for c1."""
        return self.v1 / (self.v1 + self.v2) if (self.v1 + self.v2) > 0 else 0.0
    
    def __lt__(self, other: 'TidemansRankPair') -> bool:
        """Compare pairs for sorting."""
        if self.margin != other.margin:
            return self.margin > other.margin  # Higher margin first
        elif self.pct != other.pct:
            return self.pct > other.pct  # Higher percentage first
        else:
            return str(self) < str(other)
    
    def __str__(self) -> str:
        return f"{self.c1.name:6s} {self.c2.name:6s} {self.v1:8.2f} {self.v2:8.2f}"


class HeadToHeadAccumulator:
    """Accumulates head-to-head results from ballots."""
    
    def __init__(self, candidates: List[Candidate]):
        """Initialize accumulator."""
        self.candidates = candidates
        self.n_candidates = len(candidates)
        self.candidate_indices = {c: i for i, c in enumerate(candidates)}
        self.candidate_set = set(candidates)
        self.results_matrix = [[0.0 for _ in range(self.n_candidates)] 
                              for _ in range(self.n_candidates)]
    
    def add_ballot(self, raw_ballot: RCVBallot) -> None:
        """Add a ballot to the accumulator."""
        # Filter ballot to only include candidates in this election
        filtered_candidates = [cs for cs in raw_ballot.unsorted_candidates 
                              if cs.candidate in self.candidate_set]
        
        # Create a new ballot with filtered candidates
        ballot = RCVBallot(
            unsorted_candidates=filtered_candidates,
            weight=raw_ballot.weight
        )
        
        # Find candidates not listed on the ballot
        listed_candidates = {cs.candidate for cs in ballot.unsorted_candidates}
        unlisted_candidates = self.candidate_set - listed_candidates
        
        def index_for(ballot_index: int) -> int:
            """Get matrix index for candidate at ballot position."""
            return self.candidate_indices[ballot.sorted_candidates[ballot_index].candidate]
        
        # Process each candidate on the ballot
        for i in range(len(ballot.sorted_candidates)):
            ci = index_for(i)
            
            # Candidate i gets a vote against each candidate listed after i
            for j in range(i + 1, len(ballot.unsorted_candidates)):
                cj = index_for(j)
                self.results_matrix[ci][cj] += ballot.weight
            
            # Candidate i gets a vote against each unlisted candidate
            for unlisted in unlisted_candidates:
                cj = self.candidate_indices[unlisted]
                self.results_matrix[ci][cj] += ballot.weight


class TidemansElement:
    """Represents one step in Tideman's method."""
    
    def __init__(self, candidates: List[Candidate], sorted_pairs: List[TidemansRankPair], 
                 results_matrix: List[List[float]]):
        """Initialize Tideman's element."""
        self.candidates = candidates
        self.sorted_pairs = sorted_pairs
        self.results_matrix = results_matrix
        self.results_hash: Dict[Candidate, List[Candidate]] = {}
        
        # Process pairs in order
        for pair in sorted_pairs:
            self._try_add_pair(pair)
        
        # Find candidates without defeats
        defeated_candidates = set()
        for defeated_list in self.results_hash.values():
            defeated_candidates.update(defeated_list)
        
        candidates_without_defeat = [c for c in candidates if c not in defeated_candidates]
        
        if len(candidates_without_defeat) != 1:
            # Handle cycle - choose candidate with most wins and smallest loss
            self.winner = self._handle_cycle(candidates, defeated_candidates)
        else:
            self.winner = candidates_without_defeat[0]
        
        # Filter out the winner for next iteration
        self.filtered_pairs = [p for p in sorted_pairs 
                              if self.winner not in [p.c1, p.c2]]
        self.filtered_candidates = [c for c in candidates if c != self.winner]
    
    def _try_add_pair(self, pair: TidemansRankPair) -> None:
        """Try to add a pair without creating a cycle."""
        defeated = self.results_hash.get(pair.c1, [])
        new_hash = {**self.results_hash, pair.c1: defeated + [pair.c2]}
        
        # Check for cycles
        if not self._check_for_cycle(new_hash):
            self.results_hash = new_hash
    
    def _check_for_cycle(self, results: Dict[Candidate, List[Candidate]]) -> bool:
        """Check if adding this pair would create a cycle."""
        for candidate in self.candidates:
            if self._has_cycle_from(candidate, results, []):
                return True
        return False
    
    def _has_cycle_from(self, candidate: Candidate, 
                       results: Dict[Candidate, List[Candidate]], 
                       visited: List[Candidate]) -> bool:
        """Check if there's a cycle starting from this candidate."""
        if candidate in visited:
            return True
        
        children = results.get(candidate, [])
        for child in children:
            if self._has_cycle_from(child, results, visited + [candidate]):
                return True
        return False
    
    def _handle_cycle(self, candidates: List[Candidate], 
                     defeated_candidates: Set[Candidate]) -> Candidate:
        """Handle cycle by choosing candidate with most wins and smallest loss."""
        # Calculate wins and losses for each candidate
        candidate_stats = {}
        
        for candidate in candidates:
            wins = 0
            losses = 0
            smallest_loss = float('inf')
            
            for other in candidates:
                if other != candidate:
                    # Check head-to-head results
                    i = candidates.index(candidate)
                    j = candidates.index(other)
                    
                    votes_for = self._get_votes_for_candidate(candidate, other)
                    votes_against = self._get_votes_for_candidate(other, candidate)
                    
                    if votes_for > votes_against:
                        wins += 1
                    elif votes_for < votes_against:
                        losses += 1
                        loss_margin = votes_against - votes_for
                        smallest_loss = min(smallest_loss, loss_margin)
            
            candidate_stats[candidate] = {
                'wins': wins,
                'losses': losses,
                'smallest_loss': smallest_loss if smallest_loss != float('inf') else 0
            }
        
        # Choose candidate with most wins, then smallest loss
        best_candidate = max(candidates, key=lambda c: (
            candidate_stats[c]['wins'],
            -candidate_stats[c]['smallest_loss']  # Negative for ascending order
        ))
        
        return best_candidate
    
    def _get_votes_for_candidate(self, candidate: Candidate, against: Candidate) -> float:
        """Get votes for candidate against another candidate."""
        try:
            i = self.candidates.index(candidate)
            j = self.candidates.index(against)
            return self.results_matrix[i][j]
        except (ValueError, IndexError):
            return 0.0


class TidemansMethod:
    """Implements Tideman's method for resolving head-to-head elections."""
    
    def __init__(self, candidates: List[Candidate], results_matrix: List[List[float]]):
        """Initialize Tideman's method."""
        self.candidates = candidates
        self.results_matrix = results_matrix
        self.sorted_pairs = self._compute_pairs()
        self.elements = []
        self.ordered_candidates = self._compute_ranking()
    
    def _compute_pairs(self) -> List[TidemansRankPair]:
        """Compute all pairwise comparisons."""
        pairs = []
        n = len(self.candidates)
        
        for i in range(n):
            for j in range(i):
                ca = self.candidates[i]
                cb = self.candidates[j]
                va = self.results_matrix[i][j]
                vb = self.results_matrix[j][i]
                
                if va > vb:
                    pairs.append(TidemansRankPair(ca, cb, va, vb))
                else:
                    pairs.append(TidemansRankPair(cb, ca, vb, va))
        
        return sorted(pairs)
    
    def _compute_ranking(self) -> List[Candidate]:
        """Compute the final ranking using Tideman's method."""
        working_candidates = self.candidates.copy()
        working_pairs = self.sorted_pairs.copy()
        ranked_candidates = []
        
        while working_pairs:
            element = TidemansElement(working_candidates, working_pairs, self.results_matrix)
            self.elements.append(element)
            ranked_candidates.append(element.winner)
            
            working_pairs = element.filtered_pairs
            working_candidates = element.filtered_candidates
        
        # Add the last remaining candidate
        if working_candidates:
            ranked_candidates.append(working_candidates[0])
        
        return ranked_candidates
    
    @property
    def winner(self) -> Candidate:
        """Get the winner."""
        return self.ordered_candidates[0]
    
    @property
    def results(self) -> Dict[Candidate, float]:
        """Get results as a dictionary."""
        return {candidate: float(len(self.ordered_candidates) - 1 - i) 
                for i, candidate in enumerate(self.ordered_candidates)}


class HeadToHeadResult(ElectionResult):
    """Result of a head-to-head election."""
    
    def __init__(self, tidemans_method: TidemansMethod, voter_satisfaction: float = 0.0):
        """Initialize head-to-head result."""
        self.tidemans_method = tidemans_method
        self.voter_satisfaction = voter_satisfaction
    
    @property
    def results(self) -> Dict[Candidate, float]:
        """Get results dictionary."""
        return self.tidemans_method.results
    
    @property
    def ordered_results(self) -> List[CandidateResult]:
        """Get ordered results."""
        return [CandidateResult(candidate=c, votes=v) 
                for c, v in self.tidemans_method.results.items()]
    
    @property
    def winner(self) -> Candidate:
        """Get the winner."""
        return self.tidemans_method.winner
    
    @property
    def n_votes(self) -> float:
        """Total votes (not applicable for head-to-head)."""
        return 0.0


class HeadToHeadElection:
    """Head-to-head election process using Tideman's method."""
    
    def __init__(self, debug: bool = False):
        """Initialize head-to-head election."""
        self.debug = debug
    
    @property
    def name(self) -> str:
        """Name of the election process."""
        return "headToHead"
    
    def run(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> HeadToHeadResult:
        """Run head-to-head election."""
        accumulator = HeadToHeadAccumulator(candidates)
        
        for ballot in ballots:
            accumulator.add_ballot(ballot)
        
        tidemans = TidemansMethod(candidates, accumulator.results_matrix)
        return HeadToHeadResult(tidemans, 0.0)
    
    def run_with_voters(self, voters: List, candidates: List[Candidate], 
                       ballots: List[RCVBallot]) -> HeadToHeadResult:
        """Run head-to-head election and calculate voter satisfaction."""
        result = self.run(candidates, ballots)
        
        # Calculate voter satisfaction
        if result.ordered_results:
            winner = result.winner
            left_voter_count = sum(1 for v in voters if v.ideology < winner.ideology)
            voter_satisfaction = 1 - abs((2.0 * left_voter_count / len(voters)) - 1)
            result.voter_satisfaction = voter_satisfaction
        
        return result
