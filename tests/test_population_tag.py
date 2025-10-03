"""
Tests for PopulationTag class.
"""
import pytest
from simulation_base.population_tag import PopulationTag, DEMOCRATS, REPUBLICANS, INDEPENDENTS, get_party_by_short_name


class TestPopulationTag:
    """Test PopulationTag class functionality."""
    
    def test_population_tag_creation(self):
        """Test creating a PopulationTag."""
        tag = PopulationTag(
            name="Test Party",
            short_name="Test",
            plural_name="Testers",
            hex_color="#ff0000",
            affinity={"Test": 1.0, "Other": 0.0}
        )
        
        assert tag.name == "Test Party"
        assert tag.short_name == "Test"
        assert tag.plural_name == "Testers"
        assert tag.hex_color == "#ff0000"
        assert tag.affinity == {"Test": 1.0, "Other": 0.0}
    
    def test_initial_property(self):
        """Test the initial property."""
        assert DEMOCRATS.initial == "D"
        assert REPUBLICANS.initial == "R"
        assert INDEPENDENTS.initial == "I"
    
    def test_party_affinity(self):
        """Test party affinity calculation."""
        # Test existing affinity
        assert DEMOCRATS.party_affinity(REPUBLICANS) == 0.0
        assert DEMOCRATS.party_affinity(DEMOCRATS) == 1.0
        assert DEMOCRATS.party_affinity(INDEPENDENTS) == 0.5
        
        # Test non-existing affinity (should return 0.0)
        fake_party = PopulationTag("Fake", "Fake", "Fakes", "#000000", {})
        assert DEMOCRATS.party_affinity(fake_party) == 0.0
    
    def test_string_representation(self):
        """Test string representation."""
        assert str(DEMOCRATS) == "Democratic"
        assert str(REPUBLICANS) == "Republican"
        assert str(INDEPENDENTS) == "Independent"
    
    def test_less_than_comparison(self):
        """Test less than comparison."""
        assert DEMOCRATS < REPUBLICANS  # "Dem" < "Rep"
        assert not (REPUBLICANS < INDEPENDENTS)  # "Rep" > "Ind" alphabetically
        assert not (DEMOCRATS < DEMOCRATS)  # Equal tags
    
    def test_hash_functionality(self):
        """Test hash functionality for use in sets and dicts."""
        # Same tag should have same hash
        tag1 = PopulationTag("Test", "T", "Tests", "#ff0000", {"T": 1.0})
        tag2 = PopulationTag("Test", "T", "Tests", "#ff0000", {"T": 1.0})
        assert hash(tag1) == hash(tag2)
        
        # Different tags should have different hashes
        tag3 = PopulationTag("Test", "T", "Tests", "#ff0000", {"T": 0.5})
        assert hash(tag1) != hash(tag3)
        
        # Test that tags can be used in sets
        tag_set = {DEMOCRATS, REPUBLICANS, INDEPENDENTS}
        assert len(tag_set) == 3
        assert DEMOCRATS in tag_set
    
    def test_standard_parties(self):
        """Test the standard party definitions."""
        # Test Democrats
        assert DEMOCRATS.name == "Democratic"
        assert DEMOCRATS.short_name == "Dem"
        assert DEMOCRATS.plural_name == "Democrats"
        assert DEMOCRATS.hex_color == "#0000ff"
        assert DEMOCRATS.affinity == {"Rep": 0.0, "Ind": 0.5, "Dem": 1.0}
        
        # Test Republicans
        assert REPUBLICANS.name == "Republican"
        assert REPUBLICANS.short_name == "Rep"
        assert REPUBLICANS.plural_name == "Republicans"
        assert REPUBLICANS.hex_color == "#ff0000"
        assert REPUBLICANS.affinity == {"Rep": 1.0, "Ind": 0.5, "Dem": 0.0}
        
        # Test Independents
        assert INDEPENDENTS.name == "Independent"
        assert INDEPENDENTS.short_name == "Ind"
        assert INDEPENDENTS.plural_name == "Independents"
        assert INDEPENDENTS.hex_color == "#ff00ff"
        assert INDEPENDENTS.affinity == {"Rep": 0.0, "Ind": 0.5, "Dem": 0.0}


class TestGetPartyByShortName:
    """Test get_party_by_short_name function."""
    
    def test_get_existing_parties(self):
        """Test getting existing parties by short name."""
        assert get_party_by_short_name("Dem") == DEMOCRATS
        assert get_party_by_short_name("Rep") == REPUBLICANS
        assert get_party_by_short_name("Ind") == INDEPENDENTS
    
    def test_get_nonexistent_party(self):
        """Test getting a non-existent party (should return INDEPENDENTS)."""
        result = get_party_by_short_name("Fake")
        assert result == INDEPENDENTS
    
    def test_case_sensitivity(self):
        """Test that the function is case sensitive."""
        result = get_party_by_short_name("dem")  # lowercase
        assert result == INDEPENDENTS  # Should return default, not DEMOCRATS


class TestPopulationTagEdgeCases:
    """Test edge cases for PopulationTag."""
    
    def test_empty_affinity(self):
        """Test PopulationTag with empty affinity."""
        tag = PopulationTag("Empty", "E", "Empties", "#000000", {})
        assert tag.party_affinity(DEMOCRATS) == 0.0
        assert tag.party_affinity(REPUBLICANS) == 0.0
    
    def test_single_character_short_name(self):
        """Test PopulationTag with single character short name."""
        tag = PopulationTag("X", "X", "Xes", "#000000", {"X": 1.0})
        assert tag.initial == "X"
    
    def test_unicode_characters(self):
        """Test PopulationTag with unicode characters."""
        tag = PopulationTag("测试", "测", "测试者", "#000000", {"测": 1.0})
        assert tag.name == "测试"
        assert tag.short_name == "测"
        assert tag.plural_name == "测试者"
        assert tag.initial == "测"
    
    def test_very_long_names(self):
        """Test PopulationTag with very long names."""
        long_name = "A" * 1000
        tag = PopulationTag(long_name, "L", "Longs", "#000000", {"L": 1.0})
        assert tag.name == long_name
        assert len(tag.name) == 1000

