"""
Test configuration and fixtures for simulation_base tests.
"""
import pytest
import random
from typing import List, Dict, Any
from simulation_base.population_tag import PopulationTag, DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.candidate import Candidate
from simulation_base.voter import Voter
from simulation_base.population_group import PopulationGroup
from simulation_base.combined_population import CombinedPopulation
from simulation_base.election_config import ElectionConfig
from simulation_base.gaussian_generator import GaussianGenerator
from simulation_base.ballot import RCVBallot, CandidateScore
from simulation_base.district_voting_record import DistrictVotingRecord


@pytest.fixture
def mock_gaussian_generator():
    """Mock Gaussian generator for deterministic testing."""
    class MockGaussianGenerator:
        def __init__(self, values=None):
            self.values = values or [0.0] * 1000  # Default to zeros
            self.index = 0
        
        def __call__(self):
            if self.index < len(self.values):
                value = self.values[self.index]
                self.index += 1
                return value
            return 0.0
        
        def next_boolean(self):
            return self.__call__() > 0.0
        
        def next_int(self):
            return int(self.__call__() * 1000)
        
        def set_seed(self, seed):
            pass
    
    return MockGaussianGenerator()


@pytest.fixture
def deterministic_gaussian_generator():
    """Deterministic Gaussian generator with known values."""
    return MockGaussianGenerator([0.1, -0.2, 0.3, -0.4, 0.5, -0.6, 0.7, -0.8, 0.9, -1.0])


@pytest.fixture
def sample_population_tags():
    """Sample population tags for testing."""
    return {
        'democrats': DEMOCRATS,
        'republicans': REPUBLICANS,
        'independents': INDEPENDENTS
    }


@pytest.fixture
def sample_candidates():
    """Sample candidates for testing."""
    return [
        Candidate(
            name="Alice",
            tag=DEMOCRATS,
            ideology=-0.5,
            quality=0.8,
            incumbent=False
        ),
        Candidate(
            name="Bob",
            tag=REPUBLICANS,
            ideology=0.3,
            quality=0.6,
            incumbent=True
        ),
        Candidate(
            name="Charlie",
            tag=INDEPENDENTS,
            ideology=0.0,
            quality=0.7,
            incumbent=False
        )
    ]


@pytest.fixture
def sample_population_groups():
    """Sample population groups for testing."""
    return [
        PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1.0,
            mean=-0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        ),
        PopulationGroup(
            tag=REPUBLICANS,
            party_bonus=1.0,
            mean=0.5,
            stddev=1.0,
            skew=0.0,
            weight=100.0
        ),
        PopulationGroup(
            tag=INDEPENDENTS,
            party_bonus=0.5,
            mean=0.0,
            stddev=1.0,
            skew=0.0,
            weight=50.0
        )
    ]


@pytest.fixture
def sample_combined_population(sample_population_groups):
    """Sample combined population for testing."""
    return CombinedPopulation(
        populations=sample_population_groups,
        desired_samples=100
    )


@pytest.fixture
def sample_voters(sample_population_groups):
    """Sample voters for testing."""
    return [
        Voter(party=sample_population_groups[0], ideology=-0.3),
        Voter(party=sample_population_groups[1], ideology=0.4),
        Voter(party=sample_population_groups[2], ideology=0.1)
    ]


@pytest.fixture
def sample_election_config():
    """Sample election configuration for testing."""
    return ElectionConfig(uncertainty=0.1)


@pytest.fixture
def sample_ballots(sample_candidates, sample_voters, sample_election_config, mock_gaussian_generator):
    """Sample ballots for testing."""
    ballots = []
    for voter in sample_voters:
        ballot = voter.ballot(sample_candidates, sample_election_config, mock_gaussian_generator)
        ballots.append(ballot)
    return ballots


@pytest.fixture
def sample_district_voting_record():
    """Sample district voting record for testing."""
    return DistrictVotingRecord(
        district="CA-01",
        incumbent="John Doe",
        expected_lean=-5.0,
        d_pct1=0.52,
        r_pct1=0.48,
        d_pct2=0.53,
        r_pct2=0.47
    )


@pytest.fixture
def empty_candidates():
    """Empty candidate list for edge case testing."""
    return []


