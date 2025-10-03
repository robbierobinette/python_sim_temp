"""
Tests for DistrictVotingRecord class.
"""
import pytest
from simulation_base.district_voting_record import DistrictVotingRecord


class TestDistrictVotingRecord:
    """Test DistrictVotingRecord class functionality."""
    
    def test_district_voting_record_creation(self):
        """Test creating a DistrictVotingRecord."""
        dvr = DistrictVotingRecord(
            district="CA-01",
            incumbent="John Doe",
            expected_lean=-5.0,
            d_pct1=0.52,
            r_pct1=0.48,
            d_pct2=0.53,
            r_pct2=0.47
        )
        
        assert dvr.district == "CA-01"
        assert dvr.incumbent == "John Doe"
        assert dvr.expected_lean == -5.0
        assert dvr.d_pct1 == 0.52
        assert dvr.r_pct1 == 0.48
        assert dvr.d_pct2 == 0.53
        assert dvr.r_pct2 == 0.47
    
    def test_district_voting_record_with_zero_lean(self):
        """Test DistrictVotingRecord with zero lean."""
        dvr = DistrictVotingRecord(
            district="FL-01",
            incumbent="Jane Smith",
            expected_lean=0.0,
            d_pct1=0.50,
            r_pct1=0.50,
            d_pct2=0.50,
            r_pct2=0.50
        )
        
        assert dvr.expected_lean == 0.0
        assert dvr.d_pct1 == 0.50
        assert dvr.r_pct1 == 0.50
        assert dvr.d_pct2 == 0.50
        assert dvr.r_pct2 == 0.50
    
    def test_district_voting_record_with_positive_lean(self):
        """Test DistrictVotingRecord with positive lean (Republican)."""
        dvr = DistrictVotingRecord(
            district="TX-01",
            incumbent="Bob Johnson",
            expected_lean=15.0,
            d_pct1=0.35,
            r_pct1=0.65,
            d_pct2=0.33,
            r_pct2=0.67
        )
        
        assert dvr.expected_lean == 15.0
        assert dvr.d_pct1 == 0.35
        assert dvr.r_pct1 == 0.65
        assert dvr.d_pct2 == 0.33
        assert dvr.r_pct2 == 0.67
    
    def test_district_voting_record_with_negative_lean(self):
        """Test DistrictVotingRecord with negative lean (Democratic)."""
        dvr = DistrictVotingRecord(
            district="NY-01",
            incumbent="Alice Brown",
            expected_lean=-20.0,
            d_pct1=0.70,
            r_pct1=0.30,
            d_pct2=0.68,
            r_pct2=0.32
        )
        
        assert dvr.expected_lean == -20.0
        assert dvr.d_pct1 == 0.70
        assert dvr.r_pct1 == 0.30
        assert dvr.d_pct2 == 0.68
        assert dvr.r_pct2 == 0.32
    
    def test_district_voting_record_with_extreme_lean(self):
        """Test DistrictVotingRecord with extreme lean values."""
        # Test with very high Republican lean
        dvr = DistrictVotingRecord(
            district="UT-01",
            incumbent="Mike Wilson",
            expected_lean=50.0,
            d_pct1=0.10,
            r_pct1=0.90,
            d_pct2=0.08,
            r_pct2=0.92
        )
        
        assert dvr.expected_lean == 50.0
        assert dvr.d_pct1 == 0.10
        assert dvr.r_pct1 == 0.90
        assert dvr.d_pct2 == 0.08
        assert dvr.r_pct2 == 0.92
        
        # Test with very high Democratic lean
        dvr = DistrictVotingRecord(
            district="MA-01",
            incumbent="Sarah Davis",
            expected_lean=-40.0,
            d_pct1=0.85,
            r_pct1=0.15,
            d_pct2=0.87,
            r_pct2=0.13
        )
        
        assert dvr.expected_lean == -40.0
        assert dvr.d_pct1 == 0.85
        assert dvr.r_pct1 == 0.15
        assert dvr.d_pct2 == 0.87
        assert dvr.r_pct2 == 0.13
    
    def test_district_voting_record_with_fractional_percentages(self):
        """Test DistrictVotingRecord with fractional percentages."""
        dvr = DistrictVotingRecord(
            district="OH-01",
            incumbent="Tom Green",
            expected_lean=2.5,
            d_pct1=0.4875,
            r_pct1=0.5125,
            d_pct2=0.4850,
            r_pct2=0.5150
        )
        
        assert dvr.expected_lean == 2.5
        assert dvr.d_pct1 == 0.4875
        assert dvr.r_pct1 == 0.5125
        assert dvr.d_pct2 == 0.4850
        assert dvr.r_pct2 == 0.5150
    
    def test_district_voting_record_with_unicode_characters(self):
        """Test DistrictVotingRecord with unicode characters."""
        dvr = DistrictVotingRecord(
            district="CA-测试",
            incumbent="José María",
            expected_lean=-3.0,
            d_pct1=0.51,
            r_pct1=0.49,
            d_pct2=0.52,
            r_pct2=0.48
        )
        
        assert dvr.district == "CA-测试"
        assert dvr.incumbent == "José María"
        assert dvr.expected_lean == -3.0
        assert dvr.d_pct1 == 0.51
        assert dvr.r_pct1 == 0.49
        assert dvr.d_pct2 == 0.52
        assert dvr.r_pct2 == 0.48
    
    def test_district_voting_record_with_very_long_names(self):
        """Test DistrictVotingRecord with very long names."""
        long_district = "A" * 1000
        long_incumbent = "B" * 1000
        
        dvr = DistrictVotingRecord(
            district=long_district,
            incumbent=long_incumbent,
            expected_lean=5.0,
            d_pct1=0.55,
            r_pct1=0.45,
            d_pct2=0.56,
            r_pct2=0.44
        )
        
        assert dvr.district == long_district
        assert dvr.incumbent == long_incumbent
        assert len(dvr.district) == 1000
        assert len(dvr.incumbent) == 1000
        assert dvr.expected_lean == 5.0
        assert dvr.d_pct1 == 0.55
        assert dvr.r_pct1 == 0.45
        assert dvr.d_pct2 == 0.56
        assert dvr.r_pct2 == 0.44


