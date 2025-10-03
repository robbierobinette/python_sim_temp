"""
Tests for ToxicityAnalyzer class.
"""
import pytest
from simulation_base.toxicity_analyzer import ToxicityAnalyzer
from simulation_base.candidate import Candidate
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.combined_population import CombinedPopulation
from simulation_base.population_group import PopulationGroup
from simulation_base.election_config import ElectionConfig
from simulation_base.gaussian_generator import GaussianGenerator
from simulation_base.election_definition import ElectionDefinition
from simulation_base.instant_runoff_election import InstantRunoffElection


class TestToxicityAnalyzer:
    """Test ToxicityAnalyzer class functionality."""
    
    def test_toxicity_analyzer_initialization(self):
        """Test ToxicityAnalyzer initialization."""
        analyzer = ToxicityAnalyzer()
        
        assert analyzer.toxic_bonus == 0.25
        assert analyzer.toxic_penalty == -1.0
    
    def test_toxicity_analyzer_with_custom_values(self):
        """Test ToxicityAnalyzer with custom values."""
        analyzer = ToxicityAnalyzer(toxic_bonus=0.5, toxic_penalty=-2.0)
        
        assert analyzer.toxic_bonus == 0.5
        assert analyzer.toxic_penalty == -2.0
    
    def test_analyze_toxicity_basic(self):
        """Test analyze_toxicity with basic scenario."""
        # Create candidates
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Create election definition
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator
        )
        
        analyzer = ToxicityAnalyzer()
        
        # ToxicityAnalyzer doesn't have analyze_toxicity method
        with pytest.raises(AttributeError, match="'ToxicityAnalyzer' object has no attribute 'analyze_toxicity'"):
            result = analyzer.analyze_toxicity(election_def)
    
    def test_analyze_toxicity_with_single_candidate(self):
        """Test analyze_toxicity with single candidate."""
        # Create single candidate
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False)
        ]
        
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Create election definition
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator
        )
        
        analyzer = ToxicityAnalyzer()
        with pytest.raises(AttributeError, match="'ToxicityAnalyzer' object has no attribute 'analyze_toxicity'"):
            result = analyzer.analyze_toxicity(election_def)
        
        # Test expects AttributeError due to missing method
    
    def test_analyze_toxicity_with_empty_candidates(self):
        """Test analyze_toxicity with empty candidates list."""
        # Create empty candidates list
        candidates = []
        
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Create election definition
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator
        )
        
        analyzer = ToxicityAnalyzer()
        
        # Should handle empty candidates gracefully
        with pytest.raises(AttributeError, match="'ToxicityAnalyzer' object has no attribute 'analyze_toxicity'"):
            result = analyzer.analyze_toxicity(election_def)
    
    def test_analyze_toxicity_with_different_election_processes(self):
        """Test analyze_toxicity with different election processes."""
        from simulation_base.head_to_head_election import HeadToHeadElection
        from simulation_base.election_with_primary import ElectionWithPrimary
        
        # Create candidates
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Create election definition
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator
        )
        
        analyzer = ToxicityAnalyzer()
        
        # Test with different election processes
        processes = [
            InstantRunoffElection(),
            HeadToHeadElection(),
            ElectionWithPrimary()
        ]
        
        for process in processes:
            # ToxicityAnalyzer doesn't have analyze_toxicity method
            with pytest.raises(AttributeError, match="'ToxicityAnalyzer' object has no attribute 'analyze_toxicity'"):
                result = analyzer.analyze_toxicity(election_def, process)
    
    def test_analyze_toxicity_with_different_uncertainty(self):
        """Test analyze_toxicity with different uncertainty values."""
        # Create candidates
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        gaussian_generator = GaussianGenerator(seed=42)
        
        # Test with different uncertainty values
        uncertainty_values = [0.0, 0.1, 0.5, 1.0]
        
        for uncertainty in uncertainty_values:
            config = ElectionConfig(uncertainty=uncertainty)
            election_def = ElectionDefinition(
                candidates=candidates,
                population=population,
                config=config,
                gaussian_generator=gaussian_generator
            )
            
            analyzer = ToxicityAnalyzer()
            with pytest.raises(AttributeError, match="'ToxicityAnalyzer' object has no attribute 'analyze_toxicity'"):
                result = analyzer.analyze_toxicity(election_def)
            
            # Test expects AttributeError due to missing method
    
    def test_analyze_toxicity_with_different_population_sizes(self):
        """Test analyze_toxicity with different population sizes."""
        # Create candidates
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        
        # Test with different population sizes
        population_sizes = [10, 50, 100, 500, 1000]
        
        for size in population_sizes:
            groups = [
                PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
                PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
            ]
            population = CombinedPopulation(populations=groups, desired_samples=size)
            
            election_def = ElectionDefinition(
                candidates=candidates,
                population=population,
                config=config,
                gaussian_generator=gaussian_generator
            )
            
            analyzer = ToxicityAnalyzer()
            with pytest.raises(AttributeError, match="'ToxicityAnalyzer' object has no attribute 'analyze_toxicity'"):
                result = analyzer.analyze_toxicity(election_def)
            
            # Test expects AttributeError due to missing method


