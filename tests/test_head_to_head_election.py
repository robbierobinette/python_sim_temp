"""
Tests for HeadToHeadElection class.
"""
import pytest
from simulation_base.head_to_head_election import (
    HeadToHeadElection, HeadToHeadResult, HeadToHeadAccumulator,
    PairwiseOutcome, CandidateStats, determine_winner_from_pairwise_outcomes
)
from simulation_base.candidate import Candidate
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.ballot import RCVBallot, CandidateScore
from simulation_base.election_result import CandidateResult
from simulation_base.election_definition import ElectionDefinition
from simulation_base.combined_population import CombinedPopulation
from simulation_base.population_group import PopulationGroup
from simulation_base.election_config import ElectionConfig
from simulation_base.gaussian_generator import GaussianGenerator
from simulation_base.voter import Voter


class TestPairwiseOutcome:
    """Test PairwiseOutcome class."""
    
    def test_pairwise_outcome_creation(self):
        """Test creating a PairwiseOutcome."""
        candidate_a = Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False)
        candidate_b = Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        
        outcome = PairwiseOutcome(
            candidate_a=candidate_a,
            candidate_b=candidate_b,
            votes_for_a=60.0,
            votes_for_b=40.0
        )
        
        assert outcome.candidate_a == candidate_a
        assert outcome.candidate_b == candidate_b
        assert outcome.votes_for_a == 60.0
        assert outcome.votes_for_b == 40.0
    
    def test_winner_property(self):
        """Test the winner property."""
        candidate_a = Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False)
        candidate_b = Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        
        # Test A wins
        outcome = PairwiseOutcome(candidate_a, candidate_b, 60.0, 40.0)
        assert outcome.winner == candidate_a
        
        # Test B wins
        outcome = PairwiseOutcome(candidate_a, candidate_b, 40.0, 60.0)
        assert outcome.winner == candidate_b
        
        # Test tie (B wins by default due to else clause)
        outcome = PairwiseOutcome(candidate_a, candidate_b, 50.0, 50.0)
        assert outcome.winner == candidate_b
    
    def test_margin_property(self):
        """Test the margin property."""
        candidate_a = Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False)
        candidate_b = Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        
        # Test A wins by 20
        outcome = PairwiseOutcome(candidate_a, candidate_b, 60.0, 40.0)
        assert outcome.margin == 20.0
        
        # Test B wins by 30
        outcome = PairwiseOutcome(candidate_a, candidate_b, 35.0, 65.0)
        assert outcome.margin == 30.0
        
        # Test tie
        outcome = PairwiseOutcome(candidate_a, candidate_b, 50.0, 50.0)
        assert outcome.margin == 0.0
    
    def test_string_representation(self):
        """Test string representation."""
        candidate_a = Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False)
        candidate_b = Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        
        outcome = PairwiseOutcome(candidate_a, candidate_b, 60.0, 40.0)
        str_repr = str(outcome)
        
        assert "Alice vs Bob" in str_repr
        assert "60.0 - 40.0" in str_repr


class TestCandidateStats:
    """Test CandidateStats class."""
    
    def test_candidate_stats_creation(self):
        """Test creating a CandidateStats."""
        candidate = Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False)
        
        stats = CandidateStats(
            candidate=candidate,
            wins=5,
            losses=2,
            ties=1,
            smallest_loss_margin=10.0
        )
        
        assert stats.candidate == candidate
        assert stats.wins == 5
        assert stats.losses == 2
        assert stats.ties == 1
        assert stats.smallest_loss_margin == 10.0
    
    def test_less_than_comparison(self):
        """Test the __lt__ method for sorting."""
        candidate_a = Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False)
        candidate_b = Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        
        # Test by wins (more wins is better)
        stats_a = CandidateStats(candidate_a, wins=5, losses=2, ties=1, smallest_loss_margin=10.0)
        stats_b = CandidateStats(candidate_b, wins=3, losses=4, ties=1, smallest_loss_margin=5.0)
        
        assert stats_a < stats_b  # A has more wins, so A < B (A is better)
        
        # Test by smallest loss margin when wins are equal
        stats_a = CandidateStats(candidate_a, wins=3, losses=2, ties=1, smallest_loss_margin=15.0)
        stats_b = CandidateStats(candidate_b, wins=3, losses=2, ties=1, smallest_loss_margin=5.0)
        
        assert stats_b < stats_a  # B has smaller loss margin, so B is better
        
        # Test by name when wins and loss margins are equal
        stats_a = CandidateStats(candidate_a, wins=3, losses=2, ties=1, smallest_loss_margin=10.0)
        stats_b = CandidateStats(candidate_b, wins=3, losses=2, ties=1, smallest_loss_margin=10.0)
        
        assert stats_a < stats_b  # Alice < Bob alphabetically


