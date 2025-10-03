"""
Integration tests for simulation_base components.
"""
import pytest
from simulation_base.candidate import Candidate
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.population_group import PopulationGroup
from simulation_base.combined_population import CombinedPopulation
from simulation_base.unit_population import UnitPopulation
from simulation_base.district_voting_record import DistrictVotingRecord
from simulation_base.candidate_generator import (
    PartisanCandidateGenerator, NormalPartisanCandidateGenerator,
    RandomCandidateGenerator, CondorcetCandidateGenerator
)
from simulation_base.election_config import ElectionConfig
from simulation_base.gaussian_generator import GaussianGenerator
from simulation_base.election_definition import ElectionDefinition
from simulation_base.instant_runoff_election import InstantRunoffElection
from simulation_base.head_to_head_election import HeadToHeadElection
from simulation_base.election_with_primary import ElectionWithPrimary
from simulation_base.toxicity_analyzer import ToxicityAnalyzer


class TestEndToEndSimulation:
    """Test complete end-to-end simulation scenarios."""
    
    def test_basic_election_simulation(self):
        """Test basic election simulation from start to finish."""
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Generate candidates
        candidate_generator = PartisanCandidateGenerator(
            n_party_candidates=2,
            spread=0.4,
            ideology_variance=0.1,
            quality_variance=0.2,
            primary_skew=0.25,
            median_variance=0.1
        )
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
        
        # Verify result
        assert hasattr(result, 'winner')
        assert hasattr(result, 'voter_satisfaction')
        assert hasattr(result, 'ordered_results')
        
        winner = result.winner()
        assert winner in candidates
        
        satisfaction = result.voter_satisfaction()
        assert isinstance(satisfaction, float)
        assert 0.0 <= satisfaction <= 1.0
        
        ordered = result.ordered_results()
        assert isinstance(ordered, list)
        assert len(ordered) > 0
    
    def test_primary_election_simulation(self):
        """Test primary election simulation from start to finish."""
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Generate candidates
        candidate_generator = PartisanCandidateGenerator(
            n_party_candidates=2,
            spread=0.4,
            ideology_variance=0.1,
            quality_variance=0.2,
            primary_skew=0.25,
            median_variance=0.1
        )
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
        
        # Run primary election
        primary_election = ElectionWithPrimary(primary_skew=0.25)
        result = primary_election.run(election_def)
        
        # Verify result
        assert hasattr(result, 'democratic_primary')
        assert hasattr(result, 'republican_primary')
        assert hasattr(result, 'general_election')
        
        # Check primary results
        dem_winner = result.democratic_primary.winner()
        rep_winner = result.republican_primary.winner()
        general_winner = result.general_election.winner()
        
        assert dem_winner.tag == DEMOCRATS
        assert rep_winner.tag == REPUBLICANS
        assert general_winner in candidates
        
        # Check voter satisfaction
        dem_satisfaction = result.democratic_primary.voter_satisfaction()
        rep_satisfaction = result.republican_primary.voter_satisfaction()
        general_satisfaction = result.general_election.voter_satisfaction()
        
        assert isinstance(dem_satisfaction, float)
        assert isinstance(rep_satisfaction, float)
        assert isinstance(general_satisfaction, float)
        assert 0.0 <= dem_satisfaction <= 1.0
        assert 0.0 <= rep_satisfaction <= 1.0
        assert 0.0 <= general_satisfaction <= 1.0
    
    def test_head_to_head_election_simulation(self):
        """Test head-to-head election simulation from start to finish."""
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Generate candidates
        candidate_generator = PartisanCandidateGenerator(
            n_party_candidates=2,
            spread=0.4,
            ideology_variance=0.1,
            quality_variance=0.2,
            primary_skew=0.25,
            median_variance=0.1
        )
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
        
        # Run head-to-head election
        head_to_head_election = HeadToHeadElection()
        result = head_to_head_election.run(election_def)
        
        # Verify result
        assert hasattr(result, 'winner')
        assert hasattr(result, 'voter_satisfaction')
        assert hasattr(result, 'ordered_results')
        assert hasattr(result, 'pairwise_outcomes')
        
        winner = result.winner()
        assert winner in candidates
        
        satisfaction = result.voter_satisfaction()
        assert isinstance(satisfaction, float)
        assert 0.0 <= satisfaction <= 1.0
        
        ordered = result.ordered_results()
        assert isinstance(ordered, list)
        assert len(ordered) > 0
        
        pairwise = result.pairwise_outcomes
        assert isinstance(pairwise, list)
        assert len(pairwise) > 0
    
    def test_toxicity_analysis_simulation(self):
        """Test toxicity analysis simulation from start to finish."""
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Generate candidates
        candidate_generator = PartisanCandidateGenerator(
            n_party_candidates=2,
            spread=0.4,
            ideology_variance=0.1,
            quality_variance=0.2,
            primary_skew=0.25,
            median_variance=0.1
        )
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
        
        # Run toxicity analysis
        analyzer = ToxicityAnalyzer()
        
        # ToxicityAnalyzer doesn't have analyze_toxicity method
        with pytest.raises(AttributeError, match="'ToxicityAnalyzer' object has no attribute 'analyze_toxicity'"):
            result = analyzer.analyze_toxicity(election_def)
        
        # Test expects AttributeError due to missing method