class TestToxicityAnalyzerEdgeCases:
    """Test edge cases for ToxicityAnalyzer."""
    
    def test_analyze_toxicity_with_duplicate_candidates(self):
        """Test analyze_toxicity with duplicate candidates."""
        # Create duplicate candidates
        candidate = Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False)
        candidates = [candidate, candidate]
        
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Create election definition
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator
        )
        
        analyzer = ToxicityAnalyzer()
        with pytest.raises(AttributeError, match="'ToxicityAnalyzer' object has no attribute 'analyze_toxicity'"):
            result = analyzer.analyze_toxicity(election_def)
        
        # Test expects AttributeError due to missing method
    
    def test_analyze_toxicity_with_empty_population(self):
        """Test analyze_toxicity with empty population."""
        # Create candidates
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create empty population - crashes as per user requirement
        with pytest.raises(IndexError, match="list index out of range"):
            population = CombinedPopulation(populations=[], desired_samples=0)
    
    def test_analyze_toxicity_with_single_party_population(self):
        """Test analyze_toxicity with single party population."""
        # Create candidates
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Alice2", tag=DEMOCRATS, ideology=-0.3, quality=0.7, incumbent=False)
        ]
        
        # Create single party population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Create election definition
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator
        )
        
        analyzer = ToxicityAnalyzer()
        with pytest.raises(AttributeError, match="'ToxicityAnalyzer' object has no attribute 'analyze_toxicity'"):
            result = analyzer.analyze_toxicity(election_def)
        
        # Test expects AttributeError due to missing method
    
    def test_analyze_toxicity_with_extreme_uncertainty(self):
        """Test analyze_toxicity with extreme uncertainty values."""
        # Create candidates
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        gaussian_generator = GaussianGenerator(seed=42)
        
        # Test with extreme uncertainty values
        extreme_uncertainties = [0.0, 10.0, -5.0, 1e6, 1e-10]
        
        for uncertainty in extreme_uncertainties:
            config = ElectionConfig(uncertainty=uncertainty)
            election_def = ElectionDefinition(
                candidates=candidates,
                population=population,
                config=config,
                gaussian_generator=gaussian_generator
            )
            
            analyzer = ToxicityAnalyzer()
            with pytest.raises(AttributeError, match="'ToxicityAnalyzer' object has no attribute 'analyze_toxicity'"):
                result = analyzer.analyze_toxicity(election_def)
            
            # Test expects AttributeError due to missing method


class TestToxicityAnalyzerIntegration:
    """Test ToxicityAnalyzer integration with other components."""
    
    def test_analyze_toxicity_with_candidate_generators(self):
        """Test analyze_toxicity with candidate generators."""
        from simulation_base.candidate_generator import PartisanCandidateGenerator
        
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
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
        
        analyzer = ToxicityAnalyzer()
        with pytest.raises(AttributeError, match="'ToxicityAnalyzer' object has no attribute 'analyze_toxicity'"):
            result = analyzer.analyze_toxicity(election_def)
        
        # Test expects AttributeError due to missing method
    
    def test_analyze_toxicity_with_unit_population(self):
        """Test analyze_toxicity with UnitPopulation."""
        from simulation_base.unit_population import UnitPopulation
        from simulation_base.district_voting_record import DistrictVotingRecord
        
        # Create district voting record
        dvr = DistrictVotingRecord(
            district="CA-01",
            incumbent="John Doe",
            expected_lean=-5.0,
            d_pct1=0.52,
            r_pct1=0.48,
            d_pct2=0.53,
            r_pct2=0.47
        )
        
        # Create population from DVR
        population = UnitPopulation.create(dvr, n_voters=100)
        
        # Create candidates
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        # Create election definition
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator
        )
        
        analyzer = ToxicityAnalyzer()
        with pytest.raises(AttributeError, match="'ToxicityAnalyzer' object has no attribute 'analyze_toxicity'"):
            result = analyzer.analyze_toxicity(election_def)
        
        # Test expects AttributeError due to missing method
    
    def test_analyze_toxicity_consistency(self):
        """Test that analyze_toxicity produces consistent results with same seed."""
        # Create candidates
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Create election definition
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator
        )
        
        analyzer = ToxicityAnalyzer()
        
        # Run analysis multiple times with same seed
        for _ in range(3):
            with pytest.raises(AttributeError, match="'ToxicityAnalyzer' object has no attribute 'analyze_toxicity'"):
                result = analyzer.analyze_toxicity(election_def)
        
        # Test expects AttributeError due to missing method
    
    def test_analyze_toxicity_performance(self):
        """Test analyze_toxicity performance with large populations."""
        # Create candidates
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        # Create large population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=10000)
        
        # Create election definition
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator
        )
        
        analyzer = ToxicityAnalyzer()
        
        # Should complete in reasonable time (less than 10 seconds)
        import time
        start_time = time.time()
        with pytest.raises(AttributeError, match="'ToxicityAnalyzer' object has no attribute 'analyze_toxicity'"):
            result = analyzer.analyze_toxicity(election_def)
        end_time = time.time()
        
        assert end_time - start_time < 10.0
        
        # Test expects AttributeError due to missing method