class TestDetermineWinnerFromPairwiseOutcomes:
    """Test determine_winner_from_pairwise_outcomes function."""
    
    def test_determine_winner_clear_winner(self):
        """Test determining winner with clear winner."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        # Alice beats Bob and Charlie
        outcomes = [
            PairwiseOutcome(candidates[0], candidates[1], 60.0, 40.0),  # Alice beats Bob
            PairwiseOutcome(candidates[0], candidates[2], 55.0, 45.0),  # Alice beats Charlie
            PairwiseOutcome(candidates[1], candidates[2], 50.0, 50.0)   # Bob ties Charlie
        ]
        
        winner = determine_winner_from_pairwise_outcomes(outcomes, candidates)
        assert winner == candidates[0]  # Alice should win
    
    def test_determine_winner_with_ties(self):
        """Test determining winner with ties."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # All outcomes are ties
        outcomes = [
            PairwiseOutcome(candidates[0], candidates[1], 50.0, 50.0)
        ]
        
        winner = determine_winner_from_pairwise_outcomes(outcomes, candidates)
        assert winner in candidates  # Should return one of them
    
    def test_determine_winner_with_loss_margin_tiebreaker(self):
        """Test determining winner using loss margin as tiebreaker."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        # Alice and Bob both have 1 win, 1 loss
        # Alice's loss margin is smaller (better)
        outcomes = [
            PairwiseOutcome(candidates[0], candidates[1], 60.0, 40.0),  # Alice beats Bob
            PairwiseOutcome(candidates[0], candidates[2], 45.0, 55.0),  # Alice loses to Charlie (margin 10)
            PairwiseOutcome(candidates[1], candidates[2], 70.0, 30.0)   # Bob beats Charlie
        ]
        
        winner = determine_winner_from_pairwise_outcomes(outcomes, candidates)
        assert winner == candidates[0]  # Alice should win (smaller loss margin)


class TestHeadToHeadAccumulator:
    """Test HeadToHeadAccumulator class."""
    
    def test_head_to_head_accumulator_creation(self):
        """Test creating a HeadToHeadAccumulator."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create ballots
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.8),
            CandidateScore(candidate=candidates[1], score=0.6)
        ]
        ballot = RCVBallot(unsorted_candidates=candidate_scores)
        ballots = [ballot, ballot]
        
        accumulator = HeadToHeadAccumulator(candidates, ballots)
        
        assert accumulator.candidates == candidates
        assert len(accumulator.pairwise_outcomes) == 1  # Only one pair for 2 candidates
        assert isinstance(accumulator.pairwise_outcomes[0], PairwiseOutcome)
    
    def test_head_to_head_accumulator_three_candidates(self):
        """Test HeadToHeadAccumulator with three candidates."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        # Create ballots
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.8),
            CandidateScore(candidate=candidates[1], score=0.6),
            CandidateScore(candidate=candidates[2], score=0.7)
        ]
        ballot = RCVBallot(unsorted_candidates=candidate_scores)
        ballots = [ballot]
        
        accumulator = HeadToHeadAccumulator(candidates, ballots)
        
        # Should have 3 pairwise outcomes (A vs B, A vs C, B vs C)
        assert len(accumulator.pairwise_outcomes) == 3
        
        # Check that all pairs are represented
        pairs = set()
        for outcome in accumulator.pairwise_outcomes:
            pair = (outcome.candidate_a.name, outcome.candidate_b.name)
            pairs.add(pair)
        
        expected_pairs = {
            ("Alice", "Bob"),
            ("Alice", "Charlie"),
            ("Bob", "Charlie")
        }
        assert pairs == expected_pairs
    
    def test_head_to_head_accumulator_vote_calculation(self):
        """Test that HeadToHeadAccumulator correctly calculates votes."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create ballots where Alice is clearly preferred
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.9),  # Alice first
            CandidateScore(candidate=candidates[1], score=0.1)   # Bob second
        ]
        ballot1 = RCVBallot(unsorted_candidates=candidate_scores)
        
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.8),  # Alice first
            CandidateScore(candidate=candidates[1], score=0.2)   # Bob second
        ]
        ballot2 = RCVBallot(unsorted_candidates=candidate_scores)
        
        ballots = [ballot1, ballot2]
        
        accumulator = HeadToHeadAccumulator(candidates, ballots)
        
        # Alice should win both head-to-head matchups
        outcome = accumulator.pairwise_outcomes[0]
        assert outcome.votes_for_a == 2.0  # Alice gets 2 votes
        assert outcome.votes_for_b == 0.0  # Bob gets 0 votes
        assert outcome.winner == candidates[0]  # Alice wins


