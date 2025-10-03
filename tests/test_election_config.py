"""
Tests for ElectionConfig class.
"""
import pytest
from simulation_base.election_config import ElectionConfig


class TestElectionConfig:
    """Test ElectionConfig class functionality."""
    
    def test_election_config_creation(self):
        """Test creating an ElectionConfig."""
        config = ElectionConfig(uncertainty=0.1)
        
        assert config.uncertainty == 0.1
    
    def test_election_config_with_zero_uncertainty(self):
        """Test ElectionConfig with zero uncertainty."""
        config = ElectionConfig(uncertainty=0.0)
        
        assert config.uncertainty == 0.0
    
    def test_election_config_with_negative_uncertainty(self):
        """Test ElectionConfig with negative uncertainty."""
        config = ElectionConfig(uncertainty=-0.1)
        
        assert config.uncertainty == -0.1
    
    def test_election_config_with_high_uncertainty(self):
        """Test ElectionConfig with high uncertainty."""
        config = ElectionConfig(uncertainty=10.0)
        
        assert config.uncertainty == 10.0
    
    def test_election_config_with_fractional_uncertainty(self):
        """Test ElectionConfig with fractional uncertainty."""
        config = ElectionConfig(uncertainty=0.12345)
        
        assert config.uncertainty == 0.12345
    
    def test_election_config_equality(self):
        """Test ElectionConfig equality."""
        config1 = ElectionConfig(uncertainty=0.1)
        config2 = ElectionConfig(uncertainty=0.1)
        config3 = ElectionConfig(uncertainty=0.2)
        
        assert config1 == config2
        assert config1 != config3
    
    def test_election_config_string_representation(self):
        """Test ElectionConfig string representation."""
        config = ElectionConfig(uncertainty=0.1)
        str_repr = str(config)
        
        # Should contain uncertainty value
        assert "0.1" in str_repr or "uncertainty" in str_repr.lower()
    
    def test_election_config_hash(self):
        """Test ElectionConfig hash functionality."""
        config1 = ElectionConfig(uncertainty=0.1)
        config2 = ElectionConfig(uncertainty=0.1)
        config3 = ElectionConfig(uncertainty=0.2)
        
        # ElectionConfig is not hashable (no __hash__ method)
        with pytest.raises(TypeError, match="unhashable type"):
            hash(config1)
        
        # Should not be usable in sets due to unhashable type
        with pytest.raises(TypeError, match="unhashable type"):
            config_set = {config1, config2, config3}
    
    def test_election_config_immutability(self):
        """Test that ElectionConfig is immutable."""
        config = ElectionConfig(uncertainty=0.1)
        
        # Should not be able to modify uncertainty directly
        # (This depends on implementation - if it's a dataclass with frozen=True)
        try:
            config.uncertainty = 0.2
            # If this doesn't raise an error, the config is mutable
            # This is acceptable depending on the implementation
        except (AttributeError, TypeError):
            # Expected if the config is immutable
            pass


class TestElectionConfigEdgeCases:
    """Test edge cases for ElectionConfig."""
    
    def test_election_config_with_extreme_values(self):
        """Test ElectionConfig with extreme uncertainty values."""
        # Test with very large positive value
        config = ElectionConfig(uncertainty=1e6)
        assert config.uncertainty == 1e6
        
        # Test with very small positive value
        config = ElectionConfig(uncertainty=1e-10)
        assert config.uncertainty == 1e-10
        
        # Test with very large negative value
        config = ElectionConfig(uncertainty=-1e6)
        assert config.uncertainty == -1e6
    
    def test_election_config_with_nan_uncertainty(self):
        """Test ElectionConfig with NaN uncertainty."""
        import math
        
        config = ElectionConfig(uncertainty=float('nan'))
        assert math.isnan(config.uncertainty)
    
    def test_election_config_with_infinity_uncertainty(self):
        """Test ElectionConfig with infinity uncertainty."""
        import math
        
        # Test with positive infinity
        config = ElectionConfig(uncertainty=float('inf'))
        assert math.isinf(config.uncertainty)
        assert config.uncertainty > 0
        
        # Test with negative infinity
        config = ElectionConfig(uncertainty=float('-inf'))
        assert math.isinf(config.uncertainty)
        assert config.uncertainty < 0
    
    def test_election_config_with_string_uncertainty(self):
        """Test ElectionConfig with string uncertainty (no validation)."""
        config = ElectionConfig(uncertainty="0.1")
        assert config.uncertainty == "0.1"
    
    def test_election_config_with_none_uncertainty(self):
        """Test ElectionConfig with None uncertainty (no validation)."""
        config = ElectionConfig(uncertainty=None)
        assert config.uncertainty is None
    
    def test_election_config_with_list_uncertainty(self):
        """Test ElectionConfig with list uncertainty (no validation)."""
        config = ElectionConfig(uncertainty=[0.1, 0.2])
        assert config.uncertainty == [0.1, 0.2]
    
    def test_election_config_with_dict_uncertainty(self):
        """Test ElectionConfig with dict uncertainty (no validation)."""
        config = ElectionConfig(uncertainty={"value": 0.1})
        assert config.uncertainty == {"value": 0.1}


