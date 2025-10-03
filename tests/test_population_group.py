"""
Tests for PopulationGroup class.
"""
import pytest
import random
from simulation_base.population_group import PopulationGroup
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.candidate import Candidate
from simulation_base.voter import Voter
from simulation_base.gaussian_generator import GaussianGenerator


class TestPopulationGroup:
    """Test PopulationGroup class functionality."""
    
    def test_population_group_creation(self):
        """Test creating a PopulationGroup."""
        group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        assert group.tag == DEMOCRATS
        assert group.party_bonus == 1.0
        assert group.mean == -0.5
        assert group.stddev == 1.0
        assert group.skew == 0.0
        assert group.weight == 100.0
    
    def test_population_group_defaults(self):
        """Test PopulationGroup with default values."""
        group = PopulationGroup(tag=REPUBLICANS)
        
        assert group.tag == REPUBLICANS
        assert group.party_bonus == 0.0
        assert group.mean == 0.0
        assert group.stddev == 15.0
        assert group.skew == 0.0
        assert group.weight == 100.0
    
    def test_plural_name_property(self):
        """Test the plural_name property."""
        group = PopulationGroup(tag=DEMOCRATS)
        assert group.plural_name == "Democrats"
        
        group = PopulationGroup(tag=REPUBLICANS)
        assert group.plural_name == "Republicans"
        
        group = PopulationGroup(tag=INDEPENDENTS)
        assert group.plural_name == "Independents"
    
    def test_name_property(self):
        """Test the name property."""
        group = PopulationGroup(tag=DEMOCRATS)
        assert group.name == "Democratic"
        
        group = PopulationGroup(tag=REPUBLICANS)
        assert group.name == "Republican"
        
        group = PopulationGroup(tag=INDEPENDENTS)
        assert group.name == "Independent"
    
    def test_stats_method(self):
        """Test the stats method."""
        group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        stats = group.stats()
        assert "Dem" in stats
        assert "100.00" in stats
        assert "-0.50" in stats
        assert "1.00" in stats
    
    def test_shift_out_method(self):
        """Test the shift_out method."""
        # Test Republican shift
        rep_group = PopulationGroup(
            tag=REPUBLICANS,
            party_bonus=1.0,
            mean=0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        shifted_rep = rep_group.shift_out(0.2)
        assert shifted_rep.mean == 0.7  # 0.5 + 0.2
        assert shifted_rep.tag == REPUBLICANS
        assert shifted_rep.stddev == 1.0
        assert shifted_rep.weight == 100.0
        
        # Test Democratic shift
        dem_group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        shifted_dem = dem_group.shift_out(0.2)
        assert shifted_dem.mean == -0.7  # -0.5 - 0.2
        assert shifted_dem.tag == DEMOCRATS
        assert shifted_dem.stddev == 1.0
        assert shifted_dem.weight == 100.0
        
        # Test Independent shift (should not change)
        ind_group = PopulationGroup(
            tag=INDEPENDENTS,
            party_bonus=0.5,
            mean=0.0,
            stddev=1.0,
            skew=0.0,
            weight=50.0
        )
        
        shifted_ind = ind_group.shift_out(0.2)
        assert shifted_ind.mean == 0.0  # Should not change
        assert shifted_ind.tag == INDEPENDENTS
        assert shifted_ind.stddev == 1.0
        assert shifted_ind.weight == 50.0
    
    def test_shift_method(self):
        """Test the shift method."""
        group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        shifted = group.shift(0.3)
        assert shifted.mean == -0.2  # -0.5 + 0.3
        assert shifted.tag == DEMOCRATS
        assert shifted.stddev == 1.0
        assert shifted.weight == 100.0
        
        # Test negative shift
        shifted_neg = group.shift(-0.3)
        assert shifted_neg.mean == -0.8  # -0.5 - 0.3
    
    def test_reweight_method(self):
        """Test the reweight method."""
        group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        reweighted = group.reweight(0.5)
        assert reweighted.weight == 50.0  # 100.0 * 0.5
        assert reweighted.tag == DEMOCRATS
        assert reweighted.mean == -0.5
        assert reweighted.stddev == 1.0
        
        # Test scale factor > 1
        reweighted_up = group.reweight(2.0)
        assert reweighted_up.weight == 200.0  # 100.0 * 2.0
    
    def test_party_bonus_for(self):
        """Test the party_bonus_for method."""
        group = PopulationGroup(tag=DEMOCRATS)
        
        # Test with different parties
        assert group.party_bonus_for(DEMOCRATS) == 1.0
        assert group.party_bonus_for(REPUBLICANS) == 0.0
        assert group.party_bonus_for(INDEPENDENTS) == 0.5
    
    def test_party_bonus_for_group(self):
        """Test the party_bonus_for_group method."""
        dem_group = PopulationGroup(tag=DEMOCRATS)
        rep_group = PopulationGroup(tag=REPUBLICANS)
        ind_group = PopulationGroup(tag=INDEPENDENTS)
        
        # Test with different groups
        assert dem_group.party_bonus_for_group(dem_group) == 1.0
        assert dem_group.party_bonus_for_group(rep_group) == 0.0
        assert dem_group.party_bonus_for_group(ind_group) == 0.5
    
    def test_population_sample(self):
        """Test the population_sample method."""
        group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        # Test with small sample
        voters = group.population_sample(10)
        assert len(voters) == 10
        assert all(isinstance(voter, Voter) for voter in voters)
        assert all(voter.party == group for voter in voters)
        
        # Test with larger sample
        voters_large = group.population_sample(100)
        assert len(voters_large) == 100
        
        # Test that ideologies are roughly centered around mean
        ideologies = [voter.ideology for voter in voters_large]
        mean_ideology = sum(ideologies) / len(ideologies)
        assert abs(mean_ideology - group.mean) < 0.5  # Should be close to group mean
    
    def test_random_voter(self):
        """Test the random_voter method."""
        group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        # Test with default generator
        voter = group.random_voter()
        assert isinstance(voter, Voter)
        assert voter.party == group
        
        # Test with custom generator
        mock_generator = GaussianGenerator(seed=42)
        voter_custom = group.random_voter(mock_generator)
        assert isinstance(voter_custom, Voter)
        assert voter_custom.party == group
    
    def test_random_candidate(self):
        """Test the random_candidate method."""
        group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        # Test with default generator
        candidate = group.random_candidate("Test", 0.1, 0.2)
        assert isinstance(candidate, Candidate)
        assert candidate.name == "Test"
        assert candidate.tag == group.tag
        assert candidate.incumbent == False
        
        # Test with custom generator
        mock_generator = GaussianGenerator(seed=42)
        candidate_custom = group.random_candidate("Custom", 0.1, 0.2, mock_generator)
        assert isinstance(candidate_custom, Candidate)
        assert candidate_custom.name == "Custom"
        assert candidate_custom.tag == group.tag


class TestPopulationGroupEdgeCases:
    """Test edge cases for PopulationGroup."""
    
    def test_population_group_with_extreme_values(self):
        """Test PopulationGroup with extreme values."""
        group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1000.0,
            mean=-1000.0,
            stddev=1000.0,
            skew=1000.0,
            weight=1000000.0
        )
        
        assert group.party_bonus == 1000.0
        assert group.mean == -1000.0
        assert group.stddev == 1000.0
        assert group.skew == 1000.0
        assert group.weight == 1000000.0
    
    def test_population_group_with_zero_values(self):
        """Test PopulationGroup with zero values."""
        group = PopulationGroup(
            tag=REPUBLICANS,
            party_bonus=0.0,
            mean=0.0,
            stddev=0.0,
            skew=0.0,
            weight=0.0
        )
        
        assert group.party_bonus == 0.0
        assert group.mean == 0.0
        assert group.stddev == 0.0
        assert group.skew == 0.0
        assert group.weight == 0.0
    
    def test_population_group_with_negative_values(self):
        """Test PopulationGroup with negative values."""
        group = PopulationGroup(
            tag=INDEPENDENTS,
            party_bonus=-1.0,
            mean=-0.5,
            stddev=-1.0,  # This might cause issues in practice
            skew=-0.5,
            weight=-100.0
        )
        
        assert group.party_bonus == -1.0
        assert group.mean == -0.5
        assert group.stddev == -1.0
        assert group.skew == -0.5
        assert group.weight == -100.0
    
    def test_shift_with_zero_shift(self):
        """Test shift method with zero shift."""
        group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        shifted = group.shift(0.0)
        assert shifted.mean == group.mean
        assert shifted.tag == group.tag
        assert shifted.stddev == group.stddev
        assert shifted.weight == group.weight
    
    def test_reweight_with_zero_scale(self):
        """Test reweight method with zero scale factor."""
        group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        reweighted = group.reweight(0.0)
        assert reweighted.weight == 0.0
        assert reweighted.tag == group.tag
        assert reweighted.mean == group.mean
        assert reweighted.stddev == group.stddev
    
    def test_population_sample_with_zero_samples(self):
        """Test population_sample with zero samples."""
        group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        voters = group.population_sample(0)
        assert len(voters) == 0
        assert isinstance(voters, list)
    
    def test_population_sample_with_negative_samples(self):
        """Test population_sample with negative samples."""
        group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        # This should not raise an error, but might produce unexpected results
        voters = group.population_sample(-10)
        assert isinstance(voters, list)
    
    def test_random_candidate_with_zero_variance(self):
        """Test random_candidate with zero variance."""
        group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        candidate = group.random_candidate("Test", 0.0, 0.0)
        assert candidate.name == "Test"
        assert candidate.tag == group.tag
        # With zero variance, ideology should be exactly the group mean
        assert candidate.ideology == group.mean
        assert candidate.quality == 0.0