class TestHeadToHeadResult:
    """Test HeadToHeadResult class."""
    
    def test_head_to_head_result_creation(self):
        """Test creating a HeadToHeadResult."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        outcomes = [
            PairwiseOutcome(candidates[0], candidates[1], 60.0, 40.0)
        ]
        
        result = HeadToHeadResult(outcomes, candidates, voter_satisfaction=0.75)
        
        assert result.pairwise_outcomes == outcomes
        assert result.candidates == candidates
        assert result._voter_satisfaction == 0.75
    
    def test_winner_method(self):
        """Test the winner method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        outcomes = [
            PairwiseOutcome(candidates[0], candidates[1], 60.0, 40.0)
        ]
        
        result = HeadToHeadResult(outcomes, candidates)
        winner = result.winner()
        
        assert winner == candidates[0]  # Alice should win
    
    def test_voter_satisfaction_method(self):
        """Test the voter_satisfaction method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        outcomes = [
            PairwiseOutcome(candidates[0], candidates[1], 60.0, 40.0)
        ]
        
        result = HeadToHeadResult(outcomes, candidates, voter_satisfaction=0.85)
        assert result.voter_satisfaction() == 0.85
    
    def test_ordered_results_method(self):
        """Test the ordered_results method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        outcomes = [
            PairwiseOutcome(candidates[0], candidates[1], 60.0, 40.0),  # Alice beats Bob
            PairwiseOutcome(candidates[0], candidates[2], 55.0, 45.0),  # Alice beats Charlie
            PairwiseOutcome(candidates[1], candidates[2], 50.0, 50.0)   # Bob ties Charlie
        ]
        
        result = HeadToHeadResult(outcomes, candidates)
        ordered = result.ordered_results()
        
        # Should be ordered by head-to-head wins
        assert len(ordered) == 3
        assert ordered[0].candidate == candidates[0]  # Alice should be first (2 wins)
        assert ordered[0].votes == 2.0  # Alice has 2 wins
    
    def test_n_votes_property(self):
        """Test the n_votes property."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        outcomes = [
            PairwiseOutcome(candidates[0], candidates[1], 60.0, 40.0)
        ]
        
        result = HeadToHeadResult(outcomes, candidates)
        assert result.n_votes == 0.0  # Head-to-head doesn't have total votes
    
    def test_print_pairwise_outcomes_method(self):
        """Test the print_pairwise_outcomes method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        outcomes = [
            PairwiseOutcome(candidates[0], candidates[1], 60.0, 40.0)
        ]
        
        result = HeadToHeadResult(outcomes, candidates)
        
        # Should not raise an error
        result.print_pairwise_outcomes()


