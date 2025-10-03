"""
Tests for Ballot classes.
"""
import pytest
from simulation_base.ballot import RCVBallot, CandidateScore
from simulation_base.candidate import Candidate
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.gaussian_generator import GaussianGenerator


class TestCandidateScore:
    """Test CandidateScore class functionality."""
    
    def test_candidate_score_creation(self):
        """Test creating a CandidateScore."""
        candidate = Candidate(
            name="Alice",
            tag=DEMOCRATS,
            ideology=-0.5,
            quality=0.8,
            incumbent=False
        )
        
        score = CandidateScore(candidate=candidate, score=0.75)
        
        assert score.candidate == candidate
        assert score.score == 0.75
    
    def test_candidate_score_with_negative_score(self):
        """Test CandidateScore with negative score."""
        candidate = Candidate(
            name="Bob",
            tag=REPUBLICANS,
            ideology=0.3,
            quality=0.6,
            incumbent=False
        )
        
        score = CandidateScore(candidate=candidate, score=-0.25)
        
        assert score.candidate == candidate
        assert score.score == -0.25
    
    def test_candidate_score_with_zero_score(self):
        """Test CandidateScore with zero score."""
        candidate = Candidate(
            name="Charlie",
            tag=INDEPENDENTS,
            ideology=0.0,
            quality=0.5,
            incumbent=False
        )
        
        score = CandidateScore(candidate=candidate, score=0.0)
        
        assert score.candidate == candidate
        assert score.score == 0.0


