"""
Tests for GaussianGenerator class.
"""
import pytest
import math
from simulation_base.gaussian_generator import GaussianGenerator, next_gaussian, set_seed


class TestGaussianGenerator:
    """Test GaussianGenerator class functionality."""
    
    def test_gaussian_generator_initialization(self):
        """Test GaussianGenerator initialization."""
        # Test with no seed
        generator = GaussianGenerator()
        assert hasattr(generator, '_random')
        
        # Test with seed
        generator = GaussianGenerator(seed=42)
        assert hasattr(generator, '_random')
    
    def test_gaussian_generator_set_seed(self):
        """Test set_seed method."""
        generator = GaussianGenerator()
        generator.set_seed(123)
        
        # Should not raise an error
        assert True
    
    def test_gaussian_generator_next_boolean(self):
        """Test next_boolean method."""
        generator = GaussianGenerator(seed=42)
        
        # Test multiple calls
        booleans = [generator.next_boolean() for _ in range(100)]
        
        # Should return booleans
        assert all(isinstance(b, bool) for b in booleans)
        
        # Should have some variation (not all True or all False)
        assert any(b for b in booleans)  # At least one True
        assert any(not b for b in booleans)  # At least one False
    
    def test_gaussian_generator_next_int(self):
        """Test next_int method."""
        generator = GaussianGenerator(seed=42)
        
        # Test multiple calls
        integers = [generator.next_int() for _ in range(100)]
        
        # Should return integers
        assert all(isinstance(i, int) for i in integers)
        
        # Should be within expected range
        for i in integers:
            assert -2**31 <= i <= 2**31 - 1
    
    def test_gaussian_generator_call(self):
        """Test __call__ method."""
        generator = GaussianGenerator(seed=42)
        
        # Test multiple calls
        values = [generator() for _ in range(1000)]
        
        # Should return floats
        assert all(isinstance(v, float) for v in values)
        
        # Should have some variation
        assert len(set(values)) > 1  # Not all values should be identical
        
        # Should be roughly normally distributed
        mean = sum(values) / len(values)
        assert abs(mean) < 0.5  # Mean should be close to 0
        
        # Standard deviation should be close to 1
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        stddev = math.sqrt(variance)
        assert 0.8 < stddev < 1.2  # Should be close to 1
    
    def test_gaussian_generator_deterministic_with_seed(self):
        """Test that GaussianGenerator is deterministic with same seed."""
        generator1 = GaussianGenerator(seed=42)
        generator2 = GaussianGenerator(seed=42)
        
        # Should produce same sequence
        values1 = [generator1() for _ in range(10)]
        values2 = [generator2() for _ in range(10)]
        
        assert values1 == values2
    
    def test_gaussian_generator_different_seeds(self):
        """Test that different seeds produce different sequences."""
        generator1 = GaussianGenerator(seed=42)
        generator2 = GaussianGenerator(seed=123)
        
        # Should produce different sequences
        values1 = [generator1() for _ in range(10)]
        values2 = [generator2() for _ in range(10)]
        
        assert values1 != values2
    
    def test_gaussian_generator_set_seed_changes_sequence(self):
        """Test that set_seed changes the sequence."""
        generator = GaussianGenerator(seed=42)
        
        # Get first sequence
        values1 = [generator() for _ in range(5)]
        
        # Change seed
        generator.set_seed(123)
        
        # Get second sequence
        values2 = [generator() for _ in range(5)]
        
        # Should be different
        assert values1 != values2
        
        # Reset to original seed
        generator.set_seed(42)
        
        # Should produce original sequence again
        values3 = [generator() for _ in range(5)]
        assert values1 == values3


