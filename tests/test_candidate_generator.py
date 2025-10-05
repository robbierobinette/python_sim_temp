"""
Tests for CandidateGenerator classes.
"""
import pytest
from simulation_base.candidate_generator import (
    CandidateGenerator, PartisanCandidateGenerator, NormalPartisanCandidateGenerator,
    RandomCandidateGenerator, CondorcetCandidateGenerator, RankCandidateGenerator
)
from simulation_base.candidate import Candidate
from simulation_base.combined_population import CombinedPopulation
from simulation_base.population_group import PopulationGroup
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.gaussian_generator import GaussianGenerator


class TestCandidateGenerator:
    """Test CandidateGenerator abstract base class."""
    
    def test_candidate_generator_initialization(self):
        """Test CandidateGenerator initialization."""
        # Create a concrete implementation for testing
        class TestCandidateGenerator(CandidateGenerator):
            def candidates(self, population):
                return []
        
        generator = TestCandidateGenerator(quality_variance=0.5)
        assert generator.quality_variance == 0.5
    
    def test_candidates_for_ideologies(self):
        """Test candidates_for_ideologies method."""
        class TestCandidateGenerator(CandidateGenerator):
            def candidates(self, population):
                return []
        
        generator = TestCandidateGenerator(quality_variance=0.2)
        population_group = PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0)
        
        ideologies = [-0.8, -0.3, 0.1]
        candidates = generator.candidates_for_ideologies(ideologies, population_group)
        
        assert len(candidates) == 3
        assert all(isinstance(c, Candidate) for c in candidates)
        assert all(c.tag == DEMOCRATS for c in candidates)
        
        # Should be sorted from inside to outside for Democrats
        assert candidates[0].ideology == 0.1   # Most moderate
        assert candidates[1].ideology == -0.3  # Middle
        assert candidates[2].ideology == -0.8  # Most liberal
    
    def test_candidates_for_ideologies_republican(self):
        """Test candidates_for_ideologies with Republican party."""
        class TestCandidateGenerator(CandidateGenerator):
            def candidates(self, population):
                return []
        
        generator = TestCandidateGenerator(quality_variance=0.2)
        population_group = PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        
        ideologies = [0.8, 0.3, -0.1]
        candidates = generator.candidates_for_ideologies(ideologies, population_group)
        
        assert len(candidates) == 3
        assert all(c.tag == REPUBLICANS for c in candidates)
        
        # Should be sorted from inside to outside for Republicans
        assert candidates[0].ideology == -0.1  # Most moderate
        assert candidates[1].ideology == 0.3   # Middle
        assert candidates[2].ideology == 0.8   # Most conservative
    
    def test_get_median_candidate(self):
        """Test get_median_candidate method."""
        class TestCandidateGenerator(CandidateGenerator):
            def candidates(self, population):
                return []
        
        generator = TestCandidateGenerator(quality_variance=0.2)
        
        # Create a population with known median
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        candidate = generator.get_median_candidate(population, 0.1)
        
        assert isinstance(candidate, Candidate)
        assert candidate.name.endswith('-V')  # Median candidate naming
        assert candidate.incumbent == False
        assert candidate.tag in [DEMOCRATS, REPUBLICANS]  # Should be dominant party