class TestRCVBallot:
    """Test RCVBallot class functionality."""
    
    def test_rcv_ballot_creation(self):
        """Test creating an RCVBallot."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.8),
            CandidateScore(candidate=candidates[1], score=0.6),
            CandidateScore(candidate=candidates[2], score=0.7)
        ]
        
        ballot = RCVBallot(unsorted_candidates=candidate_scores)
        
        assert ballot.unsorted_candidates == candidate_scores
        assert hasattr(ballot, 'sorted_candidates')
        assert len(ballot.sorted_candidates) == 3
    
    def test_rcv_ballot_sorting(self):
        """Test that RCVBallot sorts candidates by score."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.6),  # Lowest
            CandidateScore(candidate=candidates[1], score=0.8),  # Highest
            CandidateScore(candidate=candidates[2], score=0.7)   # Middle
        ]
        
        ballot = RCVBallot(unsorted_candidates=candidate_scores)
        
        # Should be sorted by score (descending)
        assert ballot.sorted_candidates[0].score == 0.8  # Bob
        assert ballot.sorted_candidates[1].score == 0.7  # Charlie
        assert ballot.sorted_candidates[2].score == 0.6  # Alice
        
        # Check that candidates are preserved
        assert ballot.sorted_candidates[0].candidate == candidates[1]
        assert ballot.sorted_candidates[1].candidate == candidates[2]
        assert ballot.sorted_candidates[2].candidate == candidates[0]
    
    def test_rcv_ballot_tie_breaking(self):
        """Test that RCVBallot handles ties with random tie-breaking."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.5),  # Same score
            CandidateScore(candidate=candidates[1], score=0.5)   # Same score
        ]
        
        # Use deterministic generator for testing
        mock_generator = GaussianGenerator(seed=42)
        ballot = RCVBallot(unsorted_candidates=candidate_scores, gaussian_generator=mock_generator)
        
        # Should still be sorted (tie-breaking will determine order)
        assert len(ballot.sorted_candidates) == 2
        assert ballot.sorted_candidates[0].score == 0.5
        assert ballot.sorted_candidates[1].score == 0.5
    
    def test_rcv_ballot_candidate_selection(self):
        """Test candidate selection from active candidates."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.8),  # Highest
            CandidateScore(candidate=candidates[1], score=0.6),  # Lowest
            CandidateScore(candidate=candidates[2], score=0.7)   # Middle
        ]
        
        ballot = RCVBallot(unsorted_candidates=candidate_scores)
        
        # Test with all candidates active
        active_candidates = set(candidates)
        selected = ballot.candidate(active_candidates)
        assert selected == candidates[0]  # Alice (highest score)
        
        # Test with only some candidates active
        active_candidates = {candidates[1], candidates[2]}  # Bob and Charlie
        selected = ballot.candidate(active_candidates)
        assert selected == candidates[2]  # Charlie (higher score than Bob)
        
        # Test with no candidates active
        active_candidates = set()
        selected = ballot.candidate(active_candidates)
        assert selected is None
    
    def test_rcv_ballot_candidate_selection_with_elimination(self):
        """Test candidate selection when some candidates are eliminated."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.8),  # Highest
            CandidateScore(candidate=candidates[1], score=0.6),  # Lowest
            CandidateScore(candidate=candidates[2], score=0.7)   # Middle
        ]
        
        ballot = RCVBallot(unsorted_candidates=candidate_scores)
        
        # Simulate elimination of highest-scoring candidate
        active_candidates = {candidates[1], candidates[2]}  # Bob and Charlie
        selected = ballot.candidate(active_candidates)
        assert selected == candidates[2]  # Charlie (next highest)
        
        # Simulate elimination of top two candidates
        active_candidates = {candidates[1]}  # Only Bob
        selected = ballot.candidate(active_candidates)
        assert selected == candidates[1]  # Bob (only option)
    
    def test_rcv_ballot_with_custom_generator(self):
        """Test RCVBallot with custom Gaussian generator."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.5),
            CandidateScore(candidate=candidates[1], score=0.5)
        ]
        
        # Use custom generator
        custom_generator = GaussianGenerator(seed=123)
        ballot = RCVBallot(unsorted_candidates=candidate_scores, gaussian_generator=custom_generator)
        
        assert ballot.gaussian_generator == custom_generator
        assert len(ballot.sorted_candidates) == 2
    
    def test_rcv_ballot_with_default_generator(self):
        """Test RCVBallot with default Gaussian generator."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False)
        ]
        
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.8)
        ]
        
        ballot = RCVBallot(unsorted_candidates=candidate_scores)
        
        # Should have a default generator
        assert ballot.gaussian_generator is not None
        assert isinstance(ballot.gaussian_generator, GaussianGenerator)


class TestRCVBallotEdgeCases:
    """Test edge cases for RCVBallot."""
    
    def test_rcv_ballot_with_empty_candidates(self):
        """Test RCVBallot with empty candidate list."""
        ballot = RCVBallot(unsorted_candidates=[])
        
        assert len(ballot.sorted_candidates) == 0
        
        # Test candidate selection with empty ballot
        active_candidates = set()
        selected = ballot.candidate(active_candidates)
        assert selected is None
    
    def test_rcv_ballot_with_single_candidate(self):
        """Test RCVBallot with single candidate."""
        candidate = Candidate(name="Solo", tag=INDEPENDENTS, ideology=0.0, quality=0.5, incumbent=False)
        candidate_scores = [CandidateScore(candidate=candidate, score=0.8)]
        
        ballot = RCVBallot(unsorted_candidates=candidate_scores)
        
        assert len(ballot.sorted_candidates) == 1
        assert ballot.sorted_candidates[0].candidate == candidate
        assert ballot.sorted_candidates[0].score == 0.8
        
        # Test candidate selection
        active_candidates = {candidate}
        selected = ballot.candidate(active_candidates)
        assert selected == candidate
    
    def test_rcv_ballot_with_identical_scores(self):
        """Test RCVBallot with all candidates having identical scores."""
        candidates = [
            Candidate(name="A", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="B", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="C", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.5),
            CandidateScore(candidate=candidates[1], score=0.5),
            CandidateScore(candidate=candidates[2], score=0.5)
        ]
        
        # Use deterministic generator for testing
        mock_generator = GaussianGenerator(seed=42)
        ballot = RCVBallot(unsorted_candidates=candidate_scores, gaussian_generator=mock_generator)
        
        # All should have same score
        for cs in ballot.sorted_candidates:
            assert cs.score == 0.5
        
        # Should still be able to select a candidate
        active_candidates = set(candidates)
        selected = ballot.candidate(active_candidates)
        assert selected is not None
        assert selected in candidates
    
    def test_rcv_ballot_with_extreme_scores(self):
        """Test RCVBallot with extreme score values."""
        candidates = [
            Candidate(name="High", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Low", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=1000.0),  # Very high
            CandidateScore(candidate=candidates[1], score=-1000.0)  # Very low
        ]
        
        ballot = RCVBallot(unsorted_candidates=candidate_scores)
        
        # Should be sorted correctly
        assert ballot.sorted_candidates[0].score == 1000.0
        assert ballot.sorted_candidates[1].score == -1000.0
        assert ballot.sorted_candidates[0].candidate == candidates[0]
        assert ballot.sorted_candidates[1].candidate == candidates[1]
    
    def test_rcv_ballot_candidate_selection_with_none_active(self):
        """Test candidate selection when no candidates are active."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.8),
            CandidateScore(candidate=candidates[1], score=0.6)
        ]
        
        ballot = RCVBallot(unsorted_candidates=candidate_scores)
        
        # Test with empty active set
        active_candidates = set()
        selected = ballot.candidate(active_candidates)
        assert selected is None
        
        # Test with None - current implementation raises TypeError
        with pytest.raises(TypeError, match="argument of type 'NoneType' is not iterable"):
            selected = ballot.candidate(None)
    
    def test_rcv_ballot_candidate_selection_with_inactive_candidates(self):
        """Test candidate selection when active candidates don't match ballot."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.8),
            CandidateScore(candidate=candidates[1], score=0.6)
        ]
        
        ballot = RCVBallot(unsorted_candidates=candidate_scores)
        
        # Test with different candidates (not in ballot)
        other_candidate = Candidate(name="Other", tag=INDEPENDENTS, ideology=0.0, quality=0.5, incumbent=False)
        active_candidates = {other_candidate}
        selected = ballot.candidate(active_candidates)
        assert selected is None


class TestRCVBallotIntegration:
    """Test RCVBallot integration with other components."""
    
    def test_rcv_ballot_with_voter_generated_scores(self):
        """Test RCVBallot with scores generated by voter."""
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
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        # Generate ballot using voter
        mock_generator = GaussianGenerator(seed=42)
        ballot = voter.ballot(candidates, config, mock_generator)
        
        # Verify ballot structure
        assert len(ballot.sorted_candidates) == 3
        assert all(hasattr(cs, 'candidate') and hasattr(cs, 'score') for cs in ballot.sorted_candidates)
        
        # Verify sorting
        for i in range(len(ballot.sorted_candidates) - 1):
            assert ballot.sorted_candidates[i].score >= ballot.sorted_candidates[i + 1].score
        
        # Test candidate selection
        active_candidates = set(candidates)
        selected = ballot.candidate(active_candidates)
        assert selected is not None
        assert selected in candidates