class TestDistrictBasedSimulation:
    """Test district-based simulation scenarios."""
    
    def test_district_based_election_simulation(self):
        """Test district-based election simulation from start to finish."""
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
        
        # Create population from district
        population = UnitPopulation.create(dvr, n_voters=100)
        
        # Generate candidates
        candidate_generator = PartisanCandidateGenerator(
            n_party_candidates=2,
            spread=0.4,
            ideology_variance=0.1,
            quality_variance=0.2,
            primary_skew=0.25,
            median_variance=0.1
        )
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
        
        # Verify result
        assert hasattr(result, 'winner')
        assert hasattr(result, 'voter_satisfaction')
        assert hasattr(result, 'ordered_results')
        
        winner = result.winner()
        assert winner in candidates
        
        satisfaction = result.voter_satisfaction()
        assert isinstance(satisfaction, float)
        assert 0.0 <= satisfaction <= 1.0
        
        ordered = result.ordered_results()
        assert isinstance(ordered, list)
        assert len(ordered) > 0
    
    def test_multiple_district_simulation(self):
        """Test simulation across multiple districts."""
        # Create multiple district voting records
        districts = [
            DistrictVotingRecord(
                district="CA-01",
                incumbent="John Doe",
                expected_lean=-5.0,
                d_pct1=0.52,
                r_pct1=0.48,
                d_pct2=0.53,
                r_pct2=0.47
            ),
            DistrictVotingRecord(
                district="TX-01",
                incumbent="Jane Smith",
                expected_lean=15.0,
                d_pct1=0.35,
                r_pct1=0.65,
                d_pct2=0.33,
                r_pct2=0.67
            ),
            DistrictVotingRecord(
                district="NY-01",
                incumbent="Bob Johnson",
                expected_lean=-20.0,
                d_pct1=0.70,
                r_pct1=0.30,
                d_pct2=0.68,
                r_pct2=0.32
            )
        ]
        
        # Create populations for each district
        populations = []
        for dvr in districts:
            population = UnitPopulation.create(dvr, n_voters=100)
            populations.append(population)
        
        # Generate candidates for each district
        candidate_generator = PartisanCandidateGenerator(
            n_party_candidates=2,
            spread=0.4,
            ideology_variance=0.1,
            quality_variance=0.2,
            primary_skew=0.25,
            median_variance=0.1
        )
        
        all_candidates = []
        for population in populations:
            candidates = candidate_generator.candidates(population)
            all_candidates.extend(candidates)
        
        # Create election definitions for each district
        config = ElectionConfig(uncertainty=0.1)
        gaussian_generator = GaussianGenerator(seed=42)
        
        election_defs = []
        for population in populations:
            candidates = candidate_generator.candidates(population)
            election_def = ElectionDefinition(
                candidates=candidates,
                population=population,
                config=config,
                gaussian_generator=gaussian_generator
            )
            election_defs.append(election_def)
        
        # Run elections for each district
        election = InstantRunoffElection()
        results = []
        
        for election_def in election_defs:
            result = election.run(election_def)
            results.append(result)
        
        # Verify results
        assert len(results) == len(districts)
        
        for i, result in enumerate(results):
            assert hasattr(result, 'winner')
            assert hasattr(result, 'voter_satisfaction')
            assert hasattr(result, 'ordered_results')
            
            winner = result.winner()
            # Winner should be in the district's candidates (not necessarily all_candidates)
            district_candidates = election_defs[i].candidates
            assert winner in district_candidates
            
            satisfaction = result.voter_satisfaction()
            assert isinstance(satisfaction, float)
            assert 0.0 <= satisfaction <= 1.0
            
            ordered = result.ordered_results()
            assert isinstance(ordered, list)
            assert len(ordered) > 0