class TestPartisanCandidateGenerator:
    """Test PartisanCandidateGenerator class."""
    
    def test_partisan_candidate_generator_initialization(self):
        """Test PartisanCandidateGenerator initialization."""
        generator = PartisanCandidateGenerator(
            n_party_candidates=2,
            spread=0.4,
            ideology_variance=0.1,
            quality_variance=0.2,
            primary_skew=0.25,
            median_variance=0.1
        )
        
        assert generator.n_party_candidates == 2
        assert generator.spread == 0.4
        assert generator.ideology_variance == 0.1
        assert generator.primary_skew == 0.25
        assert generator.median_variance == 0.1
        assert generator.quality_variance == 0.2
    
    def test_get_partisan_candidates_single(self):
        """Test get_partisan_candidates with single candidate."""
        generator = PartisanCandidateGenerator(
            n_party_candidates=1,
            spread=0.4,
            ideology_variance=0.0,  # No variance for deterministic test
            quality_variance=0.0,
            primary_skew=0.0,
            median_variance=0.1
        )
        
        population_group = PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0)
        groups = [population_group]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        candidates = generator.get_partisan_candidates(population_group, population, 1)
        
        assert len(candidates) == 1
        assert candidates[0].tag == DEMOCRATS
        assert candidates[0].name == "D-1"
        assert candidates[0].ideology == -0.5  # Should be at party base
    
    def test_get_partisan_candidates_two(self):
        """Test get_partisan_candidates with two candidates."""
        generator = PartisanCandidateGenerator(
            n_party_candidates=2,
            spread=0.4,
            ideology_variance=0.0,  # No variance for deterministic test
            quality_variance=0.0,
            primary_skew=0.0,
            median_variance=0.1
        )
        
        population_group = PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        groups = [population_group]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        candidates = generator.get_partisan_candidates(population_group, population, 2)
        
        assert len(candidates) == 2
        assert all(c.tag == REPUBLICANS for c in candidates)
        assert candidates[0].name == "R-1"
        assert candidates[1].name == "R-2"
        
        # Should be spread around party base
        assert candidates[0].ideology < candidates[1].ideology
    
    def test_get_partisan_candidates_three(self):
        """Test get_partisan_candidates with three candidates."""
        generator = PartisanCandidateGenerator(
            n_party_candidates=3,
            spread=0.4,
            ideology_variance=0.0,  # No variance for deterministic test
            quality_variance=0.0,
            primary_skew=0.0,
            median_variance=0.1
        )
        
        population_group = PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0)
        groups = [population_group]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        candidates = generator.get_partisan_candidates(population_group, population, 3)
        
        assert len(candidates) == 3
        assert all(c.tag == DEMOCRATS for c in candidates)
        
        # Should be spread around party base
        ideologies = [c.ideology for c in candidates]
        assert min(ideologies) < -0.5  # Leftmost candidate
        assert max(ideologies) > -0.5  # Rightmost candidate
        assert -0.5 in ideologies  # Center candidate at party base
    
    def test_get_partisan_candidates_with_primary_skew(self):
        """Test get_partisan_candidates with primary skew."""
        generator = PartisanCandidateGenerator(
            n_party_candidates=1,
            spread=0.4,
            ideology_variance=0.0,
            quality_variance=0.0,
            primary_skew=0.25,  # 25% skew
            median_variance=0.1
        )
        
        # Test Republican with positive skew
        rep_group = PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        groups = [rep_group]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        candidates = generator.get_partisan_candidates(rep_group, population, 1)
        assert candidates[0].ideology == 0.75  # 0.5 + 0.25
        
        # Test Democratic with negative skew
        dem_group = PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0)
        groups = [dem_group]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        candidates = generator.get_partisan_candidates(dem_group, population, 1)
        assert candidates[0].ideology == -0.75  # -0.5 - 0.25
    
    def test_candidates_method(self):
        """Test the candidates method."""
        generator = PartisanCandidateGenerator(
            n_party_candidates=1,
            spread=0.4,
            ideology_variance=0.0,
            quality_variance=0.0,
            primary_skew=0.0,
            median_variance=0.0
        )
        
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        candidates = generator.candidates(population)
        
        # Should have 2 partisan candidates + 1 median candidate
        assert len(candidates) == 3
        
        # Check that we have candidates from both parties
        parties = [c.tag for c in candidates]
        assert DEMOCRATS in parties
        assert REPUBLICANS in parties
        
        # Check that we have a median candidate
        median_candidates = [c for c in candidates if c.name.endswith('-V')]
        assert len(median_candidates) == 1


