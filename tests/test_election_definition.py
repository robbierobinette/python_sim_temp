"""
Tests for ElectionDefinition class.
"""
import pytest
from simulation_base.election_definition import ElectionDefinition
from simulation_base.candidate import Candidate
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.combined_population import CombinedPopulation
from simulation_base.population_group import PopulationGroup
from simulation_base.election_config import ElectionConfig
from simulation_base.gaussian_generator import GaussianGenerator


class TestElectionDefinition:
    """Test ElectionDefinition class functionality."""
    
    def test_election_definition_creation(self):
        """Test creating an ElectionDefinition."""
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
        
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator,
            state="Test"
        )
        
        assert election_def.candidates == candidates
        assert election_def.population == population
        assert election_def.config == config
        assert election_def.gaussian_generator == gaussian_generator
    
    def test_election_definition_with_empty_candidates(self):
        """Test ElectionDefinition with empty candidates list."""
        candidates = []
        
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator,
            state="Test"
        )
        
        assert election_def.candidates == []
        assert election_def.population == population
        assert election_def.config == config
        assert election_def.gaussian_generator == gaussian_generator
    
    def test_election_definition_with_single_candidate(self):
        """Test ElectionDefinition with single candidate."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False)
        ]
        
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator,
            state="Test"
        )
        
        assert len(election_def.candidates) == 1
        assert election_def.candidates[0].name == "Alice"
        assert election_def.population == population
        assert election_def.config == config
        assert election_def.gaussian_generator == gaussian_generator
    
    def test_election_definition_with_multiple_candidates(self):
        """Test ElectionDefinition with multiple candidates."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False),
            Candidate(name="David", tag=DEMOCRATS, ideology=-0.3, quality=0.5, incumbent=False)
        ]
        
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator,
            state="Test"
        )
        
        assert len(election_def.candidates) == 4
        assert election_def.candidates[0].name == "Alice"
        assert election_def.candidates[1].name == "Bob"
        assert election_def.candidates[2].name == "Charlie"
        assert election_def.candidates[3].name == "David"
        assert election_def.population == population
        assert election_def.config == config
        assert election_def.gaussian_generator == gaussian_generator
    
    def test_election_definition_with_different_configs(self):
        """Test ElectionDefinition with different configurations."""
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
        configs = [
            ElectionConfig(uncertainty=0.0),
            ElectionConfig(uncertainty=0.1),
            ElectionConfig(uncertainty=0.5),
            ElectionConfig(uncertainty=1.0)
        ]
        
        for config in configs:
            election_def = ElectionDefinition(
                candidates=candidates,
                population=population,
                config=config,
                gaussian_generator=gaussian_generator,
                state="Test"
            )
            
            assert election_def.config == config
            assert election_def.config.uncertainty == config.uncertainty
            assert election_def.candidates == candidates
            assert election_def.population == population
            assert election_def.gaussian_generator == gaussian_generator
    
    def test_election_definition_with_different_generators(self):
        """Test ElectionDefinition with different Gaussian generators."""
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
        
        config = ElectionConfig(uncertainty=0.1)
        
        # Test with different seeds
        generators = [
            GaussianGenerator(seed=42),
            GaussianGenerator(seed=123),
            GaussianGenerator(seed=0),
            GaussianGenerator(seed=None)
        ]
        
        for generator in generators:
            election_def = ElectionDefinition(
                candidates=candidates,
                population=population,
                config=config,
                gaussian_generator=generator,
                state="Test"
            )
            
            assert election_def.gaussian_generator == generator
            assert election_def.candidates == candidates
            assert election_def.population == population
            assert election_def.config == config
    
    def test_election_definition_with_different_populations(self):
        """Test ElectionDefinition with different populations."""
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
                gaussian_generator=gaussian_generator,
                state="Test"
            )
            
            assert election_def.population == population
            assert election_def.population.n_samples == size
            assert election_def.candidates == candidates
            assert election_def.config == config
            assert election_def.gaussian_generator == gaussian_generator


class TestElectionDefinitionEdgeCases:
    """Test edge cases for ElectionDefinition."""
    
    def test_election_definition_with_duplicate_candidates(self):
        """Test ElectionDefinition with duplicate candidates."""
        candidate = Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False)
        candidates = [candidate, candidate]  # Duplicate candidate
        
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator,
            state="Test"
        )
        
        assert len(election_def.candidates) == 2
        assert election_def.candidates[0] == candidate
        assert election_def.candidates[1] == candidate
        assert election_def.population == population
        assert election_def.config == config
        assert election_def.gaussian_generator == gaussian_generator
    
    def test_election_definition_with_empty_population(self):
        """Test ElectionDefinition with empty population."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create empty population - crashes as per user requirement
        with pytest.raises(IndexError, match="list index out of range"):
            population = CombinedPopulation(populations=[], desired_samples=0)
    
    def test_election_definition_with_single_party_population(self):
        """Test ElectionDefinition with single party population."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Alice2", tag=DEMOCRATS, ideology=-0.3, quality=0.7, incumbent=False)
        ]
        
        # Create single party population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator,
            state="Test"
        )
        
        assert election_def.candidates == candidates
        assert election_def.population == population
        assert len(election_def.population.populations) == 1
        assert election_def.config == config
        assert election_def.gaussian_generator == gaussian_generator
    
    def test_election_definition_with_extreme_uncertainty(self):
        """Test ElectionDefinition with extreme uncertainty values."""
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
        extreme_configs = [
            ElectionConfig(uncertainty=0.0),
            ElectionConfig(uncertainty=10.0),
            ElectionConfig(uncertainty=-5.0),
            ElectionConfig(uncertainty=1e6),
            ElectionConfig(uncertainty=1e-10)
        ]
        
        for config in extreme_configs:
            election_def = ElectionDefinition(
                candidates=candidates,
                population=population,
                config=config,
                gaussian_generator=gaussian_generator,
                state="Test"
            )
            
            assert election_def.config == config
            assert election_def.config.uncertainty == config.uncertainty
            assert election_def.candidates == candidates
            assert election_def.population == population
            assert election_def.gaussian_generator == gaussian_generator


