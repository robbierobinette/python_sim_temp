#!/usr/bin/env python3
"""
Examine toxic tactics across all congressional districts.

This script runs the twin test across all districts to see how often toxic tactics
succeed in helping a candidate win elections.
"""

import argparse
from typing import List
from simulation_base.actual_custom_election import ActualCustomElection
from simulation_base.candidate import Candidate
from simulation_base.candidate_generator import NormalPartisanCandidateGenerator, PartisanCandidateGenerator, CondorcetCandidateGenerator
from simulation_base.instant_runoff_election import InstantRunoffElection
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.unit_population import UnitPopulation
from simulation_base.election_config import ElectionConfig
from simulation_base.election_with_primary import ElectionWithPrimary
from simulation_base.gaussian_generator import GaussianGenerator, set_seed
from simulation_base.election_process import ElectionProcess
from simulation_base.head_to_head_election import HeadToHeadElection
from simulation_base.district_voting_record import DistrictVotingRecord
from simulation_base.ballot import RCVBallot
from simulation_base.population_tag import PopulationTag
from simulation_base.cook_political_data import CookPoliticalData
import csv


def load_districts(csv_file: str) -> List[DistrictVotingRecord]:
    """Load district data from CSV file."""
    cook_data = CookPoliticalData(csv_file)
    return cook_data.load_districts()


def get_opposition_party(party_tag: PopulationTag) -> PopulationTag:
    """Get the opposition party for a given party."""
    if party_tag == DEMOCRATS:
        return REPUBLICANS
    elif party_tag == REPUBLICANS:
        return DEMOCRATS
    else:
        return INDEPENDENTS

def apply_toxic_tactics(candidate: Candidate, toxic_bonus: float, toxic_penalty: float) -> Candidate:
    """Apply toxic tactics to a candidate's affinity map."""
    # Create a copy of the candidate with modified affinity
    new_affinity = candidate._affinity_map.copy()
    
    # Apply toxic bonus to own party
    own_party_short = candidate.tag.short_name
    if own_party_short in new_affinity:
        new_affinity[own_party_short] += toxic_bonus
    
    # Apply toxic penalty to opposition party
    opposition_party = get_opposition_party(candidate.tag)
    if opposition_party.short_name in new_affinity:
        new_affinity[opposition_party.short_name] += toxic_penalty
    
    # Create new candidate with toxic affinity
    toxic_candidate = Candidate(
        name=candidate.name + "-toxic",
        tag=candidate.tag,
        ideology=candidate.ideology,
        quality=candidate.quality,
        incumbent=candidate.incumbent
    )
    toxic_candidate._affinity_map = new_affinity
    
    return toxic_candidate



def run_election(candidates: List[Candidate], 
                        population: UnitPopulation, 
                        election_process: ElectionProcess,
                        config: ElectionConfig, 
                        gaussian_generator: GaussianGenerator,
                        ):
    """Run an election with the given candidates and population."""
    # Create ballots from election definition
    ballots = [RCVBallot(voter, candidates, config, gaussian_generator) for voter in population.voters]

    # Run election with new interface
    return election_process.run(candidates, ballots)