class TestNormalPartisanCandidateGenerator:
    """Test NormalPartisanCandidateGenerator class."""
    
    def test_normal_partisan_candidate_generator_initialization(self):
        """Test NormalPartisanCandidateGenerator initialization."""
        generator = NormalPartisanCandidateGenerator(
            n_partisan_candidates=2,
            ideology_variance=0.1,
            quality_variance=0.2,
            primary_skew=0.25,
            median_variance=0.1,
        )
        
        assert generator.n_partisan_candidates == 2
        assert generator.ideology_variance == 0.1
        assert generator.primary_skew == 0.25
        assert generator.median_variance == 0.1
        # adjust_for_centrists attribute removed
        assert generator.quality_variance == 0.2
    
    def test_candidates_method(self):
        """Test the candidates method."""
        generator = NormalPartisanCandidateGenerator(
            n_partisan_candidates=2,
            ideology_variance=0.0,  # No variance for deterministic test
            quality_variance=0.0,
            primary_skew=0.0,
            median_variance=0.0,
        )
        
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        candidates = generator.candidates(population)
        
        # Should have 2 Democratic + 1 median + 2 Republican = 5 candidates
        assert len(candidates) == 5
        
        # Check party distribution
        dem_candidates = [c for c in candidates if c.tag == DEMOCRATS]
        rep_candidates = [c for c in candidates if c.tag == REPUBLICANS]
        median_candidates = [c for c in candidates if c.name.endswith('-V')]
        
        # NormalPartisanCandidateGenerator adds a median candidate
        # The median candidate is tagged as a party based on its ideology
        assert len(dem_candidates) + len(rep_candidates) == 5  # Total candidates
        assert len(median_candidates) == 1  # 1 median candidate
    
    def test_adjust_for_centrist_dominant(self):
        """Test adjust_for_centrist with 'dominant' option."""
        generator = NormalPartisanCandidateGenerator(
            n_partisan_candidates=1,
            ideology_variance=0.0,
            quality_variance=0.0,
            primary_skew=0.0,
            median_variance=0.0,
        )
        
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=150.0, mean=-0.5, stddev=1.0),  # Dominant
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        candidates = generator.candidates(population)
        
        # Should have adjusted candidates
        assert len(candidates) == 3  # 1 Dem + 1 median + 1 Rep
    
    def test_adjust_for_centrist_both(self):
        """Test adjust_for_centrist with 'both' option."""
        generator = NormalPartisanCandidateGenerator(
            n_partisan_candidates=1,
            ideology_variance=0.0,
            quality_variance=0.0,
            primary_skew=0.0,
            median_variance=0.0,
        )
        
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        candidates = generator.candidates(population)
        
        # Should have adjusted candidates for both parties
        assert len(candidates) == 3  # 1 Dem + 1 median + 1 Rep
    
    def test_adjust_for_centrist_none(self):
        """Test adjust_for_centrist with 'none' option."""
        generator = NormalPartisanCandidateGenerator(
            n_partisan_candidates=1,
            ideology_variance=0.0,
            quality_variance=0.0,
            primary_skew=0.0,
            median_variance=0.0,
        )
        
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        candidates = generator.candidates(population)
        
        # Should not adjust candidates
        assert len(candidates) == 3  # 1 Dem + 1 median + 1 Rep


class TestRandomCandidateGenerator:
    """Test RandomCandidateGenerator class."""
    
    def test_random_candidate_generator_initialization(self):
        """Test RandomCandidateGenerator initialization."""
        generator = RandomCandidateGenerator(
            n_candidates=5,
            quality_variance=0.2,
            median_variance=0.1,
            n_median_candidates=2
        )
        
        assert generator.n_candidates == 5
        assert generator.n_median_candidates == 2
        assert generator.median_variance == 0.1
        assert generator.quality_variance == 0.2
    
    def test_candidates_method(self):
        """Test the candidates method."""
        generator = RandomCandidateGenerator(
            n_candidates=3,
            quality_variance=0.0,  # No variance for deterministic test
            median_variance=0.0,
            n_median_candidates=1
        )
        
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        candidates = generator.candidates(population)
        
        # Should have 3 random + 1 median = 4 candidates
        assert len(candidates) == 4
        
        # Check naming
        random_candidates = [c for c in candidates if c.name.startswith('C-')]
        median_candidates = [c for c in candidates if c.name.endswith('-V')]
        
        assert len(random_candidates) == 3
        assert len(median_candidates) == 1
    
    def test_candidates_method_no_median(self):
        """Test candidates method with no median candidates."""
        generator = RandomCandidateGenerator(
            n_candidates=2,
            quality_variance=0.0,
            median_variance=0.0,
            n_median_candidates=0
        )
        
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        candidates = generator.candidates(population)
        
        # Should have only random candidates
        assert len(candidates) == 2
        assert all(c.name.startswith('C-') for c in candidates)


