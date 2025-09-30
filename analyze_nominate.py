#!/usr/bin/env python3
"""
Analyze NOMINATE-DIM1 scores by party for specified Congresses.

This script reads HSall_members.csv and calculates the mean NOMINATE-DIM1 score
for each party in the specified Congress(es).

Usage:
    python analyze_nominate.py                    # Analyze Congress 119 (default)
    python analyze_nominate.py 119                # Analyze Congress 119
    python analyze_nominate.py 117 118 119        # Analyze multiple Congresses
"""

import csv
import sys
from typing import Dict, List
from collections import defaultdict


def parse_hsall_members(filename: str, congress: str = '119') -> Dict[str, List[float]]:
    """Parse HSall_members.csv and return NOMINATE-DIM1 scores by party."""
    nominate_scores_by_party = defaultdict(list)
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Only process House members from specified Congress
                if (row['congress'] == congress and 
                    row['chamber'] == 'House' and 
                    row['nominate_dim1'] != ''):
                    
                    # Get party code and NOMINATE score
                    party_code = row['party_code']
                    nominate_dim1 = float(row['nominate_dim1'])
                    
                    # Map party code to party name
                    party_name = map_party_code(party_code)
                    nominate_scores_by_party[party_name].append(nominate_dim1)
    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"Error reading '{filename}': {e}", file=sys.stderr)
        return {}
    
    return dict(nominate_scores_by_party)


def map_party_code(party_code: str) -> str:
    """Map party code to party name."""
    party_map = {
        '100': 'Democratic',  # Democratic
        '200': 'Republican',  # Republican
        '328': 'Independent',  # Independent
        '329': 'Independent',  # Independent
    }
    return party_map.get(party_code, 'Other')


def calculate_mean_nominate(scores_by_party: Dict[str, List[float]]) -> Dict[str, float]:
    """Calculate mean NOMINATE-DIM1 score for each party."""
    mean_scores = {}
    
    for party, scores in scores_by_party.items():
        if scores:
            mean_scores[party] = sum(scores) / len(scores)
        else:
            mean_scores[party] = 0.0
    
    return mean_scores


def print_analysis(congress: str, mean_scores: Dict[str, float], scores_by_party: Dict[str, List[float]]):
    """Print analysis results."""
    print(f"NOMINATE-DIM1 Analysis for Congress {congress}")
    print("=" * 50)
    
    if not mean_scores:
        print("No valid data found")
        return
    
    # Sort parties for consistent output
    parties = sorted(mean_scores.keys())
    
    for party in parties:
        mean = mean_scores[party]
        count = len(scores_by_party[party])
        print(f"{party:>12}: {mean:>7.3f} (n={count})")
    
    # Print total if multiple parties
    if len(parties) > 1:
        all_scores = []
        for scores in scores_by_party.values():
            all_scores.extend(scores)
        
        if all_scores:
            overall_mean = sum(all_scores) / len(all_scores)
            print(f"{'Overall':>12}: {overall_mean:>7.3f} (n={len(all_scores)})")


def main():
    """Main function to analyze NOMINATE scores."""
    # Allow multiple Congress numbers as command line arguments
    if len(sys.argv) > 1:
        congresses = sys.argv[1:]
    else:
        congresses = ['119']  # Default to 119th Congress
    
    print("NOMINATE-DIM1 Analysis")
    print("=" * 60)
    
    for congress in congresses:
        print(f"\nAnalyzing Congress {congress}...")
        
        # Parse the CSV file
        scores_by_party = parse_hsall_members('HSall_members.csv', congress)
        
        if not scores_by_party:
            print(f"No data found for Congress {congress}", file=sys.stderr)
            continue
        
        # Calculate means
        mean_scores = calculate_mean_nominate(scores_by_party)
        
        # Print results
        print_analysis(congress, mean_scores, scores_by_party)
        
        # Print some additional statistics
        print(f"\nAdditional Statistics:")
        total_members = sum(len(scores) for scores in scores_by_party.values())
        print(f"Total House members: {total_members}")
        
        # Show party distribution
        for party, scores in scores_by_party.items():
            percentage = (len(scores) / total_members) * 100
            print(f"{party}: {len(scores)} members ({percentage:.1f}%)")
    
    print(f"\nAnalyzed {len(congresses)} Congress(es)")


if __name__ == "__main__":
    main()