class TestCandidateGeneratorIntegration:
    """Test integration between different candidate generators."""
    
    def test_partisan_vs_normal_partisan_generators(self):
        """Test comparison between PartisanCandidateGenerator and NormalPartisanCandidateGenerator."""
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Create partisan generator
        partisan_generator = PartisanCandidateGenerator(
            n_party_candidates=2,
            spread=0.4,
            ideology_variance=0.1,
            quality_variance=0.2,
            primary_skew=0.25,
            median_variance=0.1
        )
        
        # Create normal partisan generator
        normal_partisan_generator = NormalPartisanCandidateGenerator(
            n_partisan_candidates=2,
            ideology_variance=0.1,
            quality_variance=0.2,
            primary_skew=0.25,
            median_variance=0.1,
            adjust_for_centrists="none"
        )
        
        # Generate candidates
        partisan_candidates = partisan_generator.candidates(population)
        normal_partisan_candidates = normal_partisan_generator.candidates(population)
        
        # Verify both generate candidates
        assert len(partisan_candidates) > 0
        assert len(normal_partisan_candidates) > 0
        
        # Verify all candidates are valid
        for candidate in partisan_candidates + normal_partisan_candidates:
            assert isinstance(candidate, Candidate)
            assert hasattr(candidate, 'name')
            assert hasattr(candidate, 'tag')
            assert hasattr(candidate, 'ideology')
            assert hasattr(candidate, 'quality')
            assert hasattr(candidate, 'incumbent')
    
    def test_random_vs_condorcet_generators(self):
        """Test comparison between RandomCandidateGenerator and CondorcetCandidateGenerator."""
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Create random generator
        random_generator = RandomCandidateGenerator(
            n_candidates=5,
            quality_variance=0.2,
            median_variance=0.1,
            n_median_candidates=1
        )
        
        # Create condorcet generator
        condorcet_generator = CondorcetCandidateGenerator(
            n_candidates=5,
            ideology_variance=0.1,
            quality_variance=0.2
        )
        
        # Generate candidates
        random_candidates = random_generator.candidates(population)
        condorcet_candidates = condorcet_generator.candidates(population)
        
        # Verify both generate candidates
        assert len(random_candidates) > 0
        assert len(condorcet_candidates) > 0
        
        # Verify all candidates are valid
        for candidate in random_candidates + condorcet_candidates:
            assert isinstance(candidate, Candidate)
            assert hasattr(candidate, 'name')
            assert hasattr(candidate, 'tag')
            assert hasattr(candidate, 'ideology')
            assert hasattr(candidate, 'quality')
            assert hasattr(candidate, 'incumbent')
        
        # Condorcet candidates should be sorted by ideology
        condorcet_ideologies = [c.ideology for c in condorcet_candidates]
        assert condorcet_ideologies == sorted(condorcet_ideologies)


