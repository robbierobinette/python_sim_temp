#!/usr/bin/env python3
"""
Simple script to examine a primary election with hard-coded candidates.
"""

from typing import List
from simulation_base.candidate import Candidate
from simulation_base.candidate_generator import NormalPartisanCandidateGenerator
from simulation_base.population_tag import DEMOCRATS, REPUBLICANS 
from simulation_base.unit_population import UnitPopulation
from simulation_base.election_config import ElectionConfig
from simulation_base.election_definition import ElectionDefinition
from simulation_base.election_with_primary import ElectionWithPrimary
from simulation_base.gaussian_generator import GaussianGenerator
from simulation_base.toxicity_analyzer import ToxicityAnalyzer
from simulation_base.election_with_primary import ElectionWithPrimaryResult

def run_primary_election(candidates: List[Candidate], 
                        population: UnitPopulation, 
                        config: ElectionConfig, 
                        gaussian_generator: GaussianGenerator) -> ElectionWithPrimaryResult:
   
    # Create election definition
    election_def = ElectionDefinition(
        candidates=candidates,
        population=population,
        config=config,
        gaussian_generator=gaussian_generator
    )
    
    election_process = ElectionWithPrimary(primary_skew=0.25, debug=False)
    return election_process.run(election_def)
    
def fixed_candidates() -> List[Candidate]:
    return[
        Candidate(name="D-1", tag=DEMOCRATS, ideology=-1.1, quality=0.0, incumbent=False),
        Candidate(name="D-2", tag=DEMOCRATS, ideology=-1.0, quality=0.0, incumbent=False),
        Candidate(name="D-3", tag=DEMOCRATS, ideology=-0.9, quality=0.0, incumbent=False),
        Candidate(name="R-1", tag=REPUBLICANS, ideology=0.9, quality=0.0, incumbent=False),
        Candidate(name="R-2", tag=REPUBLICANS, ideology=1.0, quality=0.0, incumbent=False),
        Candidate(name="R-3", tag=REPUBLICANS, ideology=1.1, quality=0.0, incumbent=False),
    ]
 
def main():
    """Run a simple primary election examination."""
    
    # Hard-coded configuration matching command line defaults
    config = ElectionConfig(uncertainty=0.1)
    
    # Create gaussian generator
    gaussian_generator = GaussianGenerator()
    candidate_generator = NormalPartisanCandidateGenerator(n_partisan_candidates=3, 
                    ideology_variance=0.1, 
                    quality_variance=0.05, 
                    primary_skew=0.0, 
                    median_variance=0.0, 
                    gaussian_generator=gaussian_generator)
    toxic_analyzer = ToxicityAnalyzer(.25, -1)

    toxic_failed = 0
    toxic_success = 0
    toxic_flip = 0

    for lean in range(-30, 30):
        
        # Create population without partisan lean
        # Parameters: lean=0, partisanship=1, stddev=1, skew_factor=0, n_voters=1000
        population = UnitPopulation.create_from_lean(
            lean=lean,           
            partisanship=1.0,   # Standard partisanship
            stddev=1.0,         # Standard deviation
            skew_factor=0.0,    # No skew
            n_voters=10000       # 1000 voters
        )
        
        candidates = candidate_generator.candidates(population)
        
        base_result = run_primary_election(candidates, population, config, gaussian_generator)
        base_winner = base_result.winner()

        toxic_twin: Candidate = toxic_analyzer.apply_toxic_tactics(base_result.winner())
        # change the name of the toxic twin to ahve a toxic prefix i.e. toxic-base_result.winner().name
        toxic_twin.name = f"toxic-{base_winner.name}"



        new_candidates: List[Candidate] = []
        for candidate in candidates:
            if candidate.tag != base_winner.tag:
                new_candidates.append(candidate)

        new_candidates.append(toxic_twin)
        new_candidates.append(base_winner)

        new_result = run_primary_election(new_candidates, population, config, gaussian_generator)
        new_winner = new_result.winner()
        
        
        # Third election: if the new winner is from opposition party and not the toxic twin,
        # test if that opposition candidate would win against their own toxic competition
        if new_winner.name == base_winner.name:
            print(f"toxic failure: lean={lean:3d} {base_winner.name:6s}({base_winner.ideology:5.2f}) toxic_twin winner {new_winner.name:6s}({new_winner.ideology:5.2f})")
            toxic_failed += 1
            continue
        if new_winner.name == toxic_twin.name:
            print(f"toxic success: lean={lean:3d} {base_winner.name:6s}({base_winner.ideology:5.2f}) twin_test winner {new_winner.name:6s}({new_winner.ideology:5.2f})")
            toxic_success += 1
            continue

        if (new_winner.tag != base_winner.tag and new_winner.name != toxic_twin.name):
            toxic_flip += 1
            
            # Create toxic twin of the opposition winner
            opposition_toxic_twin = toxic_analyzer.apply_toxic_tactics(new_winner)
            opposition_toxic_twin.name = f"toxic-{new_winner.name}"
            
            # Create third election with 4 candidates:
            # base_winner, toxic_twin, new_winner, opposition_toxic_twin

            third_candidates = [base_winner, toxic_twin, new_winner, opposition_toxic_twin]
            third_result = run_primary_election(third_candidates, population, config, gaussian_generator)
            third_winner = third_result.winner()
            
            if third_winner.name == opposition_toxic_twin.name:
                toxic_success += 1
                print(f"toxic success: lean={lean:3d} {base_winner.name:6s}({base_winner.ideology:5.2f}) toxic_twin winner {new_winner.name:6s}({new_winner.ideology:5.2f}) (flip)")
            else:
                toxic_failed += 1
                print(f"toxic failure: lean={lean:3d} {base_winner.name:6s}({base_winner.ideology:5.2f}) toxic_twin winner {new_winner.name:6s}({new_winner.ideology:5.2f}) (flip)")

    print(f"toxic_failed={toxic_failed} toxic_success={toxic_success} toxic_flip={toxic_flip}")
        

            
if __name__ == "__main__":
    main()