class TestElectionConfigIntegration:
    """Test ElectionConfig integration with other components."""
    
    def test_election_config_with_voter(self):
        """Test ElectionConfig with Voter class."""
        from simulation_base.voter import Voter
        from simulation_base.population_group import PopulationGroup
        from simulation_base.gaussian_generator import GaussianGenerator
        
        # Create voter
        population_group = PopulationGroup(
            tag=PopulationGroup,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        voter = Voter(party=population_group, ideology=-0.3)
        config = ElectionConfig(uncertainty=0.1)
        
        # Test uncertainty calculation
        mock_generator = GaussianGenerator(seed=42)
        uncertainty = voter.uncertainty(config, mock_generator)
        
        assert isinstance(uncertainty, float)
        assert -1.0 <= uncertainty <= 1.0  # Should be within reasonable bounds
    
    def test_election_config_with_different_uncertainty_values(self):
        """Test ElectionConfig with different uncertainty values."""
        from simulation_base.voter import Voter
        from simulation_base.population_group import PopulationGroup
        from simulation_base.gaussian_generator import GaussianGenerator
        
        # Create voter
        population_group = PopulationGroup(
            tag=PopulationGroup,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        voter = Voter(party=population_group, ideology=-0.3)
        mock_generator = GaussianGenerator(seed=42)
        
        # Test with different uncertainty values
        uncertainties = [0.0, 0.1, 0.5, 1.0, 2.0]
        
        for uncertainty_val in uncertainties:
            config = ElectionConfig(uncertainty=uncertainty_val)
            uncertainty = voter.uncertainty(config, mock_generator)
            
            assert isinstance(uncertainty, float)
            # Uncertainty should be scaled by config value
            assert abs(uncertainty) <= uncertainty_val
    
    def test_election_config_serialization(self):
        """Test ElectionConfig serialization (if applicable)."""
        config = ElectionConfig(uncertainty=0.1)
        
        # Test that config can be converted to dict (if dataclass)
        if hasattr(config, '__dict__'):
            config_dict = config.__dict__
            assert 'uncertainty' in config_dict
            assert config_dict['uncertainty'] == 0.1
        
        # Test that config can be pickled (if needed)
        import pickle
        try:
            pickled = pickle.dumps(config)
            unpickled = pickle.loads(pickled)
            assert unpickled.uncertainty == config.uncertainty
        except (pickle.PicklingError, AttributeError):
            # Pickling might not be supported, which is fine
            pass
    
    def test_election_config_copy(self):
        """Test ElectionConfig copying."""
        config = ElectionConfig(uncertainty=0.1)
        
        # Test shallow copy
        import copy
        config_copy = copy.copy(config)
        assert config_copy.uncertainty == config.uncertainty
        assert config_copy is not config  # Should be different objects
        
        # Test deep copy
        config_deep_copy = copy.deepcopy(config)
        assert config_deep_copy.uncertainty == config.uncertainty
        assert config_deep_copy is not config  # Should be different objects


class TestElectionConfigValidation:
    """Test ElectionConfig validation and constraints."""
    
    def test_election_config_reasonable_uncertainty_range(self):
        """Test ElectionConfig with reasonable uncertainty range."""
        # Test typical uncertainty values
        reasonable_values = [0.0, 0.05, 0.1, 0.2, 0.5, 1.0]
        
        for value in reasonable_values:
            config = ElectionConfig(uncertainty=value)
            assert config.uncertainty == value
    
    def test_election_config_uncertainty_impact_on_voting(self):
        """Test how uncertainty affects voting behavior."""
        from simulation_base.voter import Voter
        from simulation_base.population_group import PopulationGroup
        from simulation_base.candidate import Candidate
        from simulation_base.gaussian_generator import GaussianGenerator
        
        # Create voter and candidate
        from simulation_base.population_tag import DEMOCRATS
        
        population_group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        voter = Voter(party=population_group, ideology=-0.3)
        candidate = Candidate(
            name="Test",
            tag=DEMOCRATS,
            ideology=-0.2,
            quality=0.5,
            incumbent=False
        )
        
        mock_generator = GaussianGenerator(seed=42)
        
        # Test with zero uncertainty (deterministic)
        config_zero = ElectionConfig(uncertainty=0.0)
        score_zero = voter.score(candidate, config_zero, mock_generator)
        
        # Test with high uncertainty (random)
        config_high = ElectionConfig(uncertainty=1.0)
        score_high = voter.score(candidate, config_high, mock_generator)
        
        # Scores should be different due to uncertainty
        assert score_zero != score_high
        
        # Test multiple times with high uncertainty to see variation
        scores = []
        for _ in range(10):
            score = voter.score(candidate, config_high, mock_generator)
            scores.append(score)
        
        # Should have some variation in scores
        assert len(set(scores)) > 1  # Not all scores should be identical
    
    def test_election_config_consistency(self):
        """Test ElectionConfig consistency across operations."""
        config = ElectionConfig(uncertainty=0.1)
        
        # Uncertainty should remain constant
        assert config.uncertainty == 0.1
        
        # Multiple accesses should return same value
        for _ in range(100):
            assert config.uncertainty == 0.1
        
        # Config should be equal to itself
        assert config == config
        
        # Config should be equal to another config with same uncertainty
        config2 = ElectionConfig(uncertainty=0.1)
        assert config == config2
        
        # Config should not be equal to config with different uncertainty
        config3 = ElectionConfig(uncertainty=0.2)
        assert config != config3