class TestGaussianGeneratorEdgeCases:
    """Test edge cases for GaussianGenerator."""
    
    def test_gaussian_generator_with_zero_seed(self):
        """Test GaussianGenerator with zero seed."""
        generator = GaussianGenerator(seed=0)
        
        # Should work fine
        value = generator()
        assert isinstance(value, float)
    
    def test_gaussian_generator_with_negative_seed(self):
        """Test GaussianGenerator with negative seed."""
        generator = GaussianGenerator(seed=-42)
        
        # Should work fine
        value = generator()
        assert isinstance(value, float)
    
    def test_gaussian_generator_with_large_seed(self):
        """Test GaussianGenerator with large seed."""
        generator = GaussianGenerator(seed=2**31 - 1)
        
        # Should work fine
        value = generator()
        assert isinstance(value, float)
    
    def test_gaussian_generator_with_very_large_seed(self):
        """Test GaussianGenerator with very large seed."""
        generator = GaussianGenerator(seed=2**63 - 1)
        
        # Should work fine
        value = generator()
        assert isinstance(value, float)
    
    def test_gaussian_generator_with_none_seed(self):
        """Test GaussianGenerator with None seed."""
        generator = GaussianGenerator(seed=None)
        
        # Should work fine (uses default random seed)
        value = generator()
        assert isinstance(value, float)
    
    def test_gaussian_generator_extreme_values(self):
        """Test GaussianGenerator with extreme values."""
        generator = GaussianGenerator(seed=42)
        
        # Generate many values to check for extreme cases
        values = [generator() for _ in range(10000)]
        
        # Should not produce infinite values
        assert all(math.isfinite(v) for v in values)
        
        # Should not produce NaN values
        assert not any(math.isnan(v) for v in values)
        
        # Most values should be within reasonable bounds
        # (99.7% should be within 3 standard deviations)
        within_bounds = sum(1 for v in values if -3 <= v <= 3)
        assert within_bounds > 9900  # At least 99% should be within bounds
    
    def test_gaussian_generator_boolean_distribution(self):
        """Test that next_boolean produces roughly equal distribution."""
        generator = GaussianGenerator(seed=42)
        
        # Generate many booleans
        booleans = [generator.next_boolean() for _ in range(10000)]
        
        # Should be roughly 50/50
        true_count = sum(booleans)
        false_count = len(booleans) - true_count
        
        # Should be roughly equal (within 5%)
        assert 4500 <= true_count <= 5500
        assert 4500 <= false_count <= 5500
    
    def test_gaussian_generator_int_distribution(self):
        """Test that next_int produces reasonable distribution."""
        generator = GaussianGenerator(seed=42)
        
        # Generate many integers
        integers = [generator.next_int() for _ in range(10000)]
        
        # Should have variation
        assert len(set(integers)) > 100  # Should have many different values
        
        # Should be within bounds
        assert all(-2**31 <= i <= 2**31 - 1 for i in integers)
        
        # Should have both positive and negative values
        assert any(i > 0 for i in integers)
        assert any(i < 0 for i in integers)
        # Zero may or may not appear in the distribution


class TestGlobalGaussianGenerator:
    """Test global GaussianGenerator functions."""
    
    def test_next_gaussian_function(self):
        """Test next_gaussian function."""
        # Test multiple calls
        values = [next_gaussian() for _ in range(100)]
        
        # Should return floats
        assert all(isinstance(v, float) for v in values)
        
        # Should have some variation
        assert len(set(values)) > 1
    
    def test_set_seed_function(self):
        """Test set_seed function."""
        # Should not raise an error
        set_seed(42)
        
        # Should affect next_gaussian
        values1 = [next_gaussian() for _ in range(10)]
        
        set_seed(42)
        values2 = [next_gaussian() for _ in range(10)]
        
        # Should be the same with same seed
        assert values1 == values2
        
        # Should be different with different seed
        set_seed(123)
        values3 = [next_gaussian() for _ in range(10)]
        assert values1 != values3
    
    def test_global_generator_consistency(self):
        """Test that global generator is consistent."""
        # Set seed
        set_seed(42)
        
        # Get sequence
        values1 = [next_gaussian() for _ in range(10)]
        
        # Reset seed
        set_seed(42)
        
        # Get sequence again
        values2 = [next_gaussian() for _ in range(10)]
        
        # Should be identical
        assert values1 == values2
    
    def test_global_generator_independence(self):
        """Test that global generator is independent of instance generators."""
        # Set global seed
        set_seed(42)
        global_values = [next_gaussian() for _ in range(5)]
        
        # Create instance generator with different seed
        instance_generator = GaussianGenerator(seed=123)
        instance_values = [instance_generator() for _ in range(5)]
        
        # Should be different
        assert global_values != instance_values
        
        # Global generator should still be at same state
        set_seed(42)
        global_values2 = [next_gaussian() for _ in range(5)]
        assert global_values == global_values2