class TestDistrictVotingRecordEdgeCases:
    """Test edge cases for DistrictVotingRecord."""
    
    def test_district_voting_record_with_zero_percentages(self):
        """Test DistrictVotingRecord with zero percentages."""
        dvr = DistrictVotingRecord(
            district="AK-01",
            incumbent="No One",
            expected_lean=0.0,
            d_pct1=0.0,
            r_pct1=0.0,
            d_pct2=0.0,
            r_pct2=0.0
        )
        
        assert dvr.d_pct1 == 0.0
        assert dvr.r_pct1 == 0.0
        assert dvr.d_pct2 == 0.0
        assert dvr.r_pct2 == 0.0
    
    def test_district_voting_record_with_one_percentages(self):
        """Test DistrictVotingRecord with 100% percentages."""
        dvr = DistrictVotingRecord(
            district="WY-01",
            incumbent="All Republican",
            expected_lean=100.0,
            d_pct1=0.0,
            r_pct1=1.0,
            d_pct2=0.0,
            r_pct2=1.0
        )
        
        assert dvr.d_pct1 == 0.0
        assert dvr.r_pct1 == 1.0
        assert dvr.d_pct2 == 0.0
        assert dvr.r_pct2 == 1.0
    
    def test_district_voting_record_with_negative_percentages(self):
        """Test DistrictVotingRecord with negative percentages."""
        dvr = DistrictVotingRecord(
            district="NV-01",
            incumbent="Negative Votes",
            expected_lean=-10.0,
            d_pct1=-0.1,
            r_pct1=-0.2,
            d_pct2=-0.15,
            r_pct2=-0.25
        )
        
        assert dvr.d_pct1 == -0.1
        assert dvr.r_pct1 == -0.2
        assert dvr.d_pct2 == -0.15
        assert dvr.r_pct2 == -0.25
    
    def test_district_voting_record_with_percentages_over_one(self):
        """Test DistrictVotingRecord with percentages over 1.0."""
        dvr = DistrictVotingRecord(
            district="HI-01",
            incumbent="Over 100%",
            expected_lean=5.0,
            d_pct1=1.5,
            r_pct1=2.0,
            d_pct2=1.8,
            r_pct2=2.2
        )
        
        assert dvr.d_pct1 == 1.5
        assert dvr.r_pct1 == 2.0
        assert dvr.d_pct2 == 1.8
        assert dvr.r_pct2 == 2.2
    
    def test_district_voting_record_with_empty_strings(self):
        """Test DistrictVotingRecord with empty strings."""
        dvr = DistrictVotingRecord(
            district="",
            incumbent="",
            expected_lean=0.0,
            d_pct1=0.5,
            r_pct1=0.5,
            d_pct2=0.5,
            r_pct2=0.5
        )
        
        assert dvr.district == ""
        assert dvr.incumbent == ""
        assert dvr.expected_lean == 0.0
        assert dvr.d_pct1 == 0.5
        assert dvr.r_pct1 == 0.5
        assert dvr.d_pct2 == 0.5
        assert dvr.r_pct2 == 0.5
    
    def test_district_voting_record_with_none_values(self):
        """Test DistrictVotingRecord with None values."""
        dvr = DistrictVotingRecord(
            district=None,
            incumbent=None,
            expected_lean=0.0,
            d_pct1=0.5,
            r_pct1=0.5,
            d_pct2=0.5,
            r_pct2=0.5
        )
        
        assert dvr.district is None
        assert dvr.incumbent is None
        assert dvr.expected_lean == 0.0
        assert dvr.d_pct1 == 0.5
        assert dvr.r_pct1 == 0.5
        assert dvr.d_pct2 == 0.5
        assert dvr.r_pct2 == 0.5
    
    def test_district_voting_record_with_extreme_lean_values(self):
        """Test DistrictVotingRecord with extreme lean values."""
        # Test with very large positive lean
        dvr = DistrictVotingRecord(
            district="MT-01",
            incumbent="Extreme Rep",
            expected_lean=1000.0,
            d_pct1=0.001,
            r_pct1=0.999,
            d_pct2=0.0005,
            r_pct2=0.9995
        )
        
        assert dvr.expected_lean == 1000.0
        assert dvr.d_pct1 == 0.001
        assert dvr.r_pct1 == 0.999
        assert dvr.d_pct2 == 0.0005
        assert dvr.r_pct2 == 0.9995
        
        # Test with very large negative lean
        dvr = DistrictVotingRecord(
            district="VT-01",
            incumbent="Extreme Dem",
            expected_lean=-1000.0,
            d_pct1=0.999,
            r_pct1=0.001,
            d_pct2=0.9995,
            r_pct2=0.0005
        )
        
        assert dvr.expected_lean == -1000.0
        assert dvr.d_pct1 == 0.999
        assert dvr.r_pct1 == 0.001
        assert dvr.d_pct2 == 0.9995
        assert dvr.r_pct2 == 0.0005


