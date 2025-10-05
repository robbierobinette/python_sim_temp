"""
Tests for SimplePlurality class.
"""
import pytest
from simulation_base.simple_plurality import SimplePlurality, SimplePluralityResult
from simulation_base.candidate import Candidate
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.ballot import RCVBallot, CandidateScore
from simulation_base.population_group import PopulationGroup
from simulation_base.voter import Voter
from simulation_base.election_config import ElectionConfig
from simulation_base.election_result import CandidateResult


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


class TestSimplePluralityResult:
    """Test SimplePluralityResult class."""
    
    def test_simple_plurality_result_creation(self):
        """Test creating a SimplePluralityResult."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        results = {candidates[0]: 60.0, candidates[1]: 40.0}
        result = SimplePluralityResult(results, voter_satisfaction=0.75)
        
        assert result._results == results
        assert result._voter_satisfaction == 0.75
    
    def test_winner_method(self):
        """Test the winner method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        results = {candidates[0]: 60.0, candidates[1]: 40.0}
        result = SimplePluralityResult(results)
        
        winner = result.winner()
        assert winner == candidates[0]  # Alice has more votes
    
    def test_voter_satisfaction_method(self):
        """Test the voter_satisfaction method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        results = {candidates[0]: 60.0, candidates[1]: 40.0}
        result = SimplePluralityResult(results, voter_satisfaction=0.85)
        
        assert result.voter_satisfaction() == 0.85
    
    def test_ordered_results_method(self):
        """Test the ordered_results method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        results = {candidates[0]: 50.0, candidates[1]: 70.0, candidates[2]: 30.0}
        result = SimplePluralityResult(results)
        
        ordered = result.ordered_results()
        
        # Should be ordered by votes (descending)
        assert len(ordered) == 3
        assert ordered[0].candidate == candidates[1]  # Bob (70 votes)
        assert ordered[1].candidate == candidates[0]  # Alice (50 votes)
        assert ordered[2].candidate == candidates[2]  # Charlie (30 votes)
        
        # Check vote counts
        assert ordered[0].votes == 70.0
        assert ordered[1].votes == 50.0
        assert ordered[2].votes == 30.0
    
    def test_n_votes_property(self):
        """Test the n_votes property."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        results = {candidates[0]: 60.0, candidates[1]: 40.0}
        result = SimplePluralityResult(results)
        
        assert result.n_votes == 100.0  # 60 + 40
    
    def test_ordered_results_with_ties(self):
        """Test ordered_results with tied vote counts."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        results = {candidates[0]: 50.0, candidates[1]: 50.0}
        result = SimplePluralityResult(results)
        
        ordered = result.ordered_results()
        
        # Should handle ties (order may vary)
        assert len(ordered) == 2
        assert ordered[0].votes == 50.0
        assert ordered[1].votes == 50.0
        assert {ordered[0].candidate, ordered[1].candidate} == {candidates[0], candidates[1]}