class TestGaussianGeneratorIntegration:
    """Test GaussianGenerator integration with other components."""
    
    def test_gaussian_generator_with_voter(self):
        """Test GaussianGenerator with Voter class."""
        from simulation_base.voter import Voter
        from simulation_base.population_group import PopulationGroup
        from simulation_base.election_config import ElectionConfig
        
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
        
        # Test with instance generator
        generator = GaussianGenerator(seed=42)
        uncertainty = voter.uncertainty(config, generator)
        
        assert isinstance(uncertainty, float)
        assert -1.0 <= uncertainty <= 1.0
        
        # Test with global generator
        set_seed(42)
        uncertainty_global = voter.uncertainty(config)
        
        # Should be different (different generators)
        assert uncertainty != uncertainty_global
    
    def test_gaussian_generator_with_ballot(self):
        """Test GaussianGenerator with RCVBallot class."""
        from simulation_base.ballot import RCVBallot, CandidateScore
        from simulation_base.candidate import Candidate
        
        # Create candidates
        from simulation_base.population_tag import DEMOCRATS, REPUBLICANS
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create candidate scores
        candidate_scores = [
            CandidateScore(candidate=candidates[0], score=0.8),
            CandidateScore(candidate=candidates[1], score=0.6)
        ]
        
        # Test with instance generator
        generator = GaussianGenerator(seed=42)
        ballot = RCVBallot(unsorted_candidates=candidate_scores, gaussian_generator=generator)
        
        assert ballot.gaussian_generator == generator
        
        # Test with global generator (default)
        ballot2 = RCVBallot(unsorted_candidates=candidate_scores)
        
        assert ballot2.gaussian_generator is not None
        assert isinstance(ballot2.gaussian_generator, GaussianGenerator)
    
    def test_gaussian_generator_with_candidate_generator(self):
        """Test GaussianGenerator with candidate generators."""
        from simulation_base.candidate_generator import PartisanCandidateGenerator
        from simulation_base.combined_population import CombinedPopulation
        from simulation_base.population_group import PopulationGroup
        
        # Create population
        from simulation_base.population_tag import DEMOCRATS, REPUBLICANS
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Test with instance generator
        generator = GaussianGenerator(seed=42)
        candidate_generator = PartisanCandidateGenerator(
            n_party_candidates=2,
            spread=0.4,
            ideology_variance=0.1,
            quality_variance=0.2,
            primary_skew=0.25,
            median_variance=0.1,
            gaussian_generator=generator
        )
        
        candidates = candidate_generator.candidates(population)
        
        from simulation_base.candidate import Candidate
        assert len(candidates) > 0
        assert all(isinstance(c, Candidate) for c in candidates)
    
    def test_gaussian_generator_deterministic_simulation(self):
        """Test that GaussianGenerator enables deterministic simulations."""
        from simulation_base.voter import Voter
        from simulation_base.population_group import PopulationGroup
        from simulation_base.election_config import ElectionConfig
        from simulation_base.candidate import Candidate
        from simulation_base.ballot import RCVBallot, CandidateScore
        
        # Create components
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
        config = ElectionConfig(uncertainty=0.1)
        
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=DEMOCRATS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Run simulation with same seed
        generator1 = GaussianGenerator(seed=42)
        ballot1 = voter.ballot(candidates, config, generator1)
        
        generator2 = GaussianGenerator(seed=42)
        ballot2 = voter.ballot(candidates, config, generator2)
        
        # Should produce same results
        assert len(ballot1.sorted_candidates) == len(ballot2.sorted_candidates)
        
        # Scores should be the same
        for cs1, cs2 in zip(ballot1.sorted_candidates, ballot2.sorted_candidates):
            assert cs1.score == cs2.score
            assert cs1.candidate == cs2.candidate
    
    def test_gaussian_generator_performance(self):
        """Test GaussianGenerator performance."""
        generator = GaussianGenerator(seed=42)
        
        # Generate many values quickly
        import time
        
        start_time = time.time()
        values = [generator() for _ in range(100000)]
        end_time = time.time()
        
        # Should be fast (less than 1 second for 100k values)
        assert end_time - start_time < 1.0
        
        # Should have good distribution
        mean = sum(values) / len(values)
        assert abs(mean) < 0.01  # Mean should be very close to 0
        
        # Standard deviation should be close to 1
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        stddev = math.sqrt(variance)
        assert 0.99 < stddev < 1.01  # Should be very close to 1
