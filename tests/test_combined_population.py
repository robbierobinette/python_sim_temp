"""
Tests for CombinedPopulation class.
"""
import pytest
import random
from simulation_base.combined_population import CombinedPopulation
from simulation_base.population_group import PopulationGroup
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.voter import Voter
from simulation_base.gaussian_generator import GaussianGenerator


class TestCombinedPopulation:
    """Test CombinedPopulation class functionality."""
    
    def test_combined_population_creation(self):
        """Test creating a CombinedPopulation."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        assert population.populations == groups
        assert population.desired_samples == 100
        assert hasattr(population, 'party_map')
        assert hasattr(population, 'summed_weight')
        assert hasattr(population, 'sample_population')
        assert hasattr(population, 'median_voter')
    
    def test_combined_population_defaults(self):
        """Test CombinedPopulation with default values."""
        groups = [PopulationGroup(tag=DEMOCRATS, weight=100.0)]
        population = CombinedPopulation(populations=groups)
        
        assert population.desired_samples == 1000
        assert population.populations == groups
    
    def test_party_map_initialization(self):
        """Test that party_map is correctly initialized."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        assert population.party_map[DEMOCRATS] == groups[0]
        assert population.party_map[REPUBLICANS] == groups[1]
        assert population.party_map[INDEPENDENTS] == groups[2]
    
    def test_summed_weight_calculation(self):
        """Test that summed_weight is correctly calculated."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=150.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        assert population.summed_weight == 300.0  # 100 + 150 + 50
    
    def test_sample_population_generation(self):
        """Test that sample_population is correctly generated."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        assert len(population.sample_population) == 100
        assert all(isinstance(voter, Voter) for voter in population.sample_population)
        
        # Check that voters are sorted by ideology
        ideologies = [voter.ideology for voter in population.sample_population]
        assert ideologies == sorted(ideologies)
    
    def test_median_voter_calculation(self):
        """Test that median_voter is correctly calculated."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Median should be the ideology of the middle voter
        middle_idx = len(population.sample_population) // 2
        expected_median = population.sample_population[middle_idx].ideology
        assert population.median_voter == expected_median
    
    def test_n_samples_property(self):
        """Test the n_samples property."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=50)
        
        assert population.n_samples == 50
        assert population.n_samples == len(population.sample_population)
    
    def test_voters_property(self):
        """Test the voters property."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=50)
        
        assert population.voters == population.sample_population
        assert len(population.voters) == 50
    
    def test_dominant_party(self):
        """Test the dominant_party method."""
        # Test with Democrats dominant
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=150.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        dominant = population.dominant_party()
        assert dominant == DEMOCRATS
        
        # Test with Republicans dominant
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=150.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        dominant = population.dominant_party()
        assert dominant == REPUBLICANS
    
    def test_dominant_party_tie(self):
        """Test dominant_party method with tied weights."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # With tied weights, should return one of the tied parties
        dominant = population.dominant_party()
        assert dominant in [DEMOCRATS, REPUBLICANS]
    
    def test_stats_method(self):
        """Test the stats method."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=150.0, mean=0.5, stddev=1.5),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=0.5)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        stats = population.stats()
        
        # Should contain stats from all groups
        assert "Dem" in stats
        assert "Rep" in stats
        assert "Ind" in stats
    
    def test_getitem_method(self):
        """Test the __getitem__ method."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        assert population[DEMOCRATS] == groups[0]
        assert population[REPUBLICANS] == groups[1]
        assert population[INDEPENDENTS] == groups[2]
    
    def test_party_for_tag_method(self):
        """Test the party_for_tag method."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        assert population.party_for_tag(DEMOCRATS) == groups[0]
        assert population.party_for_tag(REPUBLICANS) == groups[1]
    
    def test_party_for_name_method(self):
        """Test the party_for_name method."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        assert population.party_for_name("Democratic") == groups[0]
        assert population.party_for_name("Republican") == groups[1]
        
        # Test with non-existent name
        with pytest.raises(KeyError):
            population.party_for_name("NonExistent")
    
    def test_tag_for_name_method(self):
        """Test the tag_for_name method."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        assert population.tag_for_name("Democratic") == DEMOCRATS
        assert population.tag_for_name("Republican") == REPUBLICANS
        
        # Test with non-existent name
        with pytest.raises(KeyError):
            population.tag_for_name("NonExistent")
    
    def test_percent_weight_method(self):
        """Test the percent_weight method."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=150.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Total weight is 300.0
        assert population.percent_weight(DEMOCRATS) == 100.0 / 300.0
        assert population.percent_weight(REPUBLICANS) == 150.0 / 300.0
        assert population.percent_weight(INDEPENDENTS) == 50.0 / 300.0
    
    def test_democrats_property(self):
        """Test the democrats property."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        assert population.democrats == groups[0]
        assert population.democrats.tag == DEMOCRATS
    
    def test_republicans_property(self):
        """Test the republicans property."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        assert population.republicans == groups[1]
        assert population.republicans.tag == REPUBLICANS
    
    def test_independents_property(self):
        """Test the independents property."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        assert population.independents == groups[1]
        assert population.independents.tag == INDEPENDENTS
    
    def test_ideology_for_percentile_method(self):
        """Test the ideology_for_percentile method."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Test 0th percentile (first voter)
        ideology_0 = population.ideology_for_percentile(0.0)
        assert ideology_0 == population.sample_population[0].ideology
        
        # Test 50th percentile (median)
        ideology_50 = population.ideology_for_percentile(0.5)
        assert ideology_50 == population.median_voter
        
        # Test 100th percentile (last voter)
        ideology_100 = population.ideology_for_percentile(1.0)
        assert ideology_100 == population.sample_population[-1].ideology
    
    def test_approximate_median_ideology_method(self):
        """Test the approximate_median_ideology method."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Calculate expected median
        total_weight = 250.0  # 100 + 100 + 50
        expected_median = (100.0 * -0.5 + 100.0 * 0.5 + 50.0 * 0.0) / total_weight
        expected_median = 0.0  # (100 * -0.5 + 100 * 0.5 + 50 * 0.0) / 250 = 0.0
        
        actual_median = population.approximate_median_ideology()
        assert abs(actual_median - expected_median) < 0.001
    
    def test_random_voter_method(self):
        """Test the random_voter method."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Test with default generator
        voter = population.random_voter()
        assert isinstance(voter, Voter)
        assert voter.party in groups
        
        # Test with custom generator
        mock_generator = GaussianGenerator(seed=42)
        voter_custom = population.random_voter(mock_generator)
        assert isinstance(voter_custom, Voter)
        assert voter_custom.party in groups