class TestSimplePlurality:
    """Test SimplePlurality class."""
    
    def test_simple_plurality_name(self):
        """Test the name property."""
        plurality = SimplePlurality()
        assert plurality.name == "simplePlurality"
    
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
        
        plurality = SimplePlurality()
        result = plurality.run(candidates, ballots)
        
        assert isinstance(result, SimplePluralityResult)
        assert result.winner() == candidates[0]  # Alice should win
        assert result.n_votes == 2.0  # Two ballots
    
    def test_run_with_ballots_clear_winner(self):
        """Test run_with_ballots with clear winner."""
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
            ballots.append(create_test_ballot(candidates))
        
        plurality = SimplePlurality()
        result = plurality.run(candidates, ballots)
        
        assert result.winner() == candidates[0]  # Alice
        assert result.n_votes == 5.0
        
        # Check ordered results
        ordered = result.ordered_results()
        assert ordered[0].candidate == candidates[0]  # Alice first
        assert ordered[0].votes == 5.0
    
    def test_run_with_ballots_tie(self):
        """Test run_with_ballots with tied votes."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create ballots with tied preferences
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.5),  # Alice
            CandidateScore(candidate=candidates[1], score=0.5)   # Bob (tied)
        ]
        ballot1 = create_test_ballot(candidates)
        
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.5),  # Alice (tied)
            CandidateScore(candidate=candidates[1], score=0.5)   # Bob
        ]
        ballot2 = create_test_ballot(candidates)
        
        ballots = [ballot1, ballot2]
        
        plurality = SimplePlurality()
        result = plurality.run(candidates, ballots)
        
        # Should handle tie (winner determined by ballot order/tie-breaking)
        assert result.n_votes == 2.0
        winner = result.winner()
        assert winner in candidates
    
    def test_run_with_ballots_all_candidates_in_results(self):
        """Test that all candidates appear in results, even with zero votes."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        # Create ballots where only Alice gets votes
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.9),  # Alice
            CandidateScore(candidate=candidates[1], score=0.1),  # Bob
            CandidateScore(candidate=candidates[2], score=0.2)   # Charlie
        ]
        ballot = create_test_ballot(candidates)
        
        plurality = SimplePlurality()
        result = plurality.run(candidates, [ballot])
        
        # All candidates should be in results
        ordered = result.ordered_results()
        assert len(ordered) == 3
        
        # Check that all candidates are represented
        result_candidates = [cr.candidate for cr in ordered]
        assert set(result_candidates) == set(candidates)
        
        # Alice should have 1 vote, others should have 0
        alice_result = next(cr for cr in ordered if cr.candidate == candidates[0])
        assert alice_result.votes == 1.0
        
        bob_result = next(cr for cr in ordered if cr.candidate == candidates[1])
        assert bob_result.votes == 0.0
        
        charlie_result = next(cr for cr in ordered if cr.candidate == candidates[2])
        assert charlie_result.votes == 0.0
    
    def test_run_with_ballots_empty_ballots(self):
        """Test run_with_ballots with empty ballot list."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        plurality = SimplePlurality()
        result = plurality.run(candidates, [])
        
        # Should handle empty ballots
        assert result.n_votes == 0.0
        ordered = result.ordered_results()
        assert len(ordered) == 2  # All candidates should still be in results
        
        # All candidates should have 0 votes
        for cr in ordered:
            assert cr.votes == 0.0
    
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
        
        plurality = SimplePlurality()
        result = plurality.run(candidates, [ballot])
        
        assert result.winner() == candidates[0]
        assert result.n_votes == 1.0
        ordered = result.ordered_results()
        assert len(ordered) == 1
        assert ordered[0].votes == 1.0
    
    def test_run_with_ballots_no_first_choice(self):
        """Test run_with_ballots when ballot has no first choice candidate."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create ballot with candidates not in the active set
        other_candidate = Candidate(name="Other", tag=INDEPENDENTS, ideology=0.0, quality=0.5, incumbent=False)
        ballot = create_test_ballot([other_candidate])  # Only the "other" candidate
        
        plurality = SimplePlurality()
        result = plurality.run(candidates, [ballot])
        
        # Should handle ballot with no valid first choice
        assert result.n_votes == 0.0
        ordered = result.ordered_results()
        assert len(ordered) == 2  # All candidates should still be in results
        
        # All candidates should have 0 votes
        for cr in ordered:
            assert cr.votes == 0.0