@pytest.fixture
def single_candidate():
    """Single candidate for edge case testing."""
    return [Candidate(
        name="Solo",
        tag=INDEPENDENTS,
        ideology=0.0,
        quality=0.5,
        incumbent=False
    )]


@pytest.fixture
def tied_candidates():
    """Candidates with identical scores for tie-breaking testing."""
    return [
        Candidate(
            name="Tie1",
            tag=DEMOCRATS,
            ideology=-0.1,
            quality=0.5,
            incumbent=False
        ),
        Candidate(
            name="Tie2",
            tag=DEMOCRATS,
            ideology=-0.1,
            quality=0.5,
            incumbent=False
        )
    ]


class TestDataGenerator:
    """Helper class for generating test data."""
    
    @staticmethod
    def create_candidates(count: int, party: PopulationTag, ideology_range: tuple = (-1.0, 1.0)) -> List[Candidate]:
        """Create a list of candidates with specified parameters."""
        candidates = []
        for i in range(count):
            ideology = random.uniform(ideology_range[0], ideology_range[1])
            candidate = Candidate(
                name=f"{party.short_name}-{i+1}",
                tag=party,
                ideology=ideology,
                quality=random.uniform(0.0, 1.0),
                incumbent=random.choice([True, False])
            )
            candidates.append(candidate)
        return candidates
    
    @staticmethod
    def create_voters(count: int, population_group: PopulationGroup) -> List[Voter]:
        """Create a list of voters from a population group."""
        voters = []
        for _ in range(count):
            ideology = random.gauss(population_group.mean, population_group.stddev)
            voter = Voter(party=population_group, ideology=ideology)
            voters.append(voter)
        return voters
    
    @staticmethod
    def create_population_groups() -> List[PopulationGroup]:
        """Create standard population groups for testing."""
        return [
            PopulationGroup(
                tag=DEMOCRATS,
                party_bonus=1.0,
                mean=-0.5,
                stddev=1.0,
                skew=0.0,
                weight=100.0
            ),
            PopulationGroup(
                tag=REPUBLICANS,
                party_bonus=1.0,
                mean=0.5,
                stddev=1.0,
                skew=0.0,
                weight=100.0
            ),
            PopulationGroup(
                tag=INDEPENDENTS,
                party_bonus=0.5,
                mean=0.0,
                stddev=1.0,
                skew=0.0,
                weight=50.0
            )
        ]


@pytest.fixture
def test_data_generator():
    """Test data generator fixture."""
    return TestDataGenerator()


# Test utilities
def assert_candidate_result_valid(result, expected_candidate=None):
    """Assert that a candidate result is valid."""
    assert hasattr(result, 'candidate')
    assert hasattr(result, 'votes')
    assert isinstance(result.votes, (int, float))
    assert result.votes >= 0
    
    if expected_candidate:
        assert result.candidate == expected_candidate


def assert_election_result_valid(result, expected_winner=None):
    """Assert that an election result is valid."""
    assert hasattr(result, 'winner')
    assert hasattr(result, 'voter_satisfaction')
    assert hasattr(result, 'ordered_results')
    
    winner = result.winner()
    assert winner is not None
    
    if expected_winner:
        assert winner == expected_winner
    
    ordered_results = result.ordered_results()
    assert isinstance(ordered_results, list)
    assert len(ordered_results) > 0
    
    # Check that results are ordered by votes (descending)
    for i in range(len(ordered_results) - 1):
        assert ordered_results[i].votes >= ordered_results[i + 1].votes


def assert_ballot_valid(ballot, expected_candidates=None):
    """Assert that a ballot is valid."""
    assert hasattr(ballot, 'sorted_candidates')
    assert isinstance(ballot.sorted_candidates, list)
    
    if expected_candidates:
        assert len(ballot.sorted_candidates) == len(expected_candidates)
        ballot_candidates = [cs.candidate for cs in ballot.sorted_candidates]
        for candidate in expected_candidates:
            assert candidate in ballot_candidates


def assert_population_valid(population, expected_groups=None):
    """Assert that a population is valid."""
    assert hasattr(population, 'voters')
    assert isinstance(population.voters, list)
    assert len(population.voters) > 0
    
    if expected_groups:
        assert hasattr(population, 'populations')
        assert len(population.populations) == len(expected_groups)