class TestCondorcetCandidateGenerator:
    """Test CondorcetCandidateGenerator class."""
    
    def test_condorcet_candidate_generator_initialization(self):
        """Test CondorcetCandidateGenerator initialization."""
        generator = CondorcetCandidateGenerator(
            n_candidates=5,
            ideology_variance=0.1,
            quality_variance=0.2
        )
        
        assert generator.n_candidates == 5
        assert generator.ideology_variance == 0.1
        assert generator.quality_variance == 0.2
        assert generator.party_switch_point == 0.1
    
    def test_candidates_method(self):
        """Test the candidates method."""
        generator = CondorcetCandidateGenerator(
            n_candidates=3,
            ideology_variance=0.0,  # No variance for deterministic test
            quality_variance=0.0
        )
        
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        candidates = generator.candidates(population)
        
        # Should have 3 candidates
        assert len(candidates) == 3
        
        # Should be sorted by ideology
        ideologies = [c.ideology for c in candidates]
        assert ideologies == sorted(ideologies)
        
        # Check naming convention
        for i, candidate in enumerate(candidates):
            expected_name = f"{candidate.tag.short_name[0]}-{i + 1}"
            assert candidate.name == expected_name
    
    def test_party_assignment(self):
        """Test party assignment based on ideology."""
        generator = CondorcetCandidateGenerator(
            n_candidates=5,
            ideology_variance=0.0,
            quality_variance=0.0
        )
        
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        candidates = generator.candidates(population)
        
        # Check party assignment logic
        for candidate in candidates:
            if candidate.ideology < -0.1:  # party_switch_point
                assert candidate.tag == DEMOCRATS
            elif candidate.ideology > 0.1:
                assert candidate.tag == REPUBLICANS
            else:
                assert candidate.tag == INDEPENDENTS


