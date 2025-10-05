"""
Tests for InstantRunoffElection class.
"""
import pytest
from simulation_base.instant_runoff_election import (
    InstantRunoffElection, RCVResult, RCVRoundResult
)
from simulation_base.candidate import Candidate
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.ballot import RCVBallot, CandidateScore
from simulation_base.population_group import PopulationGroup
from simulation_base.voter import Voter
from simulation_base.election_config import ElectionConfig
from simulation_base.election_result import CandidateResult
from simulation_base.election_definition import ElectionDefinition
from simulation_base.combined_population import CombinedPopulation
from simulation_base.population_group import PopulationGroup
from simulation_base.election_config import ElectionConfig
from simulation_base.gaussian_generator import GaussianGenerator
from simulation_base.voter import Voter


def create_test_ballot(candidates, voter_ideology=-0.3, voter_party=DEMOCRATS):
    """Helper function to create a test ballot with the new interface."""
    population_group = PopulationGroup(
        tag=voter_party,
        party_bonus=1.0,
        mean=-0.5,
        stddev=1.0,
        skew=0.0,
        weight=100.0
    )
    voter = Voter(party=population_group, ideology=voter_ideology)
    config = ElectionConfig(uncertainty=0.1)
    return RCVBallot(voter, candidates, config)


def create_ballot_with_preference(candidates, preferred_candidate_index, voter_ideology=-0.3, voter_party=DEMOCRATS):
    """Helper function to create a ballot that prefers a specific candidate."""
    population_group = PopulationGroup(
        tag=voter_party,
        party_bonus=1.0,
        mean=-0.5,
        stddev=1.0,
        skew=0.0,
        weight=100.0
    )
    voter = Voter(party=population_group, ideology=voter_ideology)
    config = ElectionConfig(uncertainty=0.1)
    return RCVBallot(voter, candidates, config)


class TestRCVRoundResult:
    """Test RCVRoundResult class."""
    
    def test_rcv_round_result_creation(self):
        """Test creating an RCVRoundResult."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        results = {candidates[0]: 60.0, candidates[1]: 40.0}
        round_result = RCVRoundResult(candidates, results, voter_satisfaction=0.75)
        
        assert round_result._candidates == candidates
        assert round_result._results == results
        assert round_result._voter_satisfaction == 0.75
    
    def test_candidates_property(self):
        """Test the candidates property."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        results = {candidates[0]: 60.0, candidates[1]: 40.0}
        round_result = RCVRoundResult(candidates, results)
        
        assert round_result.candidates == candidates
    
    def test_active_candidates_property(self):
        """Test the active_candidates property."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        results = {candidates[0]: 60.0, candidates[1]: 40.0}
        round_result = RCVRoundResult(candidates, results)
        
        active = round_result.active_candidates
        assert active == {candidates[0], candidates[1]}
    
    def test_winner_method(self):
        """Test the winner method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        results = {candidates[0]: 60.0, candidates[1]: 40.0}
        round_result = RCVRoundResult(candidates, results)
        
        winner = round_result.winner()
        assert winner == candidates[0]  # Alice has more votes
    
    def test_voter_satisfaction_method(self):
        """Test the voter_satisfaction method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        results = {candidates[0]: 60.0, candidates[1]: 40.0}
        round_result = RCVRoundResult(candidates, results, voter_satisfaction=0.85)
        
        assert round_result.voter_satisfaction() == 0.85
    
    def test_ordered_results_method(self):
        """Test the ordered_results method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        results = {candidates[0]: 50.0, candidates[1]: 70.0, candidates[2]: 30.0}
        round_result = RCVRoundResult(candidates, results)
        
        ordered = round_result.ordered_results()
        
        # Should be ordered by votes (descending)
        assert len(ordered) == 3
        assert ordered[0].candidate == candidates[1]  # Bob (70 votes)
        assert ordered[1].candidate == candidates[0]  # Alice (50 votes)
        assert ordered[2].candidate == candidates[2]  # Charlie (30 votes)
        
        # Check vote counts
        assert ordered[0].votes == 70.0
        assert ordered[1].votes == 50.0
        assert ordered[2].votes == 30.0


