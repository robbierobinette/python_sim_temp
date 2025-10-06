"""
Utility functions for ballot construction.
"""
from typing import List
from .ballot import RCVBallot
from .candidate import Candidate
from .election_definition import ElectionDefinition


def create_ballots_from_election_def(election_def: ElectionDefinition) -> List[RCVBallot]:
    """Create ballots from an election definition.
    
    Args:
        election_def: Complete election definition with candidates, population, config, etc.
        
    Returns:
        List of ballots from all voters
    """
    ballots = []
    for voter in election_def.population.voters:
        ballot = RCVBallot(voter, election_def.candidates, election_def.config, 
                          election_def.gaussian_generator)
        ballots.append(ballot)
    return ballots