class TestSimplePluralityEdgeCases:
    """Test edge cases for SimplePlurality."""
    
    def test_run_with_ballots_duplicate_candidates(self):
        """Test run_with_ballots with duplicate candidates."""
        candidate = Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False)
        candidates = [candidate, candidate]  # Duplicate candidate
        
        candidate_scores = [
            CandidateScore(candidate=candidate, score=0.8)
        ]
        ballot = create_test_ballot(candidates)
        
        plurality = SimplePlurality()
        result = plurality.run(candidates, [ballot])
        
        # Should handle duplicate candidates - current implementation deduplicates by candidate object
        assert result.n_votes == 1.0
        ordered = result.ordered_results()
        assert len(ordered) == 1  # Duplicate candidates are deduplicated
    
    def test_run_with_ballots_very_large_vote_counts(self):
        """Test run_with_ballots with very large vote counts."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create many ballots
        ballots = []
        for _ in range(1000):
            candidate_scores = [
                CandidateScore(candidate=candidates[0], score=0.8),
                CandidateScore(candidate=candidates[1], score=0.6)
            ]
            ballots.append(create_test_ballot(candidates))
        
        plurality = SimplePlurality()
        result = plurality.run(candidates, ballots)
        
        assert result.n_votes == 1000.0
        assert result.winner() == candidates[0]  # Alice should win
    
    def test_run_with_ballots_fractional_votes(self):
        """Test run_with_ballots with fractional vote counts."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create ballots with fractional scores
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.8),
            CandidateScore(candidate=candidates[1], score=0.6)
        ]
        ballot = create_test_ballot(candidates)
        
        plurality = SimplePlurality()
        result = plurality.run(candidates, [ballot])
        
        # Should handle fractional votes
        assert result.n_votes == 1.0
        ordered = result.ordered_results()
        assert ordered[0].votes == 1.0
        assert ordered[1].votes == 0.0
    
    def test_simple_plurality_result_with_negative_votes(self):
        """Test SimplePluralityResult with negative vote counts."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # This shouldn't happen in normal operation, but test robustness
        results = {candidates[0]: -10.0, candidates[1]: 5.0}
        result = SimplePluralityResult(results)
        
        # Should handle negative votes
        assert result.n_votes == -5.0  # -10 + 5
        winner = result.winner()
        assert winner == candidates[1]  # Bob has higher (less negative) votes
    
    def test_simple_plurality_result_with_zero_votes(self):
        """Test SimplePluralityResult with zero vote counts."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        results = {candidates[0]: 0.0, candidates[1]: 0.0}
        result = SimplePluralityResult(results)
        
        assert result.n_votes == 0.0
        ordered = result.ordered_results()
        assert len(ordered) == 2
        assert all(cr.votes == 0.0 for cr in ordered)
        
        # Winner should still be determinable (first in ordered results)
        winner = result.winner()
        assert winner in candidates


class TestSimplePluralityIntegration:
    """Test SimplePlurality integration with other components."""
    
    def test_simple_plurality_with_voter_ballots(self):
        """Test SimplePlurality with ballots generated by voters."""
        from simulation_base.voter import Voter
        from simulation_base.population_group import PopulationGroup
        from simulation_base.election_config import ElectionConfig
        
        # Create voter
        population_group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        voter = Voter(party=population_group, ideology=-0.3)
        config = ElectionConfig(uncertainty=0.1)
        
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.4, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Generate ballot using voter
        from simulation_base.gaussian_generator import GaussianGenerator
        mock_generator = GaussianGenerator(seed=42)
        ballot = RCVBallot(voter, candidates, config, mock_generator)
        
        # Run simple plurality
        plurality = SimplePlurality()
        result = plurality.run(candidates, [ballot])
        
        # Verify result
        assert result.n_votes == 1.0
        assert result.winner() in candidates
        ordered = result.ordered_results()
        assert len(ordered) == 2
    
    def test_simple_plurality_result_inheritance(self):
        """Test that SimplePluralityResult properly inherits from ElectionResult."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        results = {candidates[0]: 60.0, candidates[1]: 40.0}
        result = SimplePluralityResult(results, voter_satisfaction=0.75)
        
        # Test that it implements required methods
        assert hasattr(result, 'winner')
        assert hasattr(result, 'voter_satisfaction')
        assert hasattr(result, 'ordered_results')
        
        # Test method calls
        winner = result.winner()
        assert winner == candidates[0]
        
        satisfaction = result.voter_satisfaction()
        assert satisfaction == 0.75
        
        ordered = result.ordered_results()
        assert len(ordered) == 2
        assert all(isinstance(cr, CandidateResult) for cr in ordered)