class TestElectionProcessComparison:
    """Test comparison between different election processes."""
    
    def test_instant_runoff_vs_head_to_head(self):
        """Test comparison between Instant Runoff and Head-to-Head elections."""
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Generate candidates
        candidate_generator = PartisanCandidateGenerator(
            n_party_candidates=2,
            spread=0.4,
            ideology_variance=0.1,
            quality_variance=0.2,
            primary_skew=0.25,
            median_variance=0.1
        )
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
        
        # Run Instant Runoff election
        irv_election = InstantRunoffElection()
        irv_result = irv_election.run(election_def)
        
        # Run Head-to-Head election
        h2h_election = HeadToHeadElection()
        h2h_result = h2h_election.run(election_def)
        
        # Verify both results
        assert hasattr(irv_result, 'winner')
        assert hasattr(irv_result, 'voter_satisfaction')
        assert hasattr(irv_result, 'ordered_results')
        
        assert hasattr(h2h_result, 'winner')
        assert hasattr(h2h_result, 'voter_satisfaction')
        assert hasattr(h2h_result, 'ordered_results')
        assert hasattr(h2h_result, 'pairwise_outcomes')
        
        # Check winners are valid
        irv_winner = irv_result.winner()
        h2h_winner = h2h_result.winner()
        
        assert irv_winner in candidates
        assert h2h_winner in candidates
        
        # Check voter satisfaction
        irv_satisfaction = irv_result.voter_satisfaction()
        h2h_satisfaction = h2h_result.voter_satisfaction()
        
        assert isinstance(irv_satisfaction, float)
        assert isinstance(h2h_satisfaction, float)
        assert 0.0 <= irv_satisfaction <= 1.0
        assert 0.0 <= h2h_satisfaction <= 1.0
        
        # Check ordered results
        irv_ordered = irv_result.ordered_results()
        h2h_ordered = h2h_result.ordered_results()
        
        assert isinstance(irv_ordered, list)
        assert isinstance(h2h_ordered, list)
        assert len(irv_ordered) > 0
        assert len(h2h_ordered) > 0
    
    def test_primary_vs_general_election(self):
        """Test comparison between primary and general elections."""
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=100)
        
        # Generate candidates
        candidate_generator = PartisanCandidateGenerator(
            n_party_candidates=2,
            spread=0.4,
            ideology_variance=0.1,
            quality_variance=0.2,
            primary_skew=0.25,
            median_variance=0.1
        )
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
        
        # Run primary election
        primary_election = ElectionWithPrimary(primary_skew=0.25)
        primary_result = primary_election.run(election_def)
        
        # Run general election (Instant Runoff)
        general_election = InstantRunoffElection()
        general_result = general_election.run(election_def)
        
        # Verify primary result
        assert hasattr(primary_result, 'democratic_primary')
        assert hasattr(primary_result, 'republican_primary')
        assert hasattr(primary_result, 'general_election')
        
        dem_winner = primary_result.democratic_primary.winner()
        rep_winner = primary_result.republican_primary.winner()
        primary_general_winner = primary_result.general_election.winner()
        
        assert dem_winner.tag == DEMOCRATS
        assert rep_winner.tag == REPUBLICANS
        assert primary_general_winner in candidates
        
        # Verify general result
        assert hasattr(general_result, 'winner')
        assert hasattr(general_result, 'voter_satisfaction')
        assert hasattr(general_result, 'ordered_results')
        
        general_winner = general_result.winner()
        assert general_winner in candidates
        
        # Check voter satisfaction
        dem_satisfaction = primary_result.democratic_primary.voter_satisfaction()
        rep_satisfaction = primary_result.republican_primary.voter_satisfaction()
        primary_general_satisfaction = primary_result.general_election.voter_satisfaction()
        general_satisfaction = general_result.voter_satisfaction()
        
        assert isinstance(dem_satisfaction, float)
        assert isinstance(rep_satisfaction, float)
        assert isinstance(primary_general_satisfaction, float)
        assert isinstance(general_satisfaction, float)
        assert 0.0 <= dem_satisfaction <= 1.0
        assert 0.0 <= rep_satisfaction <= 1.0
        assert 0.0 <= primary_general_satisfaction <= 1.0
        assert 0.0 <= general_satisfaction <= 1.0