def run_twin_test(district: DistrictVotingRecord,
                 candidate_generator,
                 config: ElectionConfig,
                 gaussian_generator: GaussianGenerator,
                 election_type: str,
                 primary_skew: float,
                 toxic_bonus: float,
                 toxic_penalty: float,
                 nvoters: int,
                 verbose: bool = False) -> dict:
    """
    Run the twin test for a single district.
    
    Returns dict with:
        - district: district name
        - lean: expected lean
        - base_winner: name of base winner
        - base_ideology: ideology of base winner
        - test_result: 'success', 'failure', or 'flip'
        - final_winner: name of final winner
        - final_ideology: ideology of final winner
    """
    # Create population for this district
    population = UnitPopulation.create(district, n_voters=nvoters)
    # Create election process
    election_process = create_election_process(election_type, district, primary_skew)
    
    # Generate candidates
    candidates = candidate_generator.candidates(population)
    
    # Run base election
    base_result = run_election(candidates, population, election_process, config, gaussian_generator)
    base_winner = base_result.winner()
    
    # Create toxic twin of the base winner
    toxic_twin = apply_toxic_tactics(base_winner, toxic_bonus, toxic_penalty)
    
    # Create new candidate list with toxic twin replacing base winner's party opponents
    new_candidates = []
    for candidate in candidates:
        if candidate.tag != base_winner.tag:
            new_candidates.append(candidate)
    
    new_candidates.append(toxic_twin)
    new_candidates.append(base_winner)
    
    # Run election with toxic twin
    new_result = run_election(new_candidates, population, election_process, config, gaussian_generator)
    new_winner = new_result.winner()
    
    # Determine result
    if new_winner.name == base_winner.name:
        result = {
            'district': district.district,
            'lean': district.expected_lean,
            'base_winner': base_winner.name,
            'base_ideology': base_winner.ideology,
            'test_result': 'failure',
            'final_winner': new_winner.name,
            'final_ideology': new_winner.ideology
        }
    elif new_winner.name == toxic_twin.name:
        result = {
            'district': district.district,
            'lean': district.expected_lean,
            'base_winner': base_winner.name,
            'base_ideology': base_winner.ideology,
            'test_result': 'success',
            'final_winner': new_winner.name,
            'final_ideology': new_winner.ideology
        }
    elif new_winner.tag != base_winner.tag and new_winner.name != toxic_twin.name:
        # Opposition party won - test if their toxic twin would also win
        opposition_toxic_twin = apply_toxic_tactics(new_winner, toxic_bonus, toxic_penalty)
        
        # Create third election with 4 candidates
        third_candidates = [base_winner, toxic_twin, new_winner, opposition_toxic_twin]
        third_result = run_election(third_candidates, population, election_process, config, gaussian_generator)
        third_winner = third_result.winner()
        
        if third_winner.name == opposition_toxic_twin.name:
            result = {
                'district': district.district,
                'lean': district.expected_lean,
                'base_winner': base_winner.name,
                'base_ideology': base_winner.ideology,
                'test_result': 'success_flip',
                'final_winner': third_winner.name,
                'final_ideology': third_winner.ideology
            }
        else:
            result = {
                'district': district.district,
                'lean': district.expected_lean,
                'base_winner': base_winner.name,
                'base_ideology': base_winner.ideology,
                'test_result': 'failure_flip',
                'final_winner': third_winner.name,
                'final_ideology': third_winner.ideology
            }
    else:
        raise RuntimeError(f"Unexpected scenario in toxicity analysis: base_winner={base_winner}, new_winner={new_winner}, toxic_twin={toxic_twin}")

    if verbose:
        print(f"{result['test_result']:15s} {result['district']:10s} lean={result['lean']:6.1f} "
              f"{result['base_winner']:10s}({result['base_ideology']:5.2f}) -> "
              f"{result['final_winner']:15s}({result['final_ideology']:5.2f})")
    
    return result


def create_candidate_generator(args, gaussian_generator):
    """Create candidate generator based on arguments."""
    if args.candidate_generator == 'normal-partisan':
        return NormalPartisanCandidateGenerator(
            n_partisan_candidates=args.candidates,
            ideology_variance=args.ideology_variance,
            quality_variance=args.quality_variance,
            primary_skew=args.primary_skew,
            median_variance=0.0,
            gaussian_generator=gaussian_generator
        )
    elif args.candidate_generator == 'partisan':
        return PartisanCandidateGenerator(
            n_partisan_candidates=args.candidates,
            spread=args.spread,
            quality_variance=args.quality_variance,
            gaussian_generator=gaussian_generator
        )
    elif args.candidate_generator == 'condorcet':
        return CondorcetCandidateGenerator(
            n_candidates=args.candidates,
            ideology_variance=args.condorcet_variance,
            quality_variance=args.quality_variance,
            gaussian_generator=gaussian_generator
        )
    else:
        raise ValueError(f"Unknown candidate generator: {args.candidate_generator}")


def create_election_process(election_type: str, district: DistrictVotingRecord, primary_skew: float) -> ElectionProcess:
    """Create election process based on arguments."""
    if election_type == 'primary':
        return ElectionWithPrimary(primary_skew=primary_skew, debug=False)
    elif election_type == 'irv':
        return InstantRunoffElection(debug=False)
    elif election_type == 'condorcet':
        return HeadToHeadElection(debug=False)
    elif election_type == 'top2':
        # use california as the state for the top-2 election
        return ActualCustomElection(state_abbr='CA', primary_skew=primary_skew, debug=True)
    elif election_type == 'custom':
        return ActualCustomElection(state_abbr=district.state, primary_skew=primary_skew, debug=False)
    else:
        raise ValueError(f"Unknown election type: {election_type}")