class TestDistrictVotingRecordIntegration:
    """Test DistrictVotingRecord integration with other components."""
    
    def test_district_voting_record_with_unit_population(self):
        """Test DistrictVotingRecord with UnitPopulation."""
        from simulation_base.unit_population import UnitPopulation
        
        dvr = DistrictVotingRecord(
            district="CA-01",
            incumbent="John Doe",
            expected_lean=-5.0,
            d_pct1=0.52,
            r_pct1=0.48,
            d_pct2=0.53,
            r_pct2=0.47
        )
        
        # Test create method
        population = UnitPopulation.create(dvr, n_voters=100)
        
        assert population.n_samples == 100
        assert len(population.populations) == 3  # Dem, Rep, Ind
        
        # Test create_with_params method
        population2 = UnitPopulation.create_with_params(
            dvr=dvr,
            partisanship=1.0,
            stddev=1.0,
            skew_factor=0.05,
            n_voters=200
        )
        
        assert population2.n_samples == 200
        assert len(population2.populations) == 3
    
    def test_district_voting_record_with_candidate_generators(self):
        """Test DistrictVotingRecord with candidate generators."""
        from simulation_base.candidate_generator import PartisanCandidateGenerator
        from simulation_base.unit_population import UnitPopulation
        
        dvr = DistrictVotingRecord(
            district="TX-01",
            incumbent="Jane Smith",
            expected_lean=15.0,
            d_pct1=0.35,
            r_pct1=0.65,
            d_pct2=0.33,
            r_pct2=0.67
        )
        
        # Create population from DVR
        population = UnitPopulation.create(dvr, n_voters=100)
        
        # Create candidate generator
        candidate_generator = PartisanCandidateGenerator(
            n_party_candidates=2,
            spread=0.4,
            ideology_variance=0.1,
            quality_variance=0.2,
            primary_skew=0.25,
            median_variance=0.1
        )
        
        # Generate candidates
        from simulation_base.candidate import Candidate
        candidates = candidate_generator.candidates(population)
        
        assert len(candidates) > 0
        assert all(isinstance(c, Candidate) for c in candidates)
    
    def test_district_voting_record_with_election_processes(self):
        """Test DistrictVotingRecord with election processes."""
        from simulation_base.unit_population import UnitPopulation
        from simulation_base.candidate_generator import PartisanCandidateGenerator
        from simulation_base.election_definition import ElectionDefinition
        from simulation_base.election_config import ElectionConfig
        from simulation_base.gaussian_generator import GaussianGenerator
        from simulation_base.instant_runoff_election import InstantRunoffElection
        
        dvr = DistrictVotingRecord(
            district="NY-01",
            incumbent="Alice Brown",
            expected_lean=-20.0,
            d_pct1=0.70,
            r_pct1=0.30,
            d_pct2=0.68,
            r_pct2=0.32
        )
        
        # Create population from DVR
        population = UnitPopulation.create(dvr, n_voters=100)
        
        # Create candidate generator
        candidate_generator = PartisanCandidateGenerator(
            n_party_candidates=1,
            spread=0.4,
            ideology_variance=0.1,
            quality_variance=0.2,
            primary_skew=0.25,
            median_variance=0.1
        )
        
        # Generate candidates
        candidates = candidate_generator.candidates(population)
        
        # Create election definition
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator
        )
        
        # Run election
        election = InstantRunoffElection()
        result = election.run(election_def)
        
        assert hasattr(result, 'winner')
        assert hasattr(result, 'voter_satisfaction')
        assert hasattr(result, 'ordered_results')
        
        winner = result.winner()
        assert winner in candidates
        
        satisfaction = result.voter_satisfaction()
        assert isinstance(satisfaction, float)
        assert 0.0 <= satisfaction <= 1.0
    
    def test_district_voting_record_serialization(self):
        """Test DistrictVotingRecord serialization (if applicable)."""
        dvr = DistrictVotingRecord(
            district="CA-01",
            incumbent="John Doe",
            expected_lean=-5.0,
            d_pct1=0.52,
            r_pct1=0.48,
            d_pct2=0.53,
            r_pct2=0.47
        )
        
        # Test that dvr can be converted to dict (if dataclass)
        if hasattr(dvr, '__dict__'):
            dvr_dict = dvr.__dict__
            assert 'district' in dvr_dict
            assert 'incumbent' in dvr_dict
            assert 'expected_lean' in dvr_dict
            assert 'd_pct1' in dvr_dict
            assert 'r_pct1' in dvr_dict
            assert 'd_pct2' in dvr_dict
            assert 'r_pct2' in dvr_dict
        
        # Test that dvr can be pickled (if needed)
        import pickle
        try:
            pickled = pickle.dumps(dvr)
            unpickled = pickle.loads(pickled)
            assert unpickled.district == dvr.district
            assert unpickled.incumbent == dvr.incumbent
            assert unpickled.expected_lean == dvr.expected_lean
            assert unpickled.d_pct1 == dvr.d_pct1
            assert unpickled.r_pct1 == dvr.r_pct1
            assert unpickled.d_pct2 == dvr.d_pct2
            assert unpickled.r_pct2 == dvr.r_pct2
        except (pickle.PicklingError, AttributeError):
            # Pickling might not be supported, which is fine
            pass
    
    def test_district_voting_record_copy(self):
        """Test DistrictVotingRecord copying."""
        dvr = DistrictVotingRecord(
            district="CA-01",
            incumbent="John Doe",
            expected_lean=-5.0,
            d_pct1=0.52,
            r_pct1=0.48,
            d_pct2=0.53,
            r_pct2=0.47
        )
        
        # Test shallow copy
        import copy
        dvr_copy = copy.copy(dvr)
        assert dvr_copy.district == dvr.district
        assert dvr_copy.incumbent == dvr.incumbent
        assert dvr_copy.expected_lean == dvr.expected_lean
        assert dvr_copy.d_pct1 == dvr.d_pct1
        assert dvr_copy.r_pct1 == dvr.r_pct1
        assert dvr_copy.d_pct2 == dvr.d_pct2
        assert dvr_copy.r_pct2 == dvr.r_pct2
        assert dvr_copy is not dvr  # Should be different objects
        
        # Test deep copy
        dvr_deep_copy = copy.deepcopy(dvr)
        assert dvr_deep_copy.district == dvr.district
        assert dvr_deep_copy.incumbent == dvr.incumbent
        assert dvr_deep_copy.expected_lean == dvr.expected_lean
        assert dvr_deep_copy.d_pct1 == dvr.d_pct1
        assert dvr_deep_copy.r_pct1 == dvr.r_pct1
        assert dvr_deep_copy.d_pct2 == dvr.d_pct2
        assert dvr_deep_copy.r_pct2 == dvr.r_pct2
        assert dvr_deep_copy is not dvr  # Should be different objects
    
    def test_district_voting_record_equality(self):
        """Test DistrictVotingRecord equality."""
        dvr1 = DistrictVotingRecord(
            district="CA-01",
            incumbent="John Doe",
            expected_lean=-5.0,
            d_pct1=0.52,
            r_pct1=0.48,
            d_pct2=0.53,
            r_pct2=0.47
        )
        
        dvr2 = DistrictVotingRecord(
            district="CA-01",
            incumbent="John Doe",
            expected_lean=-5.0,
            d_pct1=0.52,
            r_pct1=0.48,
            d_pct2=0.53,
            r_pct2=0.47
        )
        
        dvr3 = DistrictVotingRecord(
            district="CA-02",
            incumbent="Jane Smith",
            expected_lean=5.0,
            d_pct1=0.48,
            r_pct1=0.52,
            d_pct2=0.47,
            r_pct2=0.53
        )
        
        # Same values should be equal
        assert dvr1 == dvr2
        
        # Different values should not be equal
        assert dvr1 != dvr3
    
    def test_district_voting_record_hash(self):
        """Test DistrictVotingRecord hash functionality."""
        dvr1 = DistrictVotingRecord(
            district="CA-01",
            incumbent="John Doe",
            expected_lean=-5.0,
            d_pct1=0.52,
            r_pct1=0.48,
            d_pct2=0.53,
            r_pct2=0.47
        )
        
        dvr2 = DistrictVotingRecord(
            district="CA-01",
            incumbent="John Doe",
            expected_lean=-5.0,
            d_pct1=0.52,
            r_pct1=0.48,
            d_pct2=0.53,
            r_pct2=0.47
        )
        
        dvr3 = DistrictVotingRecord(
            district="CA-02",
            incumbent="Jane Smith",
            expected_lean=5.0,
            d_pct1=0.48,
            r_pct1=0.52,
            d_pct2=0.47,
            r_pct2=0.53
        )
        
        # DistrictVotingRecord is not hashable (no __hash__ method)
        with pytest.raises(TypeError, match="unhashable type"):
            hash(dvr1)
        
        # Should not be usable in sets due to unhashable type
        with pytest.raises(TypeError, match="unhashable type"):
            dvr_set = {dvr1, dvr2, dvr3}
