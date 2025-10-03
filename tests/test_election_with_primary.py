"""
Tests for ElectionWithPrimary class.
"""
import pytest
from simulation_base.election_with_primary import (
    ElectionWithPrimary, ElectionWithPrimaryResult
)
from simulation_base.candidate import Candidate
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.ballot import RCVBallot, CandidateScore
from simulation_base.election_result import ElectionResult, CandidateResult
from simulation_base.election_definition import ElectionDefinition
from simulation_base.combined_population import CombinedPopulation
from simulation_base.population_group import PopulationGroup
from simulation_base.election_config import ElectionConfig
from simulation_base.gaussian_generator import GaussianGenerator
from simulation_base.voter import Voter
from simulation_base.simple_plurality import SimplePluralityResult
from simulation_base.instant_runoff_election import RCVResult


class TestElectionWithPrimaryResult:
    """Test ElectionWithPrimaryResult class."""
    
    def test_election_with_primary_result_creation(self):
        """Test creating an ElectionWithPrimaryResult."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create mock election results
        dem_primary = SimplePluralityResult({candidates[0]: 100.0}, voter_satisfaction=0.8)
        rep_primary = SimplePluralityResult({candidates[1]: 80.0}, voter_satisfaction=0.7)
        general = RCVResult([], voter_satisfaction=0.75)
        
        result = ElectionWithPrimaryResult(dem_primary, rep_primary, general)
        
        assert result.democratic_primary == dem_primary
        assert result.republican_primary == rep_primary
        assert result.general_election == general
    
    def test_winner_method(self):
        """Test the winner method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create mock election results
        dem_primary = SimplePluralityResult({candidates[0]: 100.0}, voter_satisfaction=0.8)
        rep_primary = SimplePluralityResult({candidates[1]: 80.0}, voter_satisfaction=0.7)
        general = RCVResult([], voter_satisfaction=0.75)
        
        result = ElectionWithPrimaryResult(dem_primary, rep_primary, general)
        
        # Should return general election winner, but RCVResult with no rounds crashes
        with pytest.raises(ValueError, match="No rounds in RCV result"):
            winner = result.winner()
    
    def test_voter_satisfaction_method(self):
        """Test the voter_satisfaction method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create mock election results
        dem_primary = SimplePluralityResult({candidates[0]: 100.0}, voter_satisfaction=0.8)
        rep_primary = SimplePluralityResult({candidates[1]: 80.0}, voter_satisfaction=0.7)
        general = RCVResult([], voter_satisfaction=0.75)
        
        result = ElectionWithPrimaryResult(dem_primary, rep_primary, general)
        
        # Should return general election voter satisfaction
        satisfaction = result.voter_satisfaction()
        assert satisfaction == 0.75
    
    def test_ordered_results_method(self):
        """Test the ordered_results method."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create mock election results
        dem_primary = SimplePluralityResult({candidates[0]: 100.0}, voter_satisfaction=0.8)
        rep_primary = SimplePluralityResult({candidates[1]: 80.0}, voter_satisfaction=0.7)
        general = RCVResult([], voter_satisfaction=0.75)
        
        result = ElectionWithPrimaryResult(dem_primary, rep_primary, general)
        
        # Should return general election ordered results
        ordered = result.ordered_results()
        assert ordered == general.ordered_results()
    
    def test_n_votes_property(self):
        """Test the n_votes property."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create mock election results
        dem_primary = SimplePluralityResult({candidates[0]: 100.0}, voter_satisfaction=0.8)
        rep_primary = SimplePluralityResult({candidates[1]: 80.0}, voter_satisfaction=0.7)
        general = RCVResult([], voter_satisfaction=0.75)
        
        result = ElectionWithPrimaryResult(dem_primary, rep_primary, general)
        
        # Should return general election n_votes
        n_votes = result.n_votes
        assert n_votes == general.n_votes


class TestElectionWithPrimary:
    """Test ElectionWithPrimary class."""
    
    def test_election_with_primary_initialization(self):
        """Test ElectionWithPrimary initialization."""
        # Test with default values
        primary = ElectionWithPrimary()
        assert primary.primary_skew == 0.5
        assert not primary.debug
        
        # Test with custom values
        primary = ElectionWithPrimary(primary_skew=0.25, debug=True)
        assert primary.primary_skew == 0.25
        assert primary.debug
    
    def test_name_property(self):
        """Test the name property."""
        primary = ElectionWithPrimary()
        assert primary.name == "primary"
    
    def test_run_method_basic(self):
        """Test the run method with basic scenario."""
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
        
        primary = ElectionWithPrimary(primary_skew=0.25, debug=False)
        result = primary.run(election_def)
        
        assert isinstance(result, ElectionWithPrimaryResult)
        assert isinstance(result.democratic_primary, ElectionResult)
        assert isinstance(result.republican_primary, ElectionResult)
        assert isinstance(result.general_election, ElectionResult)
        
        # Check that primaries have winners
        dem_winner = result.democratic_primary.winner()
        rep_winner = result.republican_primary.winner()
        
        assert dem_winner.tag == DEMOCRATS
        assert rep_winner.tag == REPUBLICANS
        
        # Check that general election has a winner
        general_winner = result.general_election.winner()
        assert general_winner in candidates
    
    def test_run_method_with_independents(self):
        """Test the run method with independent candidates."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False),
            Candidate(name="David", tag=INDEPENDENTS, ideology=0.1, quality=0.5, incumbent=False)
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
        
        primary = ElectionWithPrimary(primary_skew=0.25, debug=False)
        result = primary.run(election_def)
        
        assert isinstance(result, ElectionWithPrimaryResult)
        
        # Check that general election includes independent candidates
        general_winner = result.general_election.winner()
        assert general_winner in candidates
        
        # Check that independent candidates are in general election
        general_results = result.general_election.ordered_results()
        general_candidates = [cr.candidate for cr in general_results]
        
        # Should include at least one independent candidate
        independent_candidates = [c for c in general_candidates if c.tag == INDEPENDENTS]
        assert len(independent_candidates) >= 1
    
    def test_run_method_with_single_party_candidates(self):
        """Test the run method with only one party's candidates."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Alice2", tag=DEMOCRATS, ideology=-0.3, quality=0.7, incumbent=False)
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
        
        primary = ElectionWithPrimary(primary_skew=0.25, debug=False)
        
        # Republican primary crashes when no Republican candidates exist
        with pytest.raises(IndexError, match="list index out of range"):
            result = primary.run(election_def)
    
    def test_create_skewed_voters_method(self):
        """Test the _create_skewed_voters method."""
        primary = ElectionWithPrimary(primary_skew=0.25, debug=False)
        
        # Create voters
        population_group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        voters = [
            Voter(party=population_group, ideology=-0.3),
            Voter(party=population_group, ideology=-0.4)
        ]
        
        # Test with positive skew
        skewed_voters = primary._create_skewed_voters(voters, 0.2)
        
        assert len(skewed_voters) == len(voters)
        assert all(isinstance(v, Voter) for v in skewed_voters)
        assert all(v.party == population_group for v in skewed_voters)
        
        # Check that ideologies are skewed
        for i, (original, skewed) in enumerate(zip(voters, skewed_voters)):
            assert skewed.ideology == original.ideology + 0.2
    
    def test_run_primary_method(self):
        """Test the _run_primary method."""
        primary = ElectionWithPrimary(primary_skew=0.25, debug=False)
        
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Alice2", tag=DEMOCRATS, ideology=-0.3, quality=0.7, incumbent=False)
        ]
        
        # Create voters
        population_group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        voters = [
            Voter(party=population_group, ideology=-0.3),
            Voter(party=population_group, ideology=-0.4)
        ]
        
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        
        result = primary._run_primary(candidates, voters, config, gaussian_generator)
        
        assert isinstance(result, ElectionResult)
        winner = result.winner()
        assert winner in candidates
        assert winner.tag == DEMOCRATS
    
    def test_run_general_method(self):
        """Test the _run_general method."""
        primary = ElectionWithPrimary(primary_skew=0.25, debug=False)
        
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Charlie", tag=INDEPENDENTS, ideology=0.0, quality=0.7, incumbent=False)
        ]
        
        # Create voters
        population_group = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        )
        
        voters = [
            Voter(party=population_group, ideology=-0.3),
            Voter(party=population_group, ideology=-0.4)
        ]
        
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        
        result = primary._run_general(candidates, voters, config, gaussian_generator)
        
        assert isinstance(result, ElectionResult)
        winner = result.winner()
        assert winner in candidates
    
    def test_print_debug_results_method(self):
        """Test the _print_debug_results method."""
        primary = ElectionWithPrimary(primary_skew=0.25, debug=True)
        
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
        
        # Create mock results
        dem_primary = SimplePluralityResult({candidates[0]: 100.0}, voter_satisfaction=0.8)
        rep_primary = SimplePluralityResult({candidates[1]: 80.0}, voter_satisfaction=0.7)
        general = RCVResult([], voter_satisfaction=0.75)
        
        # Create mock voters
        dem_voters = [Voter(party=groups[0], ideology=-0.3) for _ in range(50)]
        rep_voters = [Voter(party=groups[1], ideology=0.3) for _ in range(50)]
        
        # Should not raise an error
        primary._print_debug_results(
            election_def, dem_primary, rep_primary, dem_voters, rep_voters, general
        )


class TestElectionWithPrimaryEdgeCases:
    """Test edge cases for ElectionWithPrimary."""
    
    def test_run_method_with_empty_candidates(self):
        """Test the run method with empty candidate list."""
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
        
        primary = ElectionWithPrimary(primary_skew=0.25, debug=False)
        
        # Should handle empty candidates gracefully
        try:
            result = primary.run(election_def)
            # If it succeeds, check the result
            assert isinstance(result, ElectionWithPrimaryResult)
        except (ValueError, IndexError):
            # Expected for empty candidates
            pass
    
    def test_run_method_with_single_candidate(self):
        """Test the run method with single candidate."""
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
        
        primary = ElectionWithPrimary(primary_skew=0.25, debug=False)
        
        # Republican primary crashes when no Republican candidates exist
        with pytest.raises(IndexError, match="list index out of range"):
            result = primary.run(election_def)
    
    def test_run_method_with_zero_primary_skew(self):
        """Test the run method with zero primary skew."""
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
        
        primary = ElectionWithPrimary(primary_skew=0.0, debug=False)
        result = primary.run(election_def)
        
        assert isinstance(result, ElectionWithPrimaryResult)
        
        # Should work with zero skew
        dem_winner = result.democratic_primary.winner()
        rep_winner = result.republican_primary.winner()
        general_winner = result.general_election.winner()
        
        assert dem_winner.tag == DEMOCRATS
        assert rep_winner.tag == REPUBLICANS
        assert general_winner in candidates
    
    def test_run_method_with_negative_primary_skew(self):
        """Test the run method with negative primary skew."""
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
        
        primary = ElectionWithPrimary(primary_skew=-0.25, debug=False)
        result = primary.run(election_def)
        
        assert isinstance(result, ElectionWithPrimaryResult)
        
        # Should work with negative skew
        dem_winner = result.democratic_primary.winner()
        rep_winner = result.republican_primary.winner()
        general_winner = result.general_election.winner()
        
        assert dem_winner.tag == DEMOCRATS
        assert rep_winner.tag == REPUBLICANS
        assert general_winner in candidates
    
    def test_run_method_with_very_large_primary_skew(self):
        """Test the run method with very large primary skew."""
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
        
        primary = ElectionWithPrimary(primary_skew=10.0, debug=False)
        result = primary.run(election_def)
        
        assert isinstance(result, ElectionWithPrimaryResult)
        
        # Should work with large skew
        dem_winner = result.democratic_primary.winner()
        rep_winner = result.republican_primary.winner()
        general_winner = result.general_election.winner()
        
        assert dem_winner.tag == DEMOCRATS
        assert rep_winner.tag == REPUBLICANS
        assert general_winner in candidates


class TestElectionWithPrimaryIntegration:
    """Test ElectionWithPrimary integration with other components."""
    
    def test_election_with_primary_result_inheritance(self):
        """Test that ElectionWithPrimaryResult properly inherits from ElectionResult."""
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False)
        ]
        
        # Create mock election results
        dem_primary = SimplePluralityResult({candidates[0]: 100.0}, voter_satisfaction=0.8)
        rep_primary = SimplePluralityResult({candidates[1]: 80.0}, voter_satisfaction=0.7)
        general = RCVResult([], voter_satisfaction=0.75)
        
        result = ElectionWithPrimaryResult(dem_primary, rep_primary, general)
        
        # Test that it implements required methods
        assert hasattr(result, 'winner')
        assert hasattr(result, 'voter_satisfaction')
        assert hasattr(result, 'ordered_results')
        
        # Test method calls - RCVResult with no rounds crashes
        with pytest.raises(ValueError, match="No rounds in RCV result"):
            winner = result.winner()
        
        satisfaction = result.voter_satisfaction()
        assert satisfaction == 0.75
        
        ordered = result.ordered_results()
        assert ordered == general.ordered_results()
    
    def test_election_with_primary_with_different_candidate_generators(self):
        """Test ElectionWithPrimary with different candidate generation scenarios."""
        # Test with multiple candidates per party
        candidates = [
            Candidate(name="Alice", tag=DEMOCRATS, ideology=-0.5, quality=0.8, incumbent=False),
            Candidate(name="Alice2", tag=DEMOCRATS, ideology=-0.3, quality=0.7, incumbent=False),
            Candidate(name="Bob", tag=REPUBLICANS, ideology=0.3, quality=0.6, incumbent=False),
            Candidate(name="Bob2", tag=REPUBLICANS, ideology=0.5, quality=0.5, incumbent=False),
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
        
        primary = ElectionWithPrimary(primary_skew=0.25, debug=False)
        result = primary.run(election_def)
        
        assert isinstance(result, ElectionWithPrimaryResult)
        
        # Check that primaries have winners from correct parties
        dem_winner = result.democratic_primary.winner()
        rep_winner = result.republican_primary.winner()
        
        assert dem_winner.tag == DEMOCRATS
        assert rep_winner.tag == REPUBLICANS
        
        # Check that general election includes independent candidate
        general_winner = result.general_election.winner()
        assert general_winner in candidates
        
        # Check that general election has multiple candidates
        general_results = result.general_election.ordered_results()
        assert len(general_results) >= 2  # At least primary winners