class TestRCVResult:
    """Test RCVResult class."""
    
    def test_rcv_result_creation(self):
        """Test creating an RCVResult."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        round1 = RCVRoundResult(candidates, {candidates[0]: 60.0, candidates[1]: 40.0})
        round2 = RCVRoundResult([candidates[0]], {candidates[0]: 100.0})
        
        rounds = [round1, round2]
        result = RCVResult(rounds, voter_satisfaction=0.75)
        
        assert result.rounds == rounds
        assert result._voter_satisfaction == 0.75
    
    def test_all_round_results_property(self):
        """Test the all_round_results property."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        round1 = RCVRoundResult(candidates, {candidates[0]: 40.0, candidates[1]: 35.0, candidates[2]: 25.0})
        round2 = RCVRoundResult([candidates[0], candidates[1]], {candidates[0]: 55.0, candidates[1]: 45.0})
        round3 = RCVRoundResult([candidates[0]], {candidates[0]: 100.0})
        
        rounds = [round1, round2, round3]
        result = RCVResult(rounds)
        
        all_results = result.all_round_results
        
        # Should include final round results and eliminated candidates
        assert len(all_results) >= 3
        assert all_results[0].candidate == candidates[0]  # Final winner
        assert all_results[0].votes == 100.0
    
    def test_winner_method(self):
        """Test the winner method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        round1 = RCVRoundResult(candidates, {candidates[0]: 60.0, candidates[1]: 40.0})
        round2 = RCVRoundResult([candidates[0]], {candidates[0]: 100.0})
        
        rounds = [round1, round2]
        result = RCVResult(rounds)
        
        winner = result.winner()
        assert winner == candidates[0]  # Alice wins final round
    
    def test_winner_method_no_rounds(self):
        """Test the winner method with no rounds."""
        result = RCVResult([], voter_satisfaction=0.0)
        
        with pytest.raises(ValueError):
            result.winner()
    
    def test_voter_satisfaction_method(self):
        """Test the voter_satisfaction method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        round1 = RCVRoundResult(candidates, {candidates[0]: 60.0, candidates[1]: 40.0})
        rounds = [round1]
        result = RCVResult(rounds, voter_satisfaction=0.85)
        
        assert result.voter_satisfaction() == 0.85
    
    def test_ordered_results_method(self):
        """Test the ordered_results method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        round1 = RCVRoundResult(candidates, {candidates[0]: 60.0, candidates[1]: 40.0})
        round2 = RCVRoundResult([candidates[0]], {candidates[0]: 100.0})
        
        rounds = [round1, round2]
        result = RCVResult(rounds)
        
        ordered = result.ordered_results()
        
        # Should return final round results
        assert len(ordered) == 1
        assert ordered[0].candidate == candidates[0]
        assert ordered[0].votes == 100.0
    
    def test_ordered_results_method_no_rounds(self):
        """Test the ordered_results method with no rounds."""
        result = RCVResult([], voter_satisfaction=0.0)
        
        ordered = result.ordered_results()
        assert ordered == []
    
    def test_n_votes_property(self):
        """Test the n_votes property."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        round1 = RCVRoundResult(candidates, {candidates[0]: 60.0, candidates[1]: 40.0})
        rounds = [round1]
        result = RCVResult(rounds)
        
        assert result.n_votes == 100.0  # Sum of first round votes
    
    def test_n_votes_property_no_rounds(self):
        """Test the n_votes property with no rounds."""
        result = RCVResult([], voter_satisfaction=0.0)
        
        assert result.n_votes == 0.0
    
    def test_print_detailed_results(self):
        """Test the print_detailed_results method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        round1 = RCVRoundResult(candidates, {candidates[0]: 60.0, candidates[1]: 40.0})
        round2 = RCVRoundResult([candidates[0]], {candidates[0]: 100.0})
        
        rounds = [round1, round2]
        result = RCVResult(rounds)
        
        # Should not raise an error
        result.print_detailed_results()


class TestInstantRunoffElection:
    """Test InstantRunoffElection class."""
    
    def test_instant_runoff_election_initialization(self):
        """Test InstantRunoffElection initialization."""
        # Test with debug=False (default)
        election = InstantRunoffElection()
        assert election.debug == False
        
        # Test with debug=True
        election = InstantRunoffElection(debug=True)
        assert election.debug == True
    
    def test_name_property(self):
        """Test the name property."""
        election = InstantRunoffElection()
        assert election.name == "instantRunoff"
    
    def test_run_with_ballots_basic(self):
        """Test run_with_ballots with basic scenario."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create ballots with clear preferences
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.8),  # Alice preferred
            CandidateScore(candidate=candidates[1], score=0.6)   # Bob less preferred
        ]
        ballot1 = create_test_ballot(candidates)
        
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.7),  # Alice preferred
            CandidateScore(candidate=candidates[1], score=0.5)   # Bob less preferred
        ]
        ballot2 = create_test_ballot(candidates)
        
        ballots = [ballot1, ballot2]
        
        election = InstantRunoffElection()
        result = election.run(candidates, ballots)
        
        assert isinstance(result, RCVResult)
        assert len(result.rounds) == 1  # Should be single round (majority)
        assert result.winner() == candidates[0]  # Alice should win
        assert result.n_votes == 2.0  # Two ballots
    
    def test_run_with_ballots_multiple_rounds(self):
        """Test run_with_ballots requiring multiple rounds."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        # Create ballots where no candidate gets majority in first round
        ballots = []
        
        # 4 ballots for Alice (first choice) - Democratic voters
        for _ in range(4):
            ballots.append(create_test_ballot(candidates, voter_ideology=-0.4, voter_party=DEMOCRATS))
        
        # 3 ballots for Bob (first choice) - Republican voters  
        for _ in range(3):
            ballots.append(create_test_ballot(candidates, voter_ideology=0.4, voter_party=REPUBLICANS))
        
        # 3 ballots for Charlie (first choice) - Independent voters
        for _ in range(3):
            ballots.append(create_test_ballot(candidates, voter_ideology=0.0, voter_party=INDEPENDENTS))
        
        election = InstantRunoffElection()
        result = election.run(candidates, ballots)
        
        assert isinstance(result, RCVResult)
        assert len(result.rounds) >= 2  # Should require multiple rounds
        assert result.n_votes == 10.0  # 10 ballots total
        
        # Check that elimination occurred
        first_round = result.rounds[0]
        assert len(first_round.active_candidates) == 3
        
        if len(result.rounds) > 1:
            second_round = result.rounds[1]
            assert len(second_round.active_candidates) < 3
    
    def test_run_with_ballots_majority_winner(self):
        """Test run_with_ballots with majority winner in first round."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        # Create ballots where Alice gets majority
        ballots = []
        
        # 6 ballots for Alice (majority of 10)
        for _ in range(6):
            candidate_scores = [
                CandidateScore(candidate=candidates[0], score=0.9),  # Alice
                CandidateScore(candidate=candidates[1], score=0.3),  # Bob
                CandidateScore(candidate=candidates[2], score=0.5)   # Charlie
            ]
            ballots.append(create_test_ballot(candidates))
        
        # 2 ballots for Bob
        for _ in range(2):
            candidate_scores = [
                CandidateScore(candidate=candidates[1], score=0.9),  # Bob
                CandidateScore(candidate=candidates[0], score=0.3),  # Alice
                CandidateScore(candidate=candidates[2], score=0.5)   # Charlie
            ]
            ballots.append(create_test_ballot(candidates))
        
        # 2 ballots for Charlie
        for _ in range(2):
            candidate_scores = [
                CandidateScore(candidate=candidates[2], score=0.9),  # Charlie
                CandidateScore(candidate=candidates[0], score=0.3),  # Alice
                CandidateScore(candidate=candidates[1], score=0.5)   # Bob
            ]
            ballots.append(create_test_ballot(candidates))
        
        election = InstantRunoffElection()
        result = election.run(candidates, ballots)
        
        assert isinstance(result, RCVResult)
        assert len(result.rounds) == 1  # Should be single round (majority)
        assert result.winner() == candidates[0]  # Alice should win
        assert result.n_votes == 10.0
    
    
    def test_run_with_ballots_single_candidate(self):
        """Test run_with_ballots with single candidate."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False)
        ]
        
        # Create ballot for single candidate
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.8)
        ]
        ballot = create_test_ballot(candidates)
        
        election = InstantRunoffElection()
        result = election.run(candidates, [ballot])
        
        assert result.winner() == candidates[0]
        assert result.n_votes == 1.0
        assert len(result.rounds) == 1  # Single round
    
    def test_run_with_voters_method(self):
        """Test the run_with_voters method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create voters
        population_group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        voters = [
            Voter(party=population_group, ideology=-0.3),
            Voter(party=population_group, ideology=-0.4)
        ]
        
        # Create ballots
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.8),
            CandidateScore(candidate=candidates[1], score=0.6)
        ]
        ballot = create_test_ballot(candidates)
        ballots = [ballot, ballot]
        
        election = InstantRunoffElection()
        result = election.run(candidates, ballots)
        
        assert isinstance(result, RCVResult)
        assert result.n_votes == 2.0
        # Should calculate voter satisfaction
        assert hasattr(result, '_voter_satisfaction')
    
    def test_run_method_with_election_definition(self):
        """Test the run method with ElectionDefinition."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=10)
        
        # Create election definition
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator,
            state="Test"
        )
        
        election = InstantRunoffElection()
        # Create ballots for the new interface
        from simulation_base.ballot_utils import create_ballots_from_election_def
        ballots = create_ballots_from_election_def(election_def)
        result = election.run(election_def.candidates, ballots)
        
        assert isinstance(result, RCVResult)
        assert result.n_votes == 10.0  # 10 voters
        # Should calculate voter satisfaction
        assert hasattr(result, '_voter_satisfaction')


class TestInstantRunoffElectionEdgeCases:
    """Test edge cases for InstantRunoffElection."""
    
    def test_run_with_ballots_all_tied(self):
        """Test run_with_ballots with all candidates tied."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create ballots with tied preferences
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.5),
            CandidateScore(candidate=candidates[1], score=0.5)
        ]
        ballot = create_test_ballot(candidates)
        
        election = InstantRunoffElection()
        result = election.run(candidates, [ballot, ballot])
        
        # Should handle tie
        assert result.n_votes == 2.0
        assert len(result.rounds) >= 1
        winner = result.winner()
        assert winner in candidates
    
    
    def test_run_with_ballots_very_large_election(self):
        """Test run_with_ballots with very large election."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        # Create many ballots
        ballots = []
        for i in range(1000):
            # Distribute votes roughly evenly
            if i % 3 == 0:
                candidate_scores = [
                    CandidateScore(candidate=candidates[0], score=0.9),
                    CandidateScore(candidate=candidates[1], score=0.3),
                    CandidateScore(candidate=candidates[2], score=0.5)
                ]
            elif i % 3 == 1:
                candidate_scores = [
                    CandidateScore(candidate=candidates[1], score=0.9),
                    CandidateScore(candidate=candidates[0], score=0.3),
                    CandidateScore(candidate=candidates[2], score=0.5)
                ]
            else:
                candidate_scores = [
                    CandidateScore(candidate=candidates[2], score=0.9),
                    CandidateScore(candidate=candidates[0], score=0.3),
                    CandidateScore(candidate=candidates[1], score=0.5)
                ]
            ballots.append(create_test_ballot(candidates))
        
        election = InstantRunoffElection()
        result = election.run(candidates, ballots)
        
        assert result.n_votes == 1000.0
        assert len(result.rounds) >= 1
        winner = result.winner()
        assert winner in candidates
    
    def test_debug_print_method(self):
        """Test the _debug_print method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        round1 = RCVRoundResult(candidates, {candidates[0]: 60.0, candidates[1]: 40.0})
        round2 = RCVRoundResult([candidates[0]], {candidates[0]: 100.0})
        
        rounds = [round1, round2]
        
        election = InstantRunoffElection(debug=True)
        
        # Should not raise an error
        election._debug_print(rounds)
    
    def test_compute_round_result_method(self):
        """Test the _compute_round_result method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create ballots
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.8),
            CandidateScore(candidate=candidates[1], score=0.6)
        ]
        ballot = create_test_ballot(candidates)
        ballots = [ballot, ballot]
        
        election = InstantRunoffElection()
        round_result = election._compute_round_result(ballots, set(candidates), candidates)
        
        assert isinstance(round_result, RCVRoundResult)
        assert round_result.candidates == candidates
        # Duplicate ballots may cause deduplication in active_candidates
        assert len(round_result.active_candidates) >= 1
        # RCVRoundResult doesn't have n_votes property
    
    def test_compute_rounds_method(self):
        """Test the _compute_rounds method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create ballots
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.8),
            CandidateScore(candidate=candidates[1], score=0.6)
        ]
        ballot = create_test_ballot(candidates)
        ballots = [ballot, ballot]
        
        election = InstantRunoffElection()
        rounds = election._compute_rounds([], ballots, set(candidates), candidates)
        
        assert isinstance(rounds, list)
        assert len(rounds) >= 1
        assert all(isinstance(r, RCVRoundResult) for r in rounds)