class TestPopulationGroupWithDifferentParties:
    """Test PopulationGroup with different party tags."""
    
    @pytest.mark.parametrize("party_tag,expected_name,expected_plural", [
        (DEMOCRATS, "Democratic", "Democrats"),
        (REPUBLICANS, "Republican", "Republicans"),
        (INDEPENDENTS, "Independent", "Independents")
    ])
    def test_population_group_with_different_parties(self, party_tag, expected_name, expected_plural):
        """Test PopulationGroup creation with different parties."""
        group = PopulationGroup(tag=party_tag)
        
        assert group.tag == party_tag
        assert group.name == expected_name
        assert group.plural_name == expected_plural
    
    def test_shift_out_with_different_parties(self):
        """Test shift_out method with different parties."""
        # Test all parties
        for party in [DEMOCRATS, REPUBLICANS, INDEPENDENTS]:
            group = PopulationGroup(
                tag=party,
                party_bonus=1.0,
                mean=0.0,
                stddev=1.0,
                skew=0.0,
                weight=100.0
            )
            
            shifted = group.shift_out(0.2)
            
            if party == REPUBLICANS:
                assert shifted.mean == 0.2  # Should shift right
            elif party == DEMOCRATS:
                assert shifted.mean == -0.2  # Should shift left
            else:  # INDEPENDENTS
                assert shifted.mean == 0.0  # Should not change
            
            assert shifted.tag == party
            assert shifted.stddev == group.stddev
            assert shifted.weight == group.weight


