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
from simulation_base.candidate_generator import CandidateGenerator, NormalPartisanCandidateGenerator, CondorcetCandidateGenerator
from simulation_base.combined_population import CombinedPopulation
from simulation_base.instant_runoff_election import InstantRunoffElection
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from simulation_base.unit_population import UnitPopulation
from simulation_base.election_config import ElectionConfig
from simulation_base.election_with_primary import ElectionWithPrimary
from simulation_base.gaussian_generator import GaussianGenerator
from simulation_base.election_process import ElectionProcess
from simulation_base.condorcet_election import CondorcetElection
from simulation_base.district_voting_record import DistrictVotingRecord
from simulation_base.ballot import RCVBallot
from simulation_base.population_tag import PopulationTag
from simulation_base.cook_political_data import CookPoliticalData


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
                    candidate_generator: CandidateGenerator,
                    config: ElectionConfig,
                    gaussian_generator: GaussianGenerator,
                    election_type: str,
                    primary_skew: float,
                    toxic_bonus: float,
                    toxic_penalty: float,
                    nvoters: int,
                    args: argparse.Namespace) -> dict:
    """
    run the election with no toxic candidates or tactics, then rerun the election with
    a toxic twin of the winner.  In the rerun, reduce the field for the original winner's party
    to be just the toxic twin and the original winner.  
    """
    population = UnitPopulation.create(district, n_voters=nvoters, gaussian_generator=gaussian_generator)
    election_process = create_election_process(election_type, district, primary_skew, args)
    candidates = candidate_generator.candidates(population, election_type)

    base_result = run_election(candidates, population, election_process, config, gaussian_generator)
    base_winner = base_result.winner()
    toxic_candidate = apply_toxic_tactics(base_winner, toxic_bonus, toxic_penalty)
    new_candidates = [toxic_candidate, base_winner]
    for candidate in candidates:
        if candidate.tag != base_winner.tag:
            new_candidates.append(candidate)
    new_result = run_election(new_candidates, population, election_process, config, gaussian_generator)
    test_result = 'success' if new_result.winner().name == toxic_candidate.name else 'failure'
    return {
        'district': district.district,
        'lean': district.expected_lean,
        'test_result': test_result,
    }

def run_non_toxic_test(district: DistrictVotingRecord,
                 candidate_generator,
                 config: ElectionConfig,
                 gaussian_generator: GaussianGenerator,
                 election_type: str,
                 primary_skew: float,
                 toxic_bonus: float,
                 toxic_penalty: float,
                 nvoters: int,
                 args: argparse.Namespace) -> dict:

    population = UnitPopulation.create(district, n_voters=nvoters, gaussian_generator=gaussian_generator)
    election_process = create_election_process(election_type, district, primary_skew, args)
    base_candidates = candidate_generator.candidates(population, election_type)
    toxic_candidates = [apply_toxic_tactics(c, toxic_bonus, toxic_penalty) for c in base_candidates]
    results = []
    for i, c in enumerate(toxic_candidates):
        new_candidates = toxic_candidates.copy()
        new_candidates[i] = base_candidates[i]
        result = run_election(new_candidates, population, election_process, config, gaussian_generator)
        results.append(result)
        winner = result.winner()
        if "toxic" not in winner.name:
            return {
                'district': district.district,
                'lean': district.expected_lean,
                'test_result': 'failure',
            }

    if args.verbose:
        print(f"Toxic Failure:  District: {district.district} Lean: {district.expected_lean}")

    return {
        'district': district.district,
        'lean': district.expected_lean,
        'test_result': 'success',
    }

def run_all_test(district: DistrictVotingRecord,
                 candidate_generator,
                 config: ElectionConfig,
                 gaussian_generator: GaussianGenerator,
                 election_type: str,
                 primary_skew: float,
                 toxic_bonus: float,
                 toxic_penalty: float,
                 nvoters: int,
                 args: argparse.Namespace) -> dict:

    population = UnitPopulation.create(district, n_voters=nvoters, gaussian_generator=gaussian_generator)
    election_process = create_election_process(election_type, district, primary_skew, args)
    candidates = candidate_generator.candidates(population, election_type)
    base_result = run_election(candidates, population, election_process, config, gaussian_generator)
    base_winner = base_result.winner()
    results = []
    for i, c in enumerate(candidates):
        new_candidates = candidates.copy()
        toxic_candidate = apply_toxic_tactics(c, toxic_bonus, toxic_penalty)
        if c.name != base_winner.name:
            new_candidates[i] = toxic_candidate
        else:
            new_candidates.append(toxic_candidate)
        result = run_election(new_candidates, population, election_process, config, gaussian_generator)
        results.append(result)
        winner = result.winner()
        if winner.name == toxic_candidate.name:
            if args.verbose and args.election_type == 'condorcet':
                print(f"Toxic Success:  District: {district.district} Lean: {district.expected_lean}")
                print(f"Base winner: {base_winner.name} ", end="")
                print(f"Toxic winner: {toxic_candidate.name}")
                result.print_details()
            return {
                'district': district.district,
                'lean': district.expected_lean,
                'test_result': 'success',
            }

    if args.verbose:
        print(f"Toxic Failure:  District: {district.district} Lean: {district.expected_lean}")
        for candidate, result in zip(candidates, results):
            tc = apply_toxic_tactics(candidate, toxic_bonus, toxic_penalty)
            print(f"testing candidate: {tc.name:12s} {tc.ideology:5.2f} {tc.quality:5.2f} {tc.affinity_string()}")
            result.print_details()

    return {
        'district': district.district,
        'lean': district.expected_lean,
        'test_result': 'failure',
    }



