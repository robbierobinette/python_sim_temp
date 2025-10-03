"""
Tests for Candidate class.
"""
import pytest
from simulation_base.candidate import Candidate
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS


class TestCandidate:
    """Test Candidate class functionality."""
    
    def test_candidate_creation(self):
        """Test creating a Candidate."""
        candidate = Candidate(
            name="Alice",
            tag=DEMOCRATS,
            ideology=-0.5,
            quality=0.8,
            incumbent=False
        )
        
        assert candidate.name == "Alice"
        assert candidate.tag == DEMOCRATS
        assert candidate.ideology == -0.5
        assert candidate.quality == 0.8
        assert candidate.incumbent == False
    
    def test_candidate_creation_with_incumbent(self):
        """Test creating an incumbent Candidate."""
        candidate = Candidate(
            name="Bob",
            tag=REPUBLICANS,
            ideology=0.3,
            quality=0.6,
            incumbent=True
        )
        
        assert candidate.incumbent == True
    
    def test_affinity_initialization(self):
        """Test that affinity map is initialized from tag."""
        candidate = Candidate(
            name="Charlie",
            tag=DEMOCRATS,
            ideology=0.0,
            quality=0.5,
            incumbent=False
        )
        
        # Should have the same affinity as DEMOCRATS
        assert candidate._affinity_map == DEMOCRATS.affinity
        assert candidate.affinity("Dem") == 1.0
        assert candidate.affinity("Rep") == 0.0
        assert candidate.affinity("Ind") == 0.5
    
    def test_affinity_method(self):
        """Test the affinity method."""
        candidate = Candidate(
            name="David",
            tag=REPUBLICANS,
            ideology=0.2,
            quality=0.7,
            incumbent=False
        )
        
        assert candidate.affinity("Rep") == 1.0
        assert candidate.affinity("Dem") == 0.0
        assert candidate.affinity("Ind") == 0.5
    
    def test_affinity_key_error(self):
        """Test that affinity raises KeyError for unknown groups."""
        candidate = Candidate(
            name="Eve",
            tag=INDEPENDENTS,
            ideology=0.0,
            quality=0.5,
            incumbent=False
        )
        
        with pytest.raises(KeyError) as exc_info:
            candidate.affinity("Unknown")
        
        assert "Unknown group 'Unknown'" in str(exc_info.value)
        assert "Available groups:" in str(exc_info.value)
    
    def test_affinity_string(self):
        """Test the affinity_string method."""
        candidate = Candidate(
            name="Frank",
            tag=DEMOCRATS,
            ideology=-0.3,
            quality=0.6,
            incumbent=False
        )
        
        affinity_str = candidate.affinity_string()
        # The actual format uses 5-character field width for keys
        assert "Dem  :   1.00" in affinity_str
        assert "Rep  :   0.00" in affinity_str
        assert "Ind  :   0.50" in affinity_str
    
    def test_hash_functionality(self):
        """Test hash functionality for use in sets and dicts."""
        candidate1 = Candidate(
            name="Alice",
            tag=DEMOCRATS,
            ideology=-0.5,
            quality=0.8,
            incumbent=False
        )
        
        candidate2 = Candidate(
            name="Alice",
            tag=DEMOCRATS,
            ideology=-0.5,
            quality=0.8,
            incumbent=False
        )
        
        # Same candidate should have same hash
        assert hash(candidate1) == hash(candidate2)
        
        # Different candidates should have different hashes
        candidate3 = Candidate(
            name="Bob",
            tag=DEMOCRATS,
            ideology=-0.5,
            quality=0.8,
            incumbent=False
        )
        assert hash(candidate1) != hash(candidate3)
        
        # Test that candidates can be used in sets
        candidate_set = {candidate1, candidate2, candidate3}
        assert len(candidate_set) == 2  # candidate1 and candidate2 are the same
        assert candidate1 in candidate_set
        assert candidate3 in candidate_set
    
    def test_hash_with_different_affinity(self):
        """Test that hash changes when affinity changes."""
        candidate1 = Candidate(
            name="Alice",
            tag=DEMOCRATS,
            ideology=-0.5,
            quality=0.8,
            incumbent=False
        )
        
        candidate2 = Candidate(
            name="Alice",
            tag=DEMOCRATS,
            ideology=-0.5,
            quality=0.8,
            incumbent=False
        )
        
        # Modify affinity of candidate2
        candidate2._affinity_map["Dem"] = 0.9
        
        # Hashes should be different
        assert hash(candidate1) != hash(candidate2)
    
    def test_equality(self):
        """Test candidate equality."""
        candidate1 = Candidate(
            name="Alice",
            tag=DEMOCRATS,
            ideology=-0.5,
            quality=0.8,
            incumbent=False
        )
        
        candidate2 = Candidate(
            name="Alice",
            tag=DEMOCRATS,
            ideology=-0.5,
            quality=0.8,
            incumbent=False
        )
        
        # Same candidates should be equal
        assert candidate1 == candidate2
        
        # Different candidates should not be equal
        candidate3 = Candidate(
            name="Bob",
            tag=DEMOCRATS,
            ideology=-0.5,
            quality=0.8,
            incumbent=False
        )
        assert candidate1 != candidate3