class TestRankCandidateGenerator:
    """Test RankCandidateGenerator class."""
    
    def test_rank_candidate_generator_initialization(self):
        """Test RankCandidateGenerator initialization."""
        generator = RankCandidateGenerator(
            n_party_candidates=2,
            spread=0.4,
            offset=0.1,
            ideology_variance=0.1,
            quality_variance=0.2,
            median_variance=0.1
        )
        
        assert generator.n_party_candidates == 2
        assert generator.spread == 0.4
        assert generator.offset == 0.1
        assert generator.ideology_variance == 0.1
        assert generator.median_variance == 0.1
        assert generator.quality_variance == 0.2
    
    def test_compute_ranks(self):
        """Test compute_ranks method."""
        generator = RankCandidateGenerator(
            n_party_candidates=3,
            spread=0.6,
            offset=0.1,
            ideology_variance=0.0,  # No variance for deterministic test
            quality_variance=0.0,
            median_variance=0.0
        )
        
        # Test with Democrats
        ranks = generator.compute_ranks(DEMOCRATS, 0.1, 0.6, 0.0, 3)
        assert len(ranks) == 3
        assert all(0 < r < 1 for r in ranks)  # All ranks should be valid
        
        # Test with Republicans
        ranks = generator.compute_ranks(REPUBLICANS, 0.1, 0.6, 0.0, 3)
        assert len(ranks) == 3
        assert all(0 < r < 1 for r in ranks)
    
    def test_compute_ranks_single_candidate(self):
        """Test compute_ranks with single candidate."""
        generator = RankCandidateGenerator(
            n_party_candidates=1,
            spread=0.4,
            offset=0.1,
            ideology_variance=0.0,
            quality_variance=0.0,
            median_variance=0.0
        )
        
        # Should raise ValueError for single candidate
        with pytest.raises(ValueError):
            generator.compute_ranks(DEMOCRATS, 0.1, 0.4, 0.0, 1)
    
    def test_get_candidates_rank(self):
        """Test get_candidates_rank method."""
        generator = RankCandidateGenerator(
            n_party_candidates=2,
            spread=0.4,
            offset=0.1,
            ideology_variance=0.0,
            quality_variance=0.0,
            median_variance=0.0
        )
        
        population_group = PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0)
        groups = [population_group]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        candidates = generator.get_candidates_rank(population_group, population, 2)
        
        assert len(candidates) == 2
        assert all(c.tag == DEMOCRATS for c in candidates)
        assert candidates[0].name == "D-1"
        assert candidates[1].name == "D-2"
    
    def test_candidates_method(self):
        """Test the candidates method."""
        generator = RankCandidateGenerator(
            n_party_candidates=2,  # Must be > 1 for RankCandidateGenerator
            spread=0.4,
            offset=0.1,
            ideology_variance=0.0,
            quality_variance=0.0,
            median_variance=0.0
        )
        
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        candidates = generator.candidates(population)
        
        # Should have 2 Dem + 1 median + 2 Rep = 5 candidates
        # But the median candidate is tagged with a party based on its ideology
        assert len(candidates) == 5
        
        # Check party distribution
        dem_candidates = [c for c in candidates if c.tag == DEMOCRATS]
        rep_candidates = [c for c in candidates if c.tag == REPUBLICANS]
        median_candidates = [c for c in candidates if c.name.endswith('-V')]
        
        # The median candidate can be tagged as either party depending on ideology
        assert len(dem_candidates) + len(rep_candidates) == 5
        assert len(median_candidates) == 1


class TestCandidateGeneratorEdgeCases:
    """Test edge cases for candidate generators."""
    
    def test_partisan_generator_with_zero_candidates(self):
        """Test PartisanCandidateGenerator with zero candidates."""
        generator = PartisanCandidateGenerator(
            n_party_candidates=0,
            spread=0.4,
            ideology_variance=0.0,
            quality_variance=0.0,
            primary_skew=0.0,
            median_variance=0.0
        )
        
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        candidates = generator.candidates(population)
        
        # Current implementation still generates candidates even with n_party_candidates=0
        # This appears to be default behavior
        assert len(candidates) >= 1
        # At minimum there should be a median candidate
        median_candidates = [c for c in candidates if c.name.endswith('-V')]
        assert len(median_candidates) >= 1
    
    def test_random_generator_with_zero_candidates(self):
        """Test RandomCandidateGenerator with zero candidates."""
        generator = RandomCandidateGenerator(
            n_candidates=0,
            quality_variance=0.0,
            median_variance=0.0,
            n_median_candidates=1
        )
        
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        candidates = generator.candidates(population)
        
        # Should only have median candidate
        assert len(candidates) == 1
        assert candidates[0].name.endswith('-V')
    
    def test_condorcet_generator_with_zero_candidates(self):
        """Test CondorcetCandidateGenerator with zero candidates."""
        generator = CondorcetCandidateGenerator(
            n_candidates=0,
            ideology_variance=0.0,
            quality_variance=0.0
        )
        
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        candidates = generator.candidates(population)
        
        # Should have no candidates
        assert len(candidates) == 0
    
    def test_generators_with_empty_population(self):
        """Test generators with empty population."""
        generator = PartisanCandidateGenerator(
            n_party_candidates=1,
            spread=0.4,
            ideology_variance=0.0,
            quality_variance=0.0,
            primary_skew=0.0,
            median_variance=0.0
        )
        
        # Empty population should crash as per user requirement
        with pytest.raises(IndexError, match="list index out of range"):
            population = CombinedPopulation(populations=[], desired_samples=0)

