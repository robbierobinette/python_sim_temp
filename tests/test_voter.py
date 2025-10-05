"""
Tests for Voter class.
"""
import pytest
from simulation_base.voter import Voter
from simulation_base.ballot import RCVBallot
from simulation_base.population_group import PopulationGroup
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.candidate import Candidate
from simulation_base.election_config import ElectionConfig
from simulation_base.gaussian_generator import GaussianGenerator


class TestVoter:
    """Test Voter class functionality."""
    
    def test_voter_creation(self):
        """Test creating a Voter."""
        population_group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        voter = Voter(party=population_group, ideology=-0.3)
        
        assert voter.party == population_group
        assert voter.ideology == -0.3
    
    def test_distance_score(self):
        """Test distance score calculation."""
        population_group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        voter = Voter(party=population_group, ideology=-0.3)
        
        # Test with candidate at same ideology
        candidate1 = Candidate(
            name="Same",
            tag=DEMOCRATS,
            ideology=-0.3,
            quality=0.5,
            incumbent=False
        )
        assert voter.distance_score(candidate1) == 0.0
        
        # Test with candidate at different ideology
        candidate2 = Candidate(
            name="Different",
            tag=DEMOCRATS,
            ideology=0.3,
            quality=0.5,
            incumbent=False
        )
        assert voter.distance_score(candidate2) == -0.6  # -|(-0.3) - 0.3|
        
        # Test with candidate at opposite ideology
        candidate3 = Candidate(
            name="Opposite",
            tag=REPUBLICANS,
            ideology=0.7,
            quality=0.5,
            incumbent=False
        )
        assert voter.distance_score(candidate3) == -1.0  # -|(-0.3) - 0.7|
    
    def test_uncertainty(self):
        """Test uncertainty calculation."""
        population_group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        voter = Voter(party=population_group, ideology=-0.3)
        config = ElectionConfig(uncertainty=0.2)
        
        # Test with mock Gaussian generator
        mock_generator = GaussianGenerator(seed=42)
        uncertainty = voter.uncertainty(config, mock_generator)
        
        # Uncertainty should be within reasonable bounds
        assert -1.0 <= uncertainty <= 1.0
        
        # Test with different uncertainty values
        config2 = ElectionConfig(uncertainty=0.5)
        uncertainty2 = voter.uncertainty(config2, mock_generator)
        assert -1.0 <= uncertainty2 <= 1.0
    
    def test_score_calculation(self):
        """Test total score calculation."""
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
        
        candidate = Candidate(
            name="Test",
            tag=DEMOCRATS,
            ideology=-0.2,
            quality=0.8,
            incumbent=False
        )
        
        # Test with mock Gaussian generator
        mock_generator = GaussianGenerator(seed=42)
        score = voter.score(candidate, config, mock_generator)
        
        # Score should be reasonable
        assert isinstance(score, float)
        assert -10.0 <= score <= 10.0  # Reasonable bounds
    
    def test_favorite_candidate(self):
        """Test finding favorite candidate."""
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
            Candidate(name="A", tag=DEMOCRATS, ideology=-0.4, quality=0.5, incumbent=False),
            Candidate(name="B", tag=DEMOCRATS, ideology=-0.2, quality=0.8, incumbent=False),
            Candidate(name="C", tag=REPUBLICANS, ideology=0.3, quality=0.3, incumbent=False)
        ]
        
        # Test with mock Gaussian generator
        mock_generator = GaussianGenerator(seed=42)
        favorite_idx = voter.favorite(candidates, config, mock_generator)
        
        assert isinstance(favorite_idx, int)
        assert 0 <= favorite_idx < len(candidates)
    
    def test_ballot_generation(self):
        """Test ballot generation."""
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
            Candidate(name="A", tag=DEMOCRATS, ideology=-0.4, quality=0.5, incumbent=False),
            Candidate(name="B", tag=DEMOCRATS, ideology=-0.2, quality=0.8, incumbent=False),
            Candidate(name="C", tag=REPUBLICANS, ideology=0.3, quality=0.3, incumbent=False)
        ]
        
        # Test with mock Gaussian generator
        mock_generator = GaussianGenerator(seed=42)
        ballot = RCVBallot(voter, candidates, config, mock_generator)
        
        # Check ballot structure
        assert hasattr(ballot, 'sorted_candidates')
        assert len(ballot.sorted_candidates) == len(candidates)
        
        # Check that all candidates are in the ballot
        ballot_candidates = [cs.candidate for cs in ballot.sorted_candidates]
        for candidate in candidates:
            assert candidate in ballot_candidates
        
        # Check that candidates are sorted by score (descending)
        for i in range(len(ballot.sorted_candidates) - 1):
            assert ballot.sorted_candidates[i].score >= ballot.sorted_candidates[i + 1].score


