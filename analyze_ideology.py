#!/usr/bin/env python3
"""
Analyze ideology from results JSON files.

This script reads one or more results JSON files and prints the mean ideology
for winners from each party (Democratic, Republican, Other).

Usage:
    python analyze_ideology.py results-primary.json results-irv.json results-actual.json
    python analyze_ideology.py *.json
"""

import json
import sys
from typing import List, Dict, Tuple
from collections import defaultdict


def load_results(filename: str) -> Dict:
    """Load results from a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{filename}': {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error reading '{filename}': {e}", file=sys.stderr)
        return None


def analyze_ideology(results: Dict) -> Tuple[Dict[str, List[float]], int, int]:
    """Analyze ideology by party from results data and count median candidates."""
    ideologies_by_party = defaultdict(list)
    total_districts = 0
    median_candidate_wins = 0
    
    if 'district_results' not in results:
        print("Warning: No 'district_results' found in JSON file", file=sys.stderr)
        return dict(ideologies_by_party), 0, 0
    
    for district_result in results['district_results']:
        if 'winner_party' in district_result and 'winner_ideology' in district_result:
            party = district_result['winner_party']
            ideology = district_result['winner_ideology']
            ideologies_by_party[party].append(ideology)
            
            # Check if winner is a median candidate (name ends in "-V")
            winner_name = district_result.get('winner_name', '')
            if winner_name.endswith('-V'):
                median_candidate_wins += 1
            
            total_districts += 1
    
    return dict(ideologies_by_party), total_districts, median_candidate_wins


def calculate_mean_ideology(ideologies_by_party: Dict[str, List[float]]) -> Dict[str, float]:
    """Calculate mean ideology for each party."""
    mean_ideology = {}
    
    for party, ideologies in ideologies_by_party.items():
        if ideologies:
            mean_ideology[party] = sum(ideologies) / len(ideologies)
        else:
            mean_ideology[party] = 0.0
    
    return mean_ideology


def print_analysis(filename: str, mean_ideology: Dict[str, float], ideologies_by_party: Dict[str, List[float]], 
                  total_districts: int, median_candidate_wins: int):
    """Print analysis results for a single file."""
    print(f"\n{filename}:")
    print("-" * (len(filename) + 1))
    
    if not mean_ideology:
        print("  No valid data found")
        return
    
    # Sort parties for consistent output
    parties = sorted(mean_ideology.keys())
    
    for party in parties:
        mean = mean_ideology[party]
        count = len(ideologies_by_party[party])
        print(f"  {party:>3}: {mean:>7.3f} (n={count})")
    
    # Print total if multiple parties
    if len(parties) > 1:
        all_ideologies = []
        for ideologies in ideologies_by_party.values():
            all_ideologies.extend(ideologies)
        
        if all_ideologies:
            overall_mean = sum(all_ideologies) / len(all_ideologies)
            print(f"  ALL: {overall_mean:>7.3f} (n={len(all_ideologies)})")
    
    # Print median candidate percentage
    if total_districts > 0:
        median_percentage = (median_candidate_wins / total_districts) * 100
        print(f"  Median candidates: {median_candidate_wins}/{total_districts} ({median_percentage:.1f}%)")
    else:
        print("  Median candidates: No data")


def main():
    """Main function to analyze ideology from JSON files."""
    if len(sys.argv) < 2:
        print("Usage: python analyze_ideology.py <json_file1> [json_file2] ...", file=sys.stderr)
        print("Example: python analyze_ideology.py results-primary.json results-irv.json", file=sys.stderr)
        sys.exit(1)
    
    filenames = sys.argv[1:]
    valid_files = 0
    
    print("Ideology Analysis")
    print("=" * 50)
    
    for filename in filenames:
        # Load results
        results = load_results(filename)
        if results is None:
            continue
        
        # Analyze ideology
        ideologies_by_party, total_districts, median_candidate_wins = analyze_ideology(results)
        mean_ideology = calculate_mean_ideology(ideologies_by_party)
        
        # Print results
        print_analysis(filename, mean_ideology, ideologies_by_party, total_districts, median_candidate_wins)
        valid_files += 1
    
    if valid_files == 0:
        print("No valid files processed", file=sys.stderr)
        sys.exit(1)
    
    print(f"\nProcessed {valid_files} file(s)")


if __name__ == "__main__":
    main()