class BalancedCandidateFilter(CandidateGenerator):
    def __init__(self, generator: CandidateGenerator):
        self.generator = generator
    def candidates(self, population: CombinedPopulation) -> List[Candidate]:
        base_candidates = self.generator.candidates(population)
        filtered_candidates = [ c for c in base_candidates if c.name[1:] != "-V"]
        return filtered_candidates


def create_candidate_generator(args, gaussian_generator):
    """Create candidate generator based on arguments."""
    if args.candidate_generator == 'normal-partisan':
        return NormalPartisanCandidateGenerator(
            n_partisan_candidates=args.candidates,
            ideology_variance=args.ideology_variance,
            quality_variance=args.quality_variance,
            primary_skew=args.primary_skew,
            median_variance=0.0,
            gaussian_generator=gaussian_generator,
            n_condorcet=args.n_condorcet
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


def create_election_process(election_type: str, district: DistrictVotingRecord, primary_skew: float, args: argparse.Namespace) -> ElectionProcess:
    """Create election process based on arguments."""
    if election_type == 'primary':
        return ElectionWithPrimary(primary_skew=primary_skew, debug=args.verbose)
    elif election_type == 'irv':
        return InstantRunoffElection(debug=args.verbose)
    elif election_type == 'condorcet':
        return CondorcetElection(debug=args.verbose)
    elif election_type == 'top-2':
        # use california as the state for the top-2 election
        return ActualCustomElection(state_abbr='CA', primary_skew=primary_skew, debug=args.verbose)
    elif election_type == 'custom':
        return ActualCustomElection(state_abbr=district.state, primary_skew=primary_skew, debug=args.verbose)
    else:
        raise ValueError(f"Unknown election type: {election_type}")


def print_stats(label: str, stats: {}):
    successes = stats['successes']
    failures = stats['failures']
    total_districts = successes + failures
    print(f"{label}: toxic success: {successes:4d}/{total_districts:4d} ({successes/total_districts*100:4.1f}%)")

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
    parser.add_argument('--election-type', choices=['primary', 'irv', 'condorcet', 'custom', 'top-2'],
                       default='primary',
                       help='Type of election to run')
    parser.add_argument('--test-type', choices=['twin', 'non-toxic', 'toxic'],
                        default='toxic', help='type of test to run, default is toxic')
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
    parser.add_argument('--n-condorcet', type=int, default=1,
                       help='Number of Condorcet candidates')
    parser.add_argument('--condorcet-variance', type=float, default=0.05,
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
    gaussian_generator = GaussianGenerator(args.seed)
    
    # Create election configuration
    config = ElectionConfig(uncertainty=args.uncertainty)
    
    # Create candidate generator
    candidate_generator = create_candidate_generator(args, gaussian_generator)
    
    
    # Load districts
    districts: List[DistrictVotingRecord] = load_districts(args.data_file)
    
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
    print(f"Candidates: {args.candidates} per party, {args.n_condorcet} Condorcet candidate {args.condorcet_variance} variance")
    print(f"Toxic bonus: {args.toxic_bonus}, penalty: {args.toxic_penalty}")
    print()
    
    # Run tests
    results = []

    # Top-2 states are the states that have a top-2 election
    # create a set of the abbreviations of the top-2 states
    top2_states = set(['CA', 'WA', 'LA'])
    top2_stats = {'successes': 0, 'failures': 0}
    other_stats = {'successes': 0, 'failures': 0}
    all_stats = {'successes': 0, 'failures': 0}

    
    for district in districts:
        if args.test_type == 'twin':
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
                args=args
            )
            results.append(result)
        elif args.test_type == 'non-toxic':
            result = run_non_toxic_test(
                district=district,
                candidate_generator=candidate_generator,
                config=config,
                gaussian_generator=gaussian_generator,
                election_type=args.election_type,
                primary_skew=args.primary_skew,
                toxic_bonus=args.toxic_bonus,
                toxic_penalty=args.toxic_penalty,
                nvoters=args.nvoters,
                args=args
            )
        elif args.test_type == 'toxic':
            result = run_all_test(
                district=district,
                candidate_generator=candidate_generator,
                config=config,
                gaussian_generator=gaussian_generator,
                election_type=args.election_type,
                primary_skew=args.primary_skew,
                toxic_bonus=args.toxic_bonus,
                toxic_penalty=args.toxic_penalty,
                nvoters=args.nvoters,
                args=args
            )
        else:
            raise ValueError(f"Unknown test type: {args.test_type}")

        results.append(result)
        
        # Count results
        if result['test_result'] == "success":
            all_stats['successes'] += 1
            if district.state in top2_states:
                top2_stats['successes'] += 1
            else:
                other_stats['successes'] += 1
        else:
            all_stats['failures'] += 1
            if district.state in top2_states:
                top2_stats['failures'] += 1
            else:
                other_stats['failures'] += 1

    
    # Print summary
    print_stats(f"All states {args.election_type:10s} {args.test_type:10s}", all_stats)


if __name__ == "__main__":
    main()
    # import cProfile
    # cProfile.run('main()', sort='cumulative', filename='twin_test.prof')
    # import pstats
    # pstats.Stats('twin_test.prof').sort_stats('cumulative').print_stats(50)
