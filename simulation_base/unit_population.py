"""
Unit population generation for simulation.
"""
from typing import Optional
from .combined_population import CombinedPopulation
from .population_group import PopulationGroup
from .population_tag import REPUBLICANS, DEMOCRATS, INDEPENDENTS
from .district_voting_record import DistrictVotingRecord


class UnitPopulation:
    """Generates unit populations for simulation."""
    
    @staticmethod
    def default_partisanship() -> float:
        """Default partisanship value."""
        return 1.0
    
    @staticmethod
    def default_skew() -> float:
        """Default skew factor."""
        return 0.0 / 30
    
    @staticmethod
    def default_stddev() -> float:
        """Default standard deviation."""
        return 1.0
    
    @staticmethod
    def create(dvr: DistrictVotingRecord, n_voters: int = 1000) -> CombinedPopulation:
        """Create population with default parameters."""
        return UnitPopulation.create_with_params(
            dvr, UnitPopulation.default_partisanship(), 
            UnitPopulation.default_stddev(), 
            UnitPopulation.default_skew(), 
            n_voters
        )
    
    @staticmethod
    def create_with_params(dvr: DistrictVotingRecord, partisanship: float, 
                          stddev: float, skew_factor: float, n_voters: int, seed: Optional[int] = None) -> CombinedPopulation:
        """Create population with specified parameters."""
        return UnitPopulation.create_from_lean(
            dvr.expected_lean, partisanship, stddev, skew_factor, n_voters, seed
        )
    
    @staticmethod
    def create_from_lean(lean: float, partisanship: float, stddev: float, 
                        skew_factor: float, n_voters: int, seed: Optional[int] = None) -> CombinedPopulation:
        """Create population from lean value."""
        r_pct = 0.5 + (lean / 2 / 100)
        d_pct = 0.5 - (lean / 2 / 100)
        return UnitPopulation.create_from_percentages(
            d_pct, r_pct, partisanship, stddev, skew_factor, n_voters, seed
        )
    
    @staticmethod
    def create_from_percentages(d_pct: float, r_pct: float, partisanship: float,
                               stddev: float, skew_factor: float, n_voters: int, seed: Optional[int] = None) -> CombinedPopulation:
        """Create population from party percentages."""
        i_weight = 0.20
        r_weight = max(0.05, (1 - i_weight) * r_pct)
        d_weight = max(0.05, (1 - i_weight) * d_pct)
        skew = (r_weight - d_weight) / 2.0 * skew_factor * 100
        
        rep = PopulationGroup(
            tag=REPUBLICANS,
            party_bonus=1,
            mean=partisanship + skew,
            stddev=stddev,
            skew=0,
            weight=r_weight * 100
        )
        
        dem = PopulationGroup(
            tag=DEMOCRATS,
            party_bonus=1,
            mean=-partisanship + skew,
            stddev=stddev,
            skew=0,
            weight=d_weight * 100
        )
        
        ind = PopulationGroup(
            tag=INDEPENDENTS,
            party_bonus=0.5,
            mean=0 + skew,
            stddev=stddev,
            skew=0,
            weight=i_weight * 100
        )
        
        return CombinedPopulation([rep, dem, ind], n_voters, seed)