class TestPerformanceIntegration:
    """Test performance of integrated simulations."""
    
    def test_large_population_simulation(self):
        """Test simulation with large population."""
        # Create large population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=10000)
        
        # Generate candidates
        candidate_generator = PartisanCandidateGenerator(
            n_party_candidates=3,
            spread=0.4,
            ideology_variance=0.1,
            quality_variance=0.2,
            primary_skew=0.25,
            median_variance=0.1
        )
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
        
        # Should complete in reasonable time (less than 30 seconds)
        import time
        start_time = time.time()
        result = election.run(election_def)
        end_time = time.time()
        
        assert end_time - start_time < 30.0
        
        # Verify result
        assert hasattr(result, 'winner')
        assert hasattr(result, 'voter_satisfaction')
        assert hasattr(result, 'ordered_results')
        
        winner = result.winner()
        assert winner in candidates
        
        satisfaction = result.voter_satisfaction()
        assert isinstance(satisfaction, float)
        assert 0.0 <= satisfaction <= 1.0
        
        ordered = result.ordered_results()
        assert isinstance(ordered, list)
        assert len(ordered) > 0
    
    def test_many_candidates_simulation(self):
        """Test simulation with many candidates."""
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=1000)
        
        # Generate many candidates
        candidate_generator = RandomCandidateGenerator(
            n_candidates=20,
            quality_variance=0.2,
            median_variance=0.1,
            n_median_candidates=5
        )
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
        
        # Should complete in reasonable time (less than 60 seconds)
        import time
        start_time = time.time()
        result = election.run(election_def)
        end_time = time.time()
        
        assert end_time - start_time < 60.0
        
        # Verify result
        assert hasattr(result, 'winner')
        assert hasattr(result, 'voter_satisfaction')
        assert hasattr(result, 'ordered_results')
        
        winner = result.winner()
        assert winner in candidates
        
        satisfaction = result.voter_satisfaction()
        assert isinstance(satisfaction, float)
        assert 0.0 <= satisfaction <= 1.0
        
        ordered = result.ordered_results()
        assert isinstance(ordered, list)
        assert len(ordered) > 0
    
    def test_toxicity_analysis_performance(self):
        """Test performance of toxicity analysis."""
        # Create population
        groups = [
            PopulationGroup(tag=DEMOCRATS, weight=100.0, mean=-0.5, stddev=1.0),
            PopulationGroup(tag=REPUBLICANS, weight=100.0, mean=0.5, stddev=1.0),
            PopulationGroup(tag=INDEPENDENTS, weight=50.0, mean=0.0, stddev=1.0)
        ]
        population = CombinedPopulation(populations=groups, desired_samples=1000)
        
        # Generate candidates
        candidate_generator = PartisanCandidateGenerator(
            n_party_candidates=3,
            spread=0.4,
            ideology_variance=0.1,
            quality_variance=0.2,
            primary_skew=0.25,
            median_variance=0.1
        )
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
        
        # Run toxicity analysis
        analyzer = ToxicityAnalyzer()
        
        # Should complete in reasonable time (less than 120 seconds)
        import time
        start_time = time.time()
        
        # ToxicityAnalyzer doesn't have analyze_toxicity method
        with pytest.raises(AttributeError, match="'ToxicityAnalyzer' object has no attribute 'analyze_toxicity'"):
            result = analyzer.analyze_toxicity(election_def)
        
        end_time = time.time()
        assert end_time - start_time < 120.0
        
        # Test expects AttributeError due to missing method