class TestHeadToHeadElection:
    """Test HeadToHeadElection class."""
    
    def test_head_to_head_election_initialization(self):
        """Test HeadToHeadElection initialization."""
        # Test with debug=False (default)
        election = HeadToHeadElection()
        assert not election.debug
        
        # Test with debug=True
        election = HeadToHeadElection(debug=True)
        assert election.debug
    
    def test_name_property(self):
        """Test the name property."""
        election = HeadToHeadElection()
        assert election.name == "headToHead"
    
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
        ballot1 = RCVBallot(unsorted_candidates=candidate_scores)
        
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.7),  # Alice preferred
            CandidateScore(candidate=candidates[1], score=0.5)   # Bob less preferred
        ]
        ballot2 = RCVBallot(unsorted_candidates=candidate_scores)
        
        ballots = [ballot1, ballot2]
        
        election = HeadToHeadElection()
        result = election.run_with_ballots(candidates, ballots)
        
        assert isinstance(result, HeadToHeadResult)
        assert result.winner() == candidates[0]  # Alice should win
        assert len(result.pairwise_outcomes) == 1  # One pairwise matchup
    
    def test_run_with_ballots_three_candidates(self):
        """Test run_with_ballots with three candidates."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        # Create ballots where Alice is clearly preferred
        ballots = []
        for _ in range(5):
            candidate_scores = [
                CandidateScore(candidate=candidates[0], score=0.9),  # Alice
                CandidateScore(candidate=candidates[1], score=0.3),  # Bob
                CandidateScore(candidate=candidates[2], score=0.5)   # Charlie
            ]
            ballots.append(RCVBallot(unsorted_candidates=candidate_scores))
        
        election = HeadToHeadElection()
        result = election.run_with_ballots(candidates, ballots)
        
        assert isinstance(result, HeadToHeadResult)
        assert result.winner() == candidates[0]  # Alice should win
        assert len(result.pairwise_outcomes) == 3  # Three pairwise matchups
    
    def test_run_with_ballots_empty_ballots(self):
        """Test run_with_ballots with empty ballot list."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        election = HeadToHeadElection()
        result = election.run_with_ballots(candidates, [])
        
        # Should handle empty ballots
        assert isinstance(result, HeadToHeadResult)
        assert len(result.pairwise_outcomes) == 1  # Still one pairwise matchup
        # All votes should be 0
        for outcome in result.pairwise_outcomes:
            assert outcome.votes_for_a == 0.0
            assert outcome.votes_for_b == 0.0
    
    def test_run_with_ballots_single_candidate(self):
        """Test run_with_ballots with single candidate."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False)
        ]
        
        # Create ballot for single candidate
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.8)
        ]
        ballot = RCVBallot(unsorted_candidates=candidate_scores)
        
        election = HeadToHeadElection()
        result = election.run_with_ballots(candidates, [ballot])
        
        assert result.winner() == candidates[0]
        assert len(result.pairwise_outcomes) == 0  # No pairwise matchups with single candidate
    
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
        ballot = RCVBallot(unsorted_candidates=candidate_scores)
        ballots = [ballot, ballot]
        
        election = HeadToHeadElection()
        result = election.run_with_voters(voters, candidates, ballots)
        
        assert isinstance(result, HeadToHeadResult)
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
            gaussian_generator=gaussian_generator
        )
        
        election = HeadToHeadElection()
        result = election.run(election_def)
        
        assert isinstance(result, HeadToHeadResult)
        # Should calculate voter satisfaction
        assert hasattr(result, '_voter_satisfaction')


class TestHeadToHeadElectionEdgeCases:
    """Test edge cases for HeadToHeadElection."""
    
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
        ballot = RCVBallot(unsorted_candidates=candidate_scores)
        
        election = HeadToHeadElection()
        result = election.run_with_ballots(candidates, [ballot, ballot])
        
        # Should handle tie
        assert isinstance(result, HeadToHeadResult)
        winner = result.winner()
        assert winner in candidates
    
    def test_run_with_ballots_no_valid_choices(self):
        """Test run_with_ballots when ballots have no valid choices."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create ballot with candidates not in the active set
        other_candidate = Candidate(name="Other", tag=INDEPENDENTS, ideology=0.0, quality=0.5, incumbent=False)
        candidate_scores = [
            CandidateScore(candidate=other_candidate, score=0.8)
        ]
        ballot = RCVBallot(unsorted_candidates=candidate_scores)
        
        election = HeadToHeadElection()
        result = election.run_with_ballots(candidates, [ballot])
        
        # Should handle ballot with no valid choices
        assert isinstance(result, HeadToHeadResult)
        # All votes should be 0
        for outcome in result.pairwise_outcomes:
            assert outcome.votes_for_a == 0.0
            assert outcome.votes_for_b == 0.0
    
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
            ballots.append(RCVBallot(unsorted_candidates=candidate_scores))
        
        election = HeadToHeadElection()
        result = election.run_with_ballots(candidates, ballots)
        
        assert isinstance(result, HeadToHeadResult)
        assert len(result.pairwise_outcomes) == 3
        winner = result.winner()
        assert winner in candidates
    
    def test_head_to_head_accumulator_with_duplicate_candidates(self):
        """Test HeadToHeadAccumulator with duplicate candidates."""
        candidate = Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False)
        candidates = [candidate, candidate]  # Duplicate candidate
        
        candidate_scores = [
            CandidateScore(candidate=candidate, score=0.8)
        ]
        ballot = RCVBallot(unsorted_candidates=candidate_scores)
        
        accumulator = HeadToHeadAccumulator(candidates, [ballot])
        
        # Should handle duplicate candidates
        assert len(accumulator.pairwise_outcomes) == 1  # One pairwise matchup
        outcome = accumulator.pairwise_outcomes[0]
        assert outcome.candidate_a == candidate
        assert outcome.candidate_b == candidate