class TestVoterEdgeCases:
    """Test edge cases for Voter."""
    
    def test_voter_with_extreme_ideology(self):
        """Test voter with extreme ideology values."""
        population_group = PopulationGroup(
            tag=REPUBLICANS,
            party_bonus=1.0,
            mean=0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        voter = Voter(party=population_group, ideology=1000.0)
        config = ElectionConfig(uncertainty=0.1)
        
        candidate = Candidate(
            name="Extreme",
            tag=REPUBLICANS,
            ideology=999.0,
            quality=0.5,
            incumbent=False
        )
        
        # Distance score should be negative
        assert voter.distance_score(candidate) < 0
        
        # Score should still be calculable
        mock_generator = GaussianGenerator(seed=42)
        score = voter.score(candidate, config, mock_generator)
        assert isinstance(score, float)
    
    def test_voter_with_zero_uncertainty(self):
        """Test voter with zero uncertainty."""
        population_group = PopulationGroup(
            tag=INDEPENDENTS,
            party_bonus=0.5,
            mean=0.0,
            stddev=1.0,
            skew=0.0,
            weight=50.0
        )
        
        voter = Voter(party=population_group, ideology=0.0)
        config = ElectionConfig(uncertainty=0.0)
        
        candidate = Candidate(
            name="Test",
            tag=INDEPENDENTS,
            ideology=0.1,
            quality=0.5,
            incumbent=False
        )
        
        mock_generator = GaussianGenerator(seed=42)
        uncertainty = voter.uncertainty(config, mock_generator)
        assert uncertainty == 0.0
        
        score = voter.score(candidate, config, mock_generator)
        # Score should be deterministic (no uncertainty)
        assert isinstance(score, float)
    
    def test_voter_with_high_uncertainty(self):
        """Test voter with high uncertainty."""
        population_group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        voter = Voter(party=population_group, ideology=-0.3)
        config = ElectionConfig(uncertainty=10.0)  # Very high uncertainty
        
        candidate = Candidate(
            name="Test",
            tag=DEMOCRATS,
            ideology=-0.2,
            quality=0.5,
            incumbent=False
        )
        
        mock_generator = GaussianGenerator(seed=42)
        uncertainty = voter.uncertainty(config, mock_generator)
        
        # Uncertainty should be scaled by config
        assert abs(uncertainty) <= 10.0
    
    def test_voter_with_single_candidate(self):
        """Test voter with single candidate."""
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
            Candidate(name="Only", tag=DEMOCRATS, ideology=-0.2, quality=0.5, incumbent=False)
        ]
        
        mock_generator = GaussianGenerator(seed=42)
        favorite_idx = voter.favorite(candidates, config, mock_generator)
        assert favorite_idx == 0
        
        ballot = RCVBallot(voter, candidates, config, mock_generator)
        assert len(ballot.sorted_candidates) == 1
        assert ballot.sorted_candidates[0].candidate == candidates[0]
    
    def test_voter_with_empty_candidates(self):
        """Test voter with empty candidate list."""
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
        
        candidates = []
        
        mock_generator = GaussianGenerator(seed=42)
        favorite_idx = voter.favorite(candidates, config, mock_generator)
        assert favorite_idx == -1  # No favorite found
        
        ballot = RCVBallot(voter, candidates, config, mock_generator)
        assert len(ballot.sorted_candidates) == 0


class TestVoterWithDifferentParties:
    """Test Voter with different party affiliations."""
    
    @pytest.mark.parametrize("party_tag,expected_affinity", [
        (DEMOCRATS, 1.0),
        (REPUBLICANS, 0.0),
        (INDEPENDENTS, 0.0)  # Independent candidate has 0.0 affinity for Democratic voters
    ])
    def test_voter_affinity_scoring(self, party_tag, expected_affinity):
        """Test that voter scoring considers party affinity."""
        population_group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        voter = Voter(party=population_group, ideology=-0.3)
        config = ElectionConfig(uncertainty=0.0)  # No uncertainty for deterministic test
        
        candidate = Candidate(
            name="Test",
            tag=party_tag,
            ideology=-0.3,  # Same ideology as voter
            quality=0.0,    # No quality difference
            incumbent=False
        )
        
        mock_generator = GaussianGenerator(seed=42)
        score = voter.score(candidate, config, mock_generator)
        
        # Score should include party affinity
        # distance_score = 0.0 (same ideology)
        # quality = 0.0
        # uncertainty = 0.0
        # affinity = expected_affinity
        expected_score = 0.0 + expected_affinity + 0.0 + 0.0
        assert abs(score - expected_score) < 0.001  # Allow for floating point precision
    
    def test_voter_quality_scoring(self):
        """Test that voter scoring considers candidate quality."""
        population_group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        voter = Voter(party=population_group, ideology=-0.3)
        config = ElectionConfig(uncertainty=0.0)  # No uncertainty for deterministic test
        
        # Test with different quality candidates
        candidates = [
            Candidate(name="Low", tag=DEMOCRATS, ideology=-0.3, quality=0.1, incumbent=False),
            Candidate(name="High", tag=DEMOCRATS, ideology=-0.3, quality=0.9, incumbent=False)
        ]
        
        mock_generator = GaussianGenerator(seed=42)
        favorite_idx = voter.favorite(candidates, config, mock_generator)
        
        # Should prefer the higher quality candidate
        assert favorite_idx == 1  # High quality candidate

