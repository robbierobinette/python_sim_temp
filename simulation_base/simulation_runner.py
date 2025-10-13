"""
Shared simulation runner for common argument parsing and simulation setup.
"""
import argparse
import os
import sys
from .simulation_config import CongressionalSimulationConfigFactory
from .gaussian_generator import GaussianGenerator, set_seed


def parse_simulation_args(description: str = "Simulate congressional elections") -> argparse.ArgumentParser:
    """Create argument parser with common simulation arguments."""
    parser = argparse.ArgumentParser(description=description)
    
    # Core simulation arguments
    parser.add_argument(
        "--data-file", 
        default="CookPoliticalData.csv",
        help="Path to CSV file with district data (default: CookPoliticalData.csv)"
    )
    parser.add_argument(
        "--output", 
        default="simulation_results.json",
        help="Output file for results (default: simulation_results.json)"
    )
    parser.add_argument(
        "--seed", 
        default=0,
        type=int,
        help="Random seed for reproducible results (default: 0)"
    )
    parser.add_argument(
        "--candidates", 
        type=int,
        default=3,
        help="Number of candidates: per party for partisan/normal-partisan, total for random/condorcet (default: 3)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--election-type", 
        choices=["primary", "irv", "condorcet", "custom"],
        default="primary",
        help="Type of election to run (default: primary)"
    )
    parser.add_argument(
        "--plot", 
        action="store_true",
        help="Generate and display plots"
    )
    parser.add_argument(
        "--plot-dir", 
        default="plots",
        help="Directory to save plots (default: plots)"
    )
    parser.add_argument(
        "--histogram-only", 
        action="store_true",
        help="Generate only the winner ideology histogram"
    )
    parser.add_argument(
        "--nvoters", 
        type=int,
        default=1000,
        help="Number of voters per district (default: 1000)"
    )
    parser.add_argument(
        "--partisan-shift", 
        type=float,
        default=0.01,
        help="Partisan shift of the population (default: 0.01), meaning a shift of .01 sigma every point of partisan lean"
    )
    parser.add_argument(
        "--uncertainty", 
        type=float,
        default=0.5,
        help="Voter uncertainty factor (default: 0.5)"
    )
    parser.add_argument(
        "--primary-skew", 
        type=float,
        default=0.0,
        help="Primary election skew factor (default: 0.0)"
    )
    parser.add_argument(
        "--candidate-generator", 
        choices=["partisan", "condorcet", "random", "normal-partisan"],
        default="partisan",
        help="Type of candidate generator to use (default: partisan)"
    )
    parser.add_argument(
        "--condorcet-variance", 
        type=float,
        default=0.1,
        help="Ideology variance for Condorcet candidates (default: 0.5)"
    )
    parser.add_argument(
        "--ideology-variance", 
        type=float,
        default=0.20,
        help="Ideology variance for candidates (default: 0.20)"
    )
    parser.add_argument(
        "--spread", 
        type=float,
        default=0.4,
        help="Spread for partisan candidate generator (default: 0.4)"
    )
    parser.add_argument(
        "--quality-variance", 
        type=float,
        default=0.0,
        help="Quality variance for candidate generation (default: 0.0)"
    )
    
    return parser


def setup_simulation(args: argparse.Namespace) -> tuple:
    """Setup simulation configuration and check data file."""
    # Check if data file exists
    if not os.path.exists(args.data_file):
        print(f"Error: Data file '{args.data_file}' not found")
        sys.exit(1)
    
    # Set random seed if provided
    if args.seed is not None:
        set_seed(args.seed)
        if args.verbose:
            print(f"Using random seed: {args.seed}")
    
    # Create simulation configuration
    gaussian_generator = GaussianGenerator(args.seed)
    config_params = {
        'candidates': args.candidates,
        'gaussian_generator': gaussian_generator,
        'nvoters': args.nvoters,
        'uncertainty': args.uncertainty,
        'primary_skew': args.primary_skew,
        'candidate_generator_type': args.candidate_generator,
        'condorcet_variance': args.condorcet_variance,
        'election_type': args.election_type,
        'ideology_variance': args.ideology_variance,
        'spread': args.spread,
        'quality_variance': args.quality_variance,
        'partisan_shift': args.partisan_shift
    }
    
    config = CongressionalSimulationConfigFactory.create_config(config_params)
    
    if args.verbose:
        print(f"Configuration: {config.describe()}")
    
    return config, gaussian_generator


def run_simulation(config, gaussian_generator, data_file: str, election_type: str, verbose: bool = False):
    """Run the simulation with given configuration."""
    from congressional_simulation import CongressionalSimulation
    
    simulation = CongressionalSimulation(
        config=config,
        gaussian_generator=gaussian_generator,
        election_type=election_type
    )
    
    if verbose:
        print(f"Loading district data from {data_file}...")
    
    result = simulation.run_simulation(data_file)
    
    if verbose:
        print(f"Simulation completed: {result.total_districts} districts")
    
    return simulation, result
