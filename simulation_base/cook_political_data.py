"""
CookPoliticalData - Centralized loader for Cook Political Report data.

This module provides a single, reusable class for loading and managing
congressional district data from Cook Political Report CSV files.
"""

import csv
from typing import List, Dict, Optional
from .district_voting_record import DistrictVotingRecord


class CookPoliticalData:
    """Loads and manages Cook Political Report congressional district data."""
    
    # State name to abbreviation mapping
    STATE_ABBREVIATIONS = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
        'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
        'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
        'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
        'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
        'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
        'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
        'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
        'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
        'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
        'District of Columbia': 'DC'
    }
    
    def __init__(self, csv_file: str):
        """
        Initialize CookPoliticalData with CSV file path.
        
        Args:
            csv_file: Path to Cook Political Report CSV file
        """
        self.csv_file = csv_file
        self._districts_cache: Optional[List[DistrictVotingRecord]] = None
    
    def _parse_pvi(self, pvi_str: str) -> float:
        """
        Parse Cook PVI (Partisan Voting Index) string.
        
        Args:
            pvi_str: PVI string like "R+27" or "D+5" or "EVEN"
            
        Returns:
            Float value where positive = Republican lean, negative = Democratic lean
        """
        pvi_str = pvi_str.strip()
        if pvi_str.startswith('R+'):
            return float(pvi_str[2:])
        elif pvi_str.startswith('D+'):
            return -float(pvi_str[2:])
        else:
            return 0.0
    
    def _format_district_name(self, state_name: str, district_number: str) -> str:
        """
        Format district name with state abbreviation and zero-padded number.
        
        Args:
            state_name: Full state name (e.g., "California")
            district_number: District number string (e.g., "15" or "AL")
            
        Returns:
            Formatted district name (e.g., "CA-15" or "AK-01")
        """
        state_abbrev = self.STATE_ABBREVIATIONS.get(state_name, state_name[:2].upper())
        
        # Handle at-large districts (AL) by converting to 01
        if district_number.upper() == 'AL':
            district_number = '01'
        else:
            # Zero-pad district numbers
            try:
                district_num = int(district_number)
                district_number = f"{district_num:02d}"
            except ValueError:
                # If not a number, keep as is
                pass
        
        return f"{state_abbrev}-{district_number}"
    
    def load_districts(self) -> List[DistrictVotingRecord]:
        """
        Load all districts from CSV file.
        
        Returns:
            List of DistrictVotingRecord objects
        """
        if self._districts_cache is not None:
            return self._districts_cache
        
        districts = []
        
        with open(self.csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip empty rows or rows with empty State
                if not row.get('State') or not row['State'].strip():
                    continue
                
                # Parse Cook PVI
                expected_lean = self._parse_pvi(row['2025 Cook PVI'])
                
                # Format district name
                district_name = self._format_district_name(row['State'], row['Number'])
                
                # Get incumbent (handle different CSV column names)
                incumbent = row.get('Member', row.get('Incumbent', ''))
                
                # Get party percentages (use actual values if available, otherwise approximate from lean)
                if row.get('D%'):
                    d_pct1 = float(row.get('D%', 0))
                    r_pct1 = float(row.get('R%', 0))
                else:
                    # Approximate from expected lean
                    d_pct1 = 50.0 - expected_lean / 2
                    r_pct1 = 50.0 + expected_lean / 2
                
                # Create district record
                district = DistrictVotingRecord(
                    district=district_name,
                    incumbent=incumbent,
                    expected_lean=expected_lean,
                    d_pct1=d_pct1,
                    r_pct1=r_pct1,
                    d_pct2=d_pct1,
                    r_pct2=r_pct1
                )
                
                districts.append(district)
        
        self._districts_cache = districts
        return districts
    
    def get_districts_dict(self) -> Dict[str, DistrictVotingRecord]:
        """
        Load districts and return as a dictionary keyed by district name.
        
        Returns:
            Dictionary mapping district names to DistrictVotingRecord objects
        """
        districts = self.load_districts()
        return {district.district: district for district in districts}
    
    def get_district(self, district_name: str) -> Optional[DistrictVotingRecord]:
        """
        Get a specific district by name.
        
        Args:
            district_name: District identifier (e.g., "CA-15")
            
        Returns:
            DistrictVotingRecord if found, None otherwise
        """
        districts_dict = self.get_districts_dict()
        return districts_dict.get(district_name)

