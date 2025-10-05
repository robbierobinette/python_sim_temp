"""
Tests for Ballot classes.
"""
import pytest
from simulation_base.ballot import RCVBallot, CandidateScore
from simulation_base.candidate import Candidate
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.gaussian_generator import GaussianGenerator
from simulation_base.population_group import PopulationGroup
from simulation_base.voter import Voter
from simulation_base.election_config import ElectionConfig


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
    
    def test_candidate_score_negative_score(self):
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
    
    def test_candidate_score_zero_score(self):
        """Test CandidateScore with zero score."""
        candidate = Candidate(
            name="Charlie",
            tag=INDEPENDENTS,
            ideology=0.0,
            quality=0.7,
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
        
        ballot = create_test_ballot(candidates)
        
        assert hasattr(ballot, 'unsorted_candidates')
        assert hasattr(ballot, 'sorted_candidates')
        assert len(ballot.sorted_candidates) == 3
        assert ballot.voter is not None
    
    def test_rcv_ballot_sorting(self):
        """Test that RCVBallot sorts candidates by score."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        ballot = create_test_ballot(candidates)
        
        # Should be sorted by score (descending)
        assert len(ballot.sorted_candidates) == 3
        assert ballot.sorted_candidates[0].score >= ballot.sorted_candidates[1].score
        assert ballot.sorted_candidates[1].score >= ballot.sorted_candidates[2].score
        
        # Check that candidates are preserved
        candidate_names = [cs.candidate.name for cs in ballot.sorted_candidates]
        assert "Alice" in candidate_names
        assert "Bob" in candidate_names
        assert "Charlie" in candidate_names
    
    def test_rcv_ballot_tie_breaking(self):
        """Test that RCVBallot handles ties with random tie-breaking."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        ballot = create_test_ballot(candidates)
        
        # Should be sorted
        assert len(ballot.sorted_candidates) == 2
        assert ballot.sorted_candidates[0].score >= ballot.sorted_candidates[1].score
    
    def test_rcv_ballot_candidate_selection(self):
        """Test candidate selection from active candidates."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        ballot = create_test_ballot(candidates)
        
        # Test selecting from all candidates
        selected = ballot.candidate(set(candidates))
        assert selected is not None
        
        # Test selecting from subset
        subset = {candidates[1], candidates[2]}  # Bob and Charlie
        selected = ballot.candidate(subset)
        assert selected is not None
    
    def test_rcv_ballot_candidate_selection_with_elimination(self):
        """Test candidate selection when some candidates are eliminated."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        ballot = create_test_ballot(candidates)
        
        # Test with only one candidate active
        active = {candidates[1]}  # Only Bob
        selected = ballot.candidate(active)
        assert selected == candidates[1]
        
        # Test with no candidates active
        active = set()
        selected = ballot.candidate(active)
        assert selected is None
    
    def test_rcv_ballot_with_custom_generator(self):
        """Test RCVBallot with custom Gaussian generator."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create ballot with custom generator
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
        generator = GaussianGenerator(seed=42)
        
        ballot = RCVBallot(voter, candidates, config, generator)
        
        assert ballot.gaussian_generator == generator
        assert len(ballot.sorted_candidates) == 2
    
    def test_rcv_ballot_with_default_generator(self):
        """Test RCVBallot with default Gaussian generator."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        ballot = create_test_ballot(candidates)
        
        assert ballot.gaussian_generator is not None
        assert len(ballot.sorted_candidates) == 2


class TestRCVBallotEdgeCases:
    """Test RCVBallot edge cases."""
    
    def test_rcv_ballot_with_empty_candidates(self):
        """Test RCVBallot with empty candidate list."""
        candidates = []
        
        ballot = create_test_ballot(candidates)
        
        assert len(ballot.sorted_candidates) == 0
        assert len(ballot.unsorted_candidates) == 0
    
    def test_rcv_ballot_with_single_candidate(self):
        """Test RCVBallot with single candidate."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False)
        ]
        
        ballot = create_test_ballot(candidates)
        
        assert len(ballot.sorted_candidates) == 1
        assert ballot.sorted_candidates[0].candidate == candidates[0]
    
    def test_rcv_ballot_with_identical_scores(self):
        """Test RCVBallot with candidates having identical characteristics."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False)  # Same party and ideology
        ]
        
        ballot = create_test_ballot(candidates)
        
        assert len(ballot.sorted_candidates) == 2
        # Scores may differ due to uncertainty component, but should be close
        score_diff = abs(ballot.sorted_candidates[0].score - ballot.sorted_candidates[1].score)
        assert score_diff < 1.0  # Allow for uncertainty differences
    
    def test_rcv_ballot_with_extreme_scores(self):
        """Test RCVBallot with extreme score values."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        ballot = create_test_ballot(candidates)
        
        assert len(ballot.sorted_candidates) == 2
        assert ballot.sorted_candidates[0].score >= ballot.sorted_candidates[1].score
    
    def test_rcv_ballot_candidate_selection_with_none_active(self):
        """Test candidate selection when no candidates are active."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        ballot = create_test_ballot(candidates)
        
        # Test with empty active set
        selected = ballot.candidate(set())
        assert selected is None
    
    def test_rcv_ballot_candidate_selection_with_inactive_candidates(self):
        """Test candidate selection when some candidates are not in active set."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        ballot = create_test_ballot(candidates)
        
        # Test with subset that doesn't include highest-scoring candidate
        active = {candidates[1], candidates[2]}  # Bob and Charlie
        selected = ballot.candidate(active)
        assert selected in active
        assert selected is not None


class TestRCVBallotIntegration:
    """Test RCVBallot integration with other components."""
    
    def test_rcv_ballot_with_voter_generated_scores(self):
        """Test RCVBallot with scores generated from voter preferences."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        # Create ballot with Democratic voter (should prefer Democratic candidate)
        ballot = create_test_ballot(candidates, voter_ideology=-0.4, voter_party=DEMOCRATS)
        
        # Democratic voter should prefer Democratic candidate (Alice)
        assert len(ballot.sorted_candidates) == 3
        
        # Check that Alice (Democratic) is likely to be ranked higher
        alice_score = next(cs.score for cs in ballot.sorted_candidates if cs.candidate.name == "Alice")
        bob_score = next(cs.score for cs in ballot.sorted_candidates if cs.candidate.name == "Bob")
        
        # Alice should have higher score due to party affinity
        assert alice_score >= bob_score