class TestPopulationGroupRandomness:
    """Test randomness aspects of PopulationGroup."""
    
    def test_population_sample_randomness(self):
        """Test that population_sample produces different results."""
        group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        # Generate two samples
        voters1 = group.population_sample(100)
        voters2 = group.population_sample(100)
        
        # Should have same length
        assert len(voters1) == len(voters2) == 100
        
        # Ideologies should be different (random)
        ideologies1 = [v.ideology for v in voters1]
        ideologies2 = [v.ideology for v in voters2]
        
        # Very unlikely to be identical
        assert ideologies1 != ideologies2
    
    def test_random_voter_randomness(self):
        """Test that random_voter produces different results."""
        group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        # Generate multiple voters
        voters = [group.random_voter() for _ in range(10)]
        
        # All should have same party
        assert all(v.party == group for v in voters)
        
        # Ideologies should be different (random)
        ideologies = [v.ideology for v in voters]
        assert len(set(ideologies)) > 1  # Should have some variation
    
    def test_random_candidate_randomness(self):
        """Test that random_candidate produces different results."""
        group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        # Generate multiple candidates
        candidates = [group.random_candidate(f"Test{i}", 0.1, 0.2) for i in range(10)]
        
        # All should have same tag
        assert all(c.tag == group.tag for c in candidates)
        
        # Ideologies and qualities should be different (random)
        ideologies = [c.ideology for c in candidates]
        qualities = [c.quality for c in candidates]
        
        assert len(set(ideologies)) > 1  # Should have some variation
        assert len(set(qualities)) > 1  # Should have some variation

