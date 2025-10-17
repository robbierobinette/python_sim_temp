"""
Toxicity analysis for election simulations.
"""
from typing import List, Dict
from .candidate import Candidate
from .population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from .election_definition import ElectionDefinition
from .gaussian_generator import GaussianGenerator
from .election_process import ElectionProcess
from .ballot import RCVBallot

class ToxicityAnalyzer:
    """Analyzes the effects of toxic tactics in elections."""
    
    def __init__(self, toxic_bonus: float = 0.25, toxic_penalty: float = -1.0):
        """Initialize toxicity analyzer."""
        self.toxic_bonus = toxic_bonus
        self.toxic_penalty = toxic_penalty

    def remove_balanced_candidates(self, candidates: List[Candidate]) -> List[Candidate]:
        return [c for c in candidates if c.name[1:] != "-V"]
    
    def apply_toxic_tactics(self, candidate: Candidate) -> Candidate:
        """Apply toxic tactics to a candidate's affinity map."""
        # Create a copy of the candidate with modified affinity
        new_affinity = candidate._affinity_map.copy()
        
        # Apply toxic bonus to own party
        new_affinity[candidate.tag.short_name] += self.toxic_bonus
        
        # Apply toxic penalty to opposition party
        opposition_party = self._get_opposition_party(candidate.tag)
        new_affinity[opposition_party.short_name] += self.toxic_penalty
        
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
    
    
    def _get_opposition_party(self, party_tag):
        """Get the opposition party for a given party."""
        if party_tag == DEMOCRATS:
            return REPUBLICANS
        elif party_tag == REPUBLICANS:
            return DEMOCRATS
        else:
            return INDEPENDENTS  # For independents, opposition is also independent
    
    def test_toxic_scenarios(self, election_def: ElectionDefinition, 
                           election_process: ElectionProcess, gaussian_generator: GaussianGenerator) -> Dict:
        """Test if losing candidates could win with toxic tactics."""
        # Run base election
        base_result = self._run_election(election_def, election_process, gaussian_generator)
        base_winner = base_result.winner()
        
        toxic_candidates = [self.apply_toxic_tactics(c) for c in election_def.candidates]
        
        # Test each losing candidate with toxic tactics
        toxic_success = False
        toxic_winner = None
        for i, candidate in enumerate(election_def.candidates):
            # Create modified election with this candidate using toxic tactics
            modified_candidates = election_def.candidates.copy()
            if base_winner.name == candidate.name:
                modified_candidates.append(toxic_candidates[i])
            else:
                modified_candidates[i] = toxic_candidates[i]

            modified_election_def = ElectionDefinition(
                candidates=modified_candidates,
                population=election_def.population,
                config=election_def.config,
                gaussian_generator=election_def.gaussian_generator,
                state=election_def.state
            )
            
            # Run election with toxic candidate
            toxic_result = self._run_election(modified_election_def, election_process, gaussian_generator)
            
            if toxic_result.winner().name == toxic_candidates[i].name:
                toxic_success = True
                toxic_winner = toxic_result.winner()
                break
        
        return {
            'base_winner': base_winner,
            'toxic_success': toxic_success,
            'toxic_winner': toxic_winner
        }
    
    def test_non_toxic_scenarios(self, election_def: ElectionDefinition,
                                election_process: ElectionProcess, gaussian_generator: GaussianGenerator) -> Dict:
        """Test if losing candidates could win by rejecting toxic tactics."""
        # Create toxic base election (all candidates use toxic tactics)
        toxic_candidates = [self.apply_toxic_tactics(c) for c in election_def.candidates]

        toxic_election_def = ElectionDefinition(
            candidates=toxic_candidates,
            population=election_def.population,
            config=election_def.config,
            gaussian_generator=election_def.gaussian_generator,
            state=election_def.state
        )
        
        # Run toxic base election
        toxic_result = self._run_election(toxic_election_def, election_process, gaussian_generator)
        toxic_winner = toxic_result.winner()
        

        # Test each losing candidate by removing toxic tactics
        non_toxic_success = False
        for i, candidate in enumerate(election_def.candidates):

            # skip the original winner, they may be the only viable candidate.
            if toxic_winner.name == toxic_candidates[i].name:
                continue

            # try replace each candidate with
            # a non-toxic candidate
            new_candidates = toxic_candidates.copy()
            new_candidates[i] = candidate
            
            
            modified_election_def = ElectionDefinition(
                candidates=new_candidates,
                population=election_def.population,
                config=election_def.config,
                gaussian_generator=election_def.gaussian_generator,
                state=election_def.state
            )
            
            # Run election with non-toxic candidate
            non_toxic_result = self._run_election(modified_election_def, election_process, gaussian_generator)
            
            if non_toxic_result.winner().name == candidate.name:
                print(  f"Non-toxic success in district {election_def.state}-{election_def.district()} " + 
                        f"lean {election_def.population.district.lean:.1f} " +
                        f"toxic winner {toxic_winner.name} " +
                        f"non-toxic winner {candidate.name} ")
                print("general election votes:")
                for cs in non_toxic_result.ordered_results():
                    print(f"  {cs.candidate.name}: {cs.votes}")

                non_toxic_success = True
                break
        
        return {
            'toxic_winner': toxic_winner,
            'non_toxic_success': non_toxic_success,
            'total_candidates': len(election_def.candidates)
        }
    
    def _run_election(self, election_def: ElectionDefinition, election_process: ElectionProcess, 
                     gaussian_generator: GaussianGenerator):
        """Run an election with the given definition and process."""
        # All election processes now implement the ElectionProcess interface
        ballots = [RCVBallot(voter, election_def.candidates, election_def.config, gaussian_generator) for voter in election_def.population.voters]
        return election_process.run(election_def.candidates, ballots)
    
    def test_twin_scenarios(self, election_def: ElectionDefinition, 
                           election_process: ElectionProcess, gaussian_generator: GaussianGenerator) -> Dict:
        """Test the twin scenario: base winner vs toxic twin vs opposition candidates."""
        # Run base election
        base_result = self._run_election(election_def, election_process, gaussian_generator)
        base_winner = base_result.winner()
        
        # Create toxic twin of base winner
        toxic_twin = self.apply_toxic_tactics(base_winner)
        toxic_twin.name = f"toxic-{base_winner.name}"
        
        # Create second election: opposition candidates + toxic twin + base winner
        new_candidates = []
        for candidate in election_def.candidates:
            if candidate.tag != base_winner.tag:
                new_candidates.append(candidate)
        
        new_candidates.append(toxic_twin)
        new_candidates.append(base_winner)
        
        new_election_def = ElectionDefinition(
            candidates=new_candidates,
            population=election_def.population,
            config=election_def.config,
            gaussian_generator=election_def.gaussian_generator,
            state=election_def.state
        )
        
        new_result = self._run_election(new_election_def, election_process, gaussian_generator)
        new_winner = new_result.winner()
        
        # Analyze results
        if new_winner.name == base_winner.name:
            return {
                'scenario': 'toxic_failure',
                'base_winner': base_winner,
                'new_winner': new_winner,
                'toxic_twin': toxic_twin,
                'third_winner': None,
                'opposition_toxic_twin': None
            }
        elif new_winner.name == toxic_twin.name:
            return {
                'scenario': 'toxic_success',
                'base_winner': base_winner,
                'new_winner': new_winner,
                'toxic_twin': toxic_twin,
                'third_winner': None,
                'opposition_toxic_twin': None
            }
        elif (new_winner.tag != base_winner.tag and new_winner.name != toxic_twin.name):
            # Third election: test if opposition winner can beat their own toxic competition
            opposition_toxic_twin = self.apply_toxic_tactics(new_winner)
            opposition_toxic_twin.name = f"toxic-{new_winner.name}"
            
            third_candidates = [base_winner, toxic_twin, new_winner, opposition_toxic_twin]
            third_election_def = ElectionDefinition(
                candidates=third_candidates,
                population=election_def.population,
                config=election_def.config,
                gaussian_generator=election_def.gaussian_generator,
                state=election_def.state
            )
            
            third_result = self._run_election(third_election_def, election_process, gaussian_generator)
            third_winner = third_result.winner()
            
            if third_winner.name == opposition_toxic_twin.name:
                return {
                    'scenario': 'toxic_success_flip',
                    'base_winner': base_winner,
                    'new_winner': new_winner,
                    'toxic_twin': toxic_twin,
                    'third_winner': third_winner,
                    'opposition_toxic_twin': opposition_toxic_twin
                }
            else:
                return {
                    'scenario': 'toxic_failure_flip',
                    'base_winner': base_winner,
                    'new_winner': new_winner,
                    'toxic_twin': toxic_twin,
                    'third_winner': third_winner,
                    'opposition_toxic_twin': opposition_toxic_twin
                }
        else:
            raise RuntimeError(f"Unexpected scenario in toxicity analysis: base_winner={base_winner}, new_winner={new_winner}, toxic_twin={toxic_twin}")
    
    def analyze_district_toxicity(self, election_def: ElectionDefinition, 
                                 election_process: ElectionProcess, gaussian_generator: GaussianGenerator) -> Dict:
        """Comprehensive toxicity analysis for a single district."""

        # filter out candidates the balanced candidates
        election_def.candidates = self.remove_balanced_candidates(election_def.candidates)
        # Use existing methods to get comprehensive analysis
        twin_result = self.test_twin_scenarios(election_def, election_process, gaussian_generator)
        toxic_scenario_result = self.test_toxic_scenarios(election_def, election_process, gaussian_generator)
        non_toxic_scenario_result = self.test_non_toxic_scenarios(election_def, election_process, gaussian_generator)
        
        # Extract key information
        base_winner = twin_result['base_winner']
        toxic_winner = non_toxic_scenario_result['toxic_winner']
        
        # Analyze toxic base scenario using twin logic
        toxic_base_analysis = {
            'toxic_winner': toxic_winner,
            'non_toxic_twin_wins': False,
            'opposition_wins': False,
            'original_winner_wins': False
        }
        
        # Test if non-toxic tactics could succeed in toxic environment
        if non_toxic_scenario_result['non_toxic_success']:
            toxic_base_analysis['non_toxic_twin_wins'] = True
        else:
            toxic_base_analysis['original_winner_wins'] = True
        
        return {
            'district': getattr(election_def, 'district', 'Unknown'),
            'base_winner': base_winner,
            'toxic_winner': toxic_winner,
            'twin_scenario': twin_result,
            'toxic_base_analysis': toxic_base_analysis,
            'toxic_success': toxic_scenario_result['toxic_success'],
            'non_toxic_success': non_toxic_scenario_result['non_toxic_success'],
        }
    
    def analyze_toxicity_effects(self, district_results: List[Dict]) -> Dict:
        """Analyze the overall effects of toxicity across all districts."""
        total_districts = len(district_results)
        
        # Phase 1: Base → Toxic (count districts where at least one candidate could win with toxic tactics)
        toxic_changeable = sum(1 for result in district_results if result.get('toxic_success', False))
        toxic_changeable_pct = (toxic_changeable / total_districts) * 100 if total_districts > 0 else 0
        
        # Phase 2: Toxic → Non-Toxic (count districts where at least one candidate could win by rejecting toxic tactics)
        non_toxic_changeable = sum(1 for result in district_results if result.get('non_toxic_success', False))
        non_toxic_changeable_pct = (non_toxic_changeable / total_districts) * 100 if total_districts > 0 else 0
        
        return {
            'total_districts': total_districts,
            'toxic_changeable': toxic_changeable,
            'toxic_changeable_pct': toxic_changeable_pct,
            'non_toxic_changeable': non_toxic_changeable,
            'non_toxic_changeable_pct': non_toxic_changeable_pct
        }
