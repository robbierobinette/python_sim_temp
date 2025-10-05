"""
Composable election process implementation.
"""
from typing import List
from .election_result import ElectionResult, CandidateResult
from .election_process import ElectionProcess
from .election_definition import ElectionDefinition
from .candidate import Candidate
from .ballot import RCVBallot


class ComposableElectionResult(ElectionResult):
    """Result of a composable election with primary and general phases."""
    
    def __init__(self, primary_result: ElectionResult, general_result: ElectionResult, voter_satisfaction: float = 0.0):
        """Initialize composable election result."""
        self.primary_result = primary_result
        self.general_result = general_result
        self._voter_satisfaction = voter_satisfaction
    
    def winner(self) -> Candidate:
        """Winner of the general election."""
        return self.general_result.winner()
    
    def voter_satisfaction(self) -> float:
        """Voter satisfaction from general election."""
        return self._voter_satisfaction
    
    def ordered_results(self) -> List[CandidateResult]:
        """Ordered results of the general election."""
        return self.general_result.ordered_results()
    
    @property
    def n_votes(self) -> float:
        """Total votes in general election."""
        return self.general_result.n_votes


class ComposableElection(ElectionProcess):
    """Composable election process that runs a primary followed by a general election."""
    
    def __init__(self, primary_process: ElectionProcess, general_process: ElectionProcess, debug: bool = False):
        """Initialize composable election.
        
        Args:
            primary_process: The election process to use for the primary
            general_process: The election process to use for the general election
            debug: Whether to enable debug output
        """
        self.primary_process = primary_process
        self.general_process = general_process
        self.debug = debug
    
    @property
    def name(self) -> str:
        """Name of the election process."""
        return f"composable_{self.primary_process.name}_to_{self.general_process.name}"
    
    def run(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> ComposableElectionResult:
        """Run composable election with primary followed by general election.
        
        Args:
            candidates: List of candidates in the election
            ballots: List of ballots from voters
            
        Returns:
            ComposableElectionResult with results from both phases
        """
        if self.debug:
            print(f"Running primary election with {self.primary_process.name}")
        
        # Run primary election (primary process will handle skewing internally if needed)
        primary_result = self.primary_process.run(candidates, ballots)
        
        if self.debug:
            print(f"Primary winner: {primary_result.winner().name}")
            print("Primary results:")
            for result in primary_result.ordered_results():
                print(f"  {result.candidate.name}: {result.votes}")
        
        # Get all candidates from primary results (not just the winner)
        # This allows for multi-winner primaries or other scenarios
        primary_candidates = [result.candidate for result in primary_result.ordered_results()]
        
        if self.debug:
            print(f"Running general election with {self.general_process.name}")
            print(f"General election candidates: {[c.name for c in primary_candidates]}")
        
        # Run general election with same ballots (no skewing for general)
        general_result = self.general_process.run(primary_candidates, ballots)
        
        if self.debug:
            print(f"General election winner: {general_result.winner().name}")
            print("General election results:")
            for result in general_result.ordered_results():
                print(f"  {result.candidate.name}: {result.votes}")
        
        # Calculate voter satisfaction based on winner ideology vs population median
        winner = general_result.winner()
        left_voter_count = sum(1 for ballot in ballots if ballot.voter.ideology < winner.ideology)
        voter_satisfaction = 1 - abs((2.0 * left_voter_count / len(ballots)) - 1)
        
        return ComposableElectionResult(primary_result, general_result, voter_satisfaction)