def main():
    """Run twin test across all congressional districts."""
    parser = argparse.ArgumentParser(description='Examine toxic tactics across congressional districts')
    
    # Core arguments
    parser.add_argument('--data-file', default='CookPoliticalData.csv',
                       help='Path to CSV file with district data')
    parser.add_argument('--seed', type=int, default=0,
                       help='Random seed for reproducible results')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose output')
    
    # Election configuration
    parser.add_argument('--election-type', choices=['primary', 'irv', 'condorcet', 'custom', 'top2'],
                       default='primary',
                       help='Type of election to run')
    parser.add_argument('--primary-skew', type=float, default=0.0,
                       help='Primary election skew factor')
    parser.add_argument('--uncertainty', type=float, default=0.5,
                       help='Voter uncertainty factor')
    parser.add_argument('--nvoters', type=int, default=1000,
                       help='Number of voters per district')
    
    # Candidate generation
    parser.add_argument('--candidate-generator', 
                       choices=['partisan', 'condorcet', 'normal-partisan'],
                       default='normal-partisan',
                       help='Type of candidate generator to use')
    parser.add_argument('--candidates', type=int, default=3,
                       help='Number of candidates per party')
    parser.add_argument('--ideology-variance', type=float, default=0.2,
                       help='Ideology variance for candidates')
    parser.add_argument('--quality-variance', type=float, default=0.01,
                       help='Quality variance for candidate generation')
    parser.add_argument('--spread', type=float, default=0.4,
                       help='Spread for partisan candidate generator')
    parser.add_argument('--condorcet-variance', type=float, default=0.1,
                       help='Ideology variance for Condorcet candidates')
    
    # Toxicity parameters
    parser.add_argument('--toxic-bonus', type=float, default=0.25,
                       help='Ideology bonus for toxic tactics (moves toward extreme)')
    parser.add_argument('--toxic-penalty', type=float, default=-1.0,
                       help='Quality penalty for toxic tactics')
    
    # Output options
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of districts to test')
    parser.add_argument('--districts', nargs='+',
                       help='Test specific districts (e.g., CA-14 TX-01)')
    
    args = parser.parse_args()
    
    # Setup
    set_seed(args.seed)
    gaussian_generator = GaussianGenerator(args.seed)
    
    # Create election configuration
    config = ElectionConfig(uncertainty=args.uncertainty)
    
    # Create candidate generator
    candidate_generator = create_candidate_generator(args, gaussian_generator)
    
    
    # Load districts
    districts = load_districts(args.data_file)
    
    # Filter districts if specific ones requested
    if args.districts:
        districts = [d for d in districts if d.district in args.districts]
        if not districts:
            print("Error: No matching districts found")
            return
    
    # Limit districts if requested
    if args.limit:
        districts = districts[:args.limit]
    
    print(f"Testing {len(districts)} districts...")
    print(f"Election type: {args.election_type}")
    print(f"Primary skew: {args.primary_skew}")
    print(f"Candidates: {args.candidates} per party")
    print(f"Toxic bonus: {args.toxic_bonus}, penalty: {args.toxic_penalty}")
    print()
    
    # Run tests
    results = []
    toxic_success = 0
    toxic_failure = 0
    toxic_flip = 0
    
    for district in districts:
        result = run_twin_test(
            district=district,
            candidate_generator=candidate_generator,
            config=config,
            gaussian_generator=gaussian_generator,
            election_type=args.election_type,
            primary_skew=args.primary_skew,
            toxic_bonus=args.toxic_bonus,
            toxic_penalty=args.toxic_penalty,
            nvoters=args.nvoters,
            verbose=args.verbose
        )
        results.append(result)
        
        # Count results
        if result['test_result'] in ['success', 'success_flip']:
            toxic_success += 1
            if result['test_result'] == 'success_flip':
                toxic_flip += 1
        elif result['test_result'] in ['failure', 'failure_flip']:
            toxic_failure += 1
            if result['test_result'] == 'failure_flip':
                toxic_flip += 1
    
    # Print summary
    print()
    print("=" * 60)
    print("SUMMARY:")
    print(f"Total districts tested: {len(results)}")
    print(f"Toxic tactics succeeded: {toxic_success} ({toxic_success/len(results)*100:.1f}%)")
    print(f"Toxic tactics failed: {toxic_failure} ({toxic_failure/len(results)*100:.1f}%)")
    print(f"Flips to opposition: {toxic_flip} ({toxic_flip/len(results)*100:.1f}%)")
    
    # Break down by lean
    dem_districts = [r for r in results if r['lean'] < -5]
    rep_districts = [r for r in results if r['lean'] > 5]
    swing_districts = [r for r in results if -5 <= r['lean'] <= 5]
    
    if dem_districts:
        dem_success = sum(1 for r in dem_districts if r['test_result'] in ['success', 'success_flip'])
        print(f"\nDemocratic districts (lean < -5): {dem_success}/{len(dem_districts)} ({dem_success/len(dem_districts)*100:.1f}%)")
    
    if rep_districts:
        rep_success = sum(1 for r in rep_districts if r['test_result'] in ['success', 'success_flip'])
        print(f"Republican districts (lean > 5): {rep_success}/{len(rep_districts)} ({rep_success/len(rep_districts)*100:.1f}%)")
    
    if swing_districts:
        swing_success = sum(1 for r in swing_districts if r['test_result'] in ['success', 'success_flip'])
        print(f"Swing districts (-5 <= lean <= 5): {swing_success}/{len(swing_districts)} ({swing_success/len(swing_districts)*100:.1f}%)")


if __name__ == "__main__":
    main()