class TestCombinedPopulationEdgeCases:
    """Test edge cases for CombinedPopulation."""
    
    def test_combined_population_with_empty_groups(self):
        """Test CombinedPopulation with empty groups list."""
        # Empty population crashes on __post_init__ as per user requirement
        with pytest.raises(IndexError, match="list index out of range"):
            population = CombinedPopulation(populations=[], desired_samples=100)
    
    def test_combined_population_with_single_group(self):
        """Test CombinedPopulation with single group."""
        groups = [PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0)]
        population = CombinedPopulation(populations=groups, desired_samples=50)
        
        assert len(population.populations) == 1
        assert population.summed_weight == 100.0
        assert len(population.sample_population) == 50
        
        # All voters should be from the single group
        assert all(voter.party == groups[0] for voter in population.sample_population)
    
    def test_combined_population_with_zero_weights(self):
        """Test CombinedPopulation with zero weights."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=0.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=0.0, mean=0.5, stddev=1.0)
        ]
        
        # Zero weights cause division by zero in _population_sample
        with pytest.raises(ZeroDivisionError, match="float division by zero"):
            population = CombinedPopulation(populations=groups, desired_samples=100)
    
    def test_combined_population_with_negative_weights(self):
        """Test CombinedPopulation with negative weights."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=-100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        
        # Negative weights sum to zero, causing division by zero
        with pytest.raises(ZeroDivisionError, match="float division by zero"):
            population = CombinedPopulation(populations=groups, desired_samples=100)
    
    def test_combined_population_with_zero_samples(self):
        """Test CombinedPopulation with zero desired samples."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        
        # Zero samples crash on __post_init__ as per user requirement
        with pytest.raises(IndexError, match="list index out of range"):
            population = CombinedPopulation(populations=groups, desired_samples=0)
    
    def test_ideology_for_percentile_edge_cases(self):
        """Test ideology_for_percentile with edge cases."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Test with negative percentile (should clamp to 0)
        ideology_neg = population.ideology_for_percentile(-0.1)
        assert ideology_neg == population.sample_population[0].ideology
        
        # Test with percentile > 1 (should clamp to last)
        ideology_over = population.ideology_for_percentile(1.1)
        assert ideology_over == population.sample_population[-1].ideology
    
    def test_weighted_population_selection(self):
        """Test _weighted_population method with edge cases."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Test that weighted selection works
        selected_groups = []
        for _ in range(100):
            group = population._weighted_population()
            selected_groups.append(group)
        
        # Should select from both groups
        assert any(g.tag == DEMOCRATS for g in selected_groups)
        assert any(g.tag == REPUBLICANS for g in selected_groups)
    
    def test_weighted_population_with_zero_weight(self):
        """Test _weighted_population with zero total weight."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=0.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=0.0, mean=0.5, stddev=1.0)
        ]
        
        # Zero weights cause division by zero
        with pytest.raises(ZeroDivisionError, match="float division by zero"):
            population = CombinedPopulation(populations=groups, desired_samples=100)


class TestCombinedPopulationRandomness:
    """Test randomness aspects of CombinedPopulation."""
    
    def test_sample_population_randomness(self):
        """Test that sample_population produces different results."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        
        # Create two populations with same parameters
        population1 = CombinedPopulation(populations=groups, desired_samples=100)
        population2 = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Ideologies should be different (random)
        ideologies1 = [v.ideology for v in population1.sample_population]
        ideologies2 = [v.ideology for v in population2.sample_population]
        
        # Very unlikely to be identical
        assert ideologies1 != ideologies2
    
    def test_random_voter_randomness(self):
        """Test that random_voter produces different results."""
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Generate multiple voters
        voters = [population.random_voter() for _ in range(20)]
        
        # Should have voters from different groups
        parties = [v.party.tag for v in voters]
        assert len(set(parties)) > 1  # Should have multiple parties
        
        # Ideologies should be different
        ideologies = [v.ideology for v in voters]
        assert len(set(ideologies)) > 1  # Should have variation