class TestCandidateEdgeCases:
    """Test edge cases for Candidate."""
    
    def test_extreme_ideology_values(self):
        """Test candidate with extreme ideology values."""
        candidate = Candidate(
            name="Extreme",
            tag=REPUBLICANS,
            ideology=1000.0,
            quality=0.5,
            incumbent=False
        )
        
        assert candidate.ideology == 1000.0
        assert candidate.affinity("Rep") == 1.0
    
    def test_negative_quality(self):
        """Test candidate with negative quality."""
        candidate = Candidate(
            name="Negative",
            tag=INDEPENDENTS,
            ideology=0.0,
            quality=-0.5,
            incumbent=False
        )
        
        assert candidate.quality == -0.5
    
    def test_zero_quality(self):
        """Test candidate with zero quality."""
        candidate = Candidate(
            name="Zero",
            tag=DEMOCRATS,
            ideology=0.0,
            quality=0.0,
            incumbent=False
        )
        
        assert candidate.quality == 0.0
    
    def test_very_long_name(self):
        """Test candidate with very long name."""
        long_name = "A" * 1000
        candidate = Candidate(
            name=long_name,
            tag=REPUBLICANS,
            ideology=0.0,
            quality=0.5,
            incumbent=False
        )
        
        assert candidate.name == long_name
        assert len(candidate.name) == 1000
    
    def test_unicode_name(self):
        """Test candidate with unicode name."""
        unicode_name = "候选人"
        candidate = Candidate(
            name=unicode_name,
            tag=DEMOCRATS,
            ideology=0.0,
            quality=0.5,
            incumbent=False
        )
        
        assert candidate.name == unicode_name
    
    def test_custom_affinity_map(self):
        """Test candidate with custom affinity map."""
        custom_affinity = {"Custom": 1.0, "Other": 0.0}
        candidate = Candidate(
            name="Custom",
            tag=DEMOCRATS,
            ideology=0.0,
            quality=0.5,
            incumbent=False
        )
        
        # Override the affinity map
        candidate._affinity_map = custom_affinity
        
        assert candidate.affinity("Custom") == 1.0
        assert candidate.affinity("Other") == 0.0
        
        with pytest.raises(KeyError):
            candidate.affinity("Dem")


class TestCandidateWithDifferentParties:
    """Test Candidate with different party tags."""
    
    @pytest.mark.parametrize("party,expected_affinity", [
        (DEMOCRATS, {"Rep": 0.0, "Ind": 0.5, "Dem": 1.0}),
        (REPUBLICANS, {"Rep": 1.0, "Ind": 0.5, "Dem": 0.0}),
        (INDEPENDENTS, {"Rep": 0.0, "Ind": 0.5, "Dem": 0.0})
    ])
    def test_candidate_with_different_parties(self, party, expected_affinity):
        """Test candidate creation with different parties."""
        candidate = Candidate(
            name="Test",
            tag=party,
            ideology=0.0,
            quality=0.5,
            incumbent=False
        )
        
        assert candidate._affinity_map == expected_affinity
        assert candidate.tag == party
    
    def test_candidate_affinity_consistency(self):
        """Test that candidate affinity is consistent with party affinity."""
        for party in [DEMOCRATS, REPUBLICANS, INDEPENDENTS]:
            candidate = Candidate(
                name=f"Test-{party.short_name}",
                tag=party,
                ideology=0.0,
                quality=0.5,
                incumbent=False
            )
            
            # Test that candidate affinity matches party affinity
            for other_party in [DEMOCRATS, REPUBLICANS, INDEPENDENTS]:
                expected_affinity = party.party_affinity(other_party)
                actual_affinity = candidate.affinity(other_party.short_name)
                assert actual_affinity == expected_affinity