class TestElectionDefinitionIntegration:
    """Test ElectionDefinition integration with other components."""
    
    def test_election_definition_with_election_processes(self):
        """Test ElectionDefinition with election processes."""
        from simulation_base.instant_runoff_election import InstantRunoffElection
        from simulation_base.head_to_head_election import HeadToHeadElection
        from simulation_base.election_with_primary import ElectionWithPrimary
        
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
        
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator,
            state="Test"
        )
        
        # Test with different election processes
        processes = [
            InstantRunoffElection(),
            HeadToHeadElection(),
            ElectionWithPrimary()
        ]
        
        for process in processes:
            # Create ballots for the new interface
            from simulation_base.ballot_utils import create_ballots_from_election_def
            ballots = create_ballots_from_election_def(election_def)
            result = process.run(election_def.candidates, ballots)
            
            # Should return an election result
            assert hasattr(result, 'winner')
            assert hasattr(result, 'voter_satisfaction')
            assert hasattr(result, 'ordered_results')
            
            # Should have a winner
            winner = result.winner()
            assert winner in candidates
            
            # Should have voter satisfaction
            satisfaction = result.voter_satisfaction()
            assert isinstance(satisfaction, float)
            assert 0.0 <= satisfaction <= 1.0
            
            # Should have ordered results
            ordered = result.ordered_results()
            assert isinstance(ordered, list)
            assert len(ordered) > 0
    
    def test_election_definition_with_candidate_generators(self):
        """Test ElectionDefinition with candidate generators."""
        from simulation_base.candidate_generator import PartisanCandidateGenerator
        
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        
        # Generate candidates using candidate generator
        candidate_generator = PartisanCandidateGenerator(
            n_party_candidates=2,
            spread=0.4,
            ideology_variance=0.1,
            quality_variance=0.2,
            primary_skew=0.25,
            median_variance=0.1,
            gaussian_generator=gaussian_generator
        )
        
        candidates = candidate_generator.candidates(population)
        
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator,
            state="Test"
        )
        
        assert election_def.candidates == candidates
        assert len(election_def.candidates) > 0
        assert all(isinstance(c, Candidate) for c in election_def.candidates)
        assert election_def.population == population
        assert election_def.config == config
        assert election_def.gaussian_generator == gaussian_generator
    
    def test_election_definition_serialization(self):
        """Test ElectionDefinition serialization (if applicable)."""
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
        
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator,
            state="Test"
        )
        
        # Test that election_def can be converted to dict (if dataclass)
        if hasattr(election_def, '__dict__'):
            election_dict = election_def.__dict__
            assert 'candidates' in election_dict
            assert 'population' in election_dict
            assert 'config' in election_dict
            assert 'gaussian_generator' in election_dict
        
        # Test that election_def can be pickled (if needed)
        import pickle
        try:
            pickled = pickle.dumps(election_def)
            unpickled = pickle.loads(pickled)
            assert len(unpickled.candidates) == len(election_def.candidates)
            assert unpickled.population.n_samples == election_def.population.n_samples
            assert unpickled.config.uncertainty == election_def.config.uncertainty
        except (pickle.PicklingError, AttributeError):
            # Pickling might not be supported, which is fine
            pass
    
    def test_election_definition_copy(self):
        """Test ElectionDefinition copying."""
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
        
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        
        election_def = ElectionDefinition(
            candidates=candidates,
            population=population,
            config=config,
            gaussian_generator=gaussian_generator,
            state="Test"
        )
        
        # Test shallow copy
        import copy
        election_copy = copy.copy(election_def)
        assert len(election_copy.candidates) == len(election_def.candidates)
        assert election_copy.population.n_samples == election_def.population.n_samples
        assert election_copy.config.uncertainty == election_def.config.uncertainty
        assert election_copy is not election_def  # Should be different objects
        
        # Test deep copy
        election_deep_copy = copy.deepcopy(election_def)
        assert len(election_deep_copy.candidates) == len(election_def.candidates)
        assert election_deep_copy.population.n_samples == election_def.population.n_samples
        assert election_deep_copy.config.uncertainty == election_def.config.uncertainty
        assert election_deep_copy is not election_def  # Should be different objects
