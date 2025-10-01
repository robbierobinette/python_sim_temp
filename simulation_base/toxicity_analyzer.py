"""
Toxicity analysis for election simulations.
"""
from typing import List, Dict
from .candidate import Candidate
from .population_tag import DEMOCRATS, REPUBLICANS, INDEPENDENTS
from .election_definition import ElectionDefinition
from .gaussian_generator import GaussianGenerator
from .election_process import ElectionProcess


class ToxicityAnalyzer:
    """Analyzes the effects of toxic tactics in elections."""
    
    def __init__(self, toxic_bonus: float = 0.25, toxic_penalty: float = -1.0):
        """Initialize toxicity analyzer."""
        self.toxic_bonus = toxic_bonus
        self.toxic_penalty = toxic_penalty
    
    def apply_toxic_tactics(self, candidate: Candidate) -> Candidate:
        """Apply toxic tactics to a candidate's affinity map."""
        # Create a copy of the candidate with modified affinity
        new_affinity = candidate._affinity_map.copy()
        
        # Apply toxic bonus to own party
        own_party_short = candidate.tag.short_name
        if own_party_short in new_affinity:
            new_affinity[own_party_short] += self.toxic_bonus
        
        # Apply toxic penalty to opposition party
        opposition_party = self._get_opposition_party(candidate.tag)
        if opposition_party.short_name in new_affinity:
            new_affinity[opposition_party.short_name] += self.toxic_penalty
        
        # Create new candidate with toxic affinity
        toxic_candidate = Candidate(
            name=candidate.name,
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
        toxic_candidate_map = {c.name:c for c in toxic_candidates}
        base_candidate_map = {c.name:c for c in election_def.candidates}
        # Test each losing candidate with toxic tactics
        toxic_wins = []
        for candidate in election_def.candidates:
            if candidate.name != base_winner.name:
                # Create modified election with this candidate using toxic tactics
                modified_candidates = [toxic_candidate_map[c.name] if c.name == candidate.name else base_candidate_map[c.name]
                                    for c in election_def.candidates]

                modified_election_def = ElectionDefinition(
                    candidates=modified_candidates,
                    population=election_def.population,
                    config=election_def.config,
                    gaussian_generator=election_def.gaussian_generator
                )
                
                # Run election with toxic candidate
                toxic_result = self._run_election(modified_election_def, election_process, gaussian_generator)
                
                if toxic_result.winner().name == candidate.name:
                    print(f"Toxic winner: {candidate.name}")
                    
                    # If this is a head-to-head result, print pairwise outcomes
                    if hasattr(toxic_result, 'print_pairwise_outcomes'):
                        for p in election_def.population.populations:
                            print(f"{p.tag.short_name:6s} {p.weight:6.2f}")
                        toxic_result.print_pairwise_outcomes()
                    
                    toxic_wins.append({
                        'candidate': candidate,
                        'original_winner': base_winner,
                        'district': getattr(election_def, 'district', 'Unknown')
                    })
        
        return {
            'base_winner': base_winner,
            'toxic_wins': toxic_wins,
            'total_candidates': len(election_def.candidates)
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
            gaussian_generator=election_def.gaussian_generator
        )

        
        # Run toxic base election
        toxic_result = self._run_election(toxic_election_def, election_process, gaussian_generator)
        toxic_winner = toxic_result.winner()
        
        toxic_candidate_map = {c.name:c for c in toxic_candidates}
        base_candidate_map = {c.name:c for c in election_def.candidates}

        # Test each losing candidate by removing toxic tactics
        non_toxic_wins = []
        for i, candidate in enumerate(election_def.candidates):
            if candidate.name != toxic_winner.name:
                # Create modified election with this candidate rejecting toxic tactics
                modified_candidates = [base_candidate_map[c.name] if c.name == candidate.name else toxic_candidate_map[c.name]
                                    for c in election_def.candidates]
                
                modified_election_def = ElectionDefinition(
                    candidates=modified_candidates,
                    population=election_def.population,
                    config=election_def.config,
                    gaussian_generator=election_def.gaussian_generator
                )
                
                # Run election with non-toxic candidate
                non_toxic_result = self._run_election(modified_election_def, election_process, gaussian_generator)
                
                if non_toxic_result.winner().name == candidate.name:
                    non_toxic_wins.append({
                        'candidate': candidate,
                        'original_winner': toxic_winner,
                        'district': getattr(election_def, 'district', 'Unknown')
                    })
        
        return {
            'toxic_winner': toxic_winner,
            'non_toxic_wins': non_toxic_wins,
            'total_candidates': len(election_def.candidates)
        }
    
    def _run_election(self, election_def: ElectionDefinition, election_process: ElectionProcess, 
                     gaussian_generator: GaussianGenerator):
        """Run an election with the given definition and process."""
        # All election processes now implement the ElectionProcess interface
        return election_process.run(election_def)
    
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
            gaussian_generator=election_def.gaussian_generator
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
                gaussian_generator=election_def.gaussian_generator
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
            return {
                'scenario': 'unexpected',
                'base_winner': base_winner,
                'new_winner': new_winner,
                'toxic_twin': toxic_twin,
                'third_winner': None,
                'opposition_toxic_twin': None
            }
    
    def analyze_district_toxicity(self, election_def: ElectionDefinition, 
                                 election_process: ElectionProcess, gaussian_generator: GaussianGenerator) -> Dict:
        """Comprehensive toxicity analysis for a single district."""
        
        # Run base election
        base_result = self._run_election(election_def, election_process, gaussian_generator)
        base_winner = base_result.winner()
        
        # Test twin scenarios (non-toxic base)
        twin_result = self.test_twin_scenarios(election_def, election_process, gaussian_generator)
        
        # Test toxic base scenario
        toxic_candidates = [self.apply_toxic_tactics(c) for c in election_def.candidates]
        toxic_election_def = ElectionDefinition(
            candidates=toxic_candidates,
            population=election_def.population,
            config=election_def.config,
            gaussian_generator=election_def.gaussian_generator
        )
        
        # Run toxic base election
        toxic_result = self._run_election(toxic_election_def, election_process, gaussian_generator)
        toxic_winner = toxic_result.winner()
        
        # Find the original candidate for toxic base analysis
        original_candidate = None
        for candidate in election_def.candidates:
            if (candidate.ideology == toxic_winner.ideology and 
                candidate.tag == toxic_winner.tag and
                candidate.quality == toxic_winner.quality):
                original_candidate = candidate
                break
        
        # Test non-toxic twin in toxic environment
        toxic_base_analysis = {
            'toxic_winner': toxic_winner,
            'non_toxic_twin_wins': False,
            'opposition_wins': False,
            'original_winner_wins': False
        }
        
        if original_candidate:
            # Create non-toxic twin
            import copy
            non_toxic_twin = copy.deepcopy(original_candidate)
            non_toxic_twin.name = f"non-toxic-{original_candidate.name}"
            
            # Create election with non-toxic twin vs other toxic candidates
            non_toxic_candidates = []
            for candidate in toxic_candidates:
                if (candidate.ideology == toxic_winner.ideology and 
                    candidate.tag == toxic_winner.tag and
                    candidate.quality == toxic_winner.quality):
                    non_toxic_candidates.append(non_toxic_twin)
                else:
                    non_toxic_candidates.append(candidate)
            
            non_toxic_election_def = ElectionDefinition(
                candidates=non_toxic_candidates,
                population=election_def.population,
                config=election_def.config,
                gaussian_generator=election_def.gaussian_generator
            )
            
            non_toxic_base_result = self._run_election(non_toxic_election_def, election_process, gaussian_generator)
            non_toxic_base_winner = non_toxic_base_result.winner()
            
            if non_toxic_base_winner.name == non_toxic_twin.name:
                toxic_base_analysis['non_toxic_twin_wins'] = True
            elif non_toxic_base_winner.tag != toxic_winner.tag:
                toxic_base_analysis['opposition_wins'] = True
            else:
                toxic_base_analysis['original_winner_wins'] = True
        
        # Test individual candidate toxic scenarios
        individual_toxic_wins = []
        for candidate in election_def.candidates:
            if candidate.name != base_winner.name:
                # Create modified election with this candidate using toxic tactics
                modified_candidates = []
                for c in election_def.candidates:
                    if c.name == candidate.name:
                        modified_candidates.append(self.apply_toxic_tactics(c))
                    else:
                        modified_candidates.append(c)
                
                modified_election_def = ElectionDefinition(
                    candidates=modified_candidates,
                    population=election_def.population,
                    config=election_def.config,
                    gaussian_generator=election_def.gaussian_generator
                )
                
                # Run election with toxic candidate
                toxic_result = self._run_election(modified_election_def, election_process, gaussian_generator)
                
                if toxic_result.winner().name == candidate.name:
                    individual_toxic_wins.append({
                        'candidate': candidate,
                        'original_winner': base_winner
                    })
        
        # Test individual candidate non-toxic scenarios
        individual_non_toxic_wins = []
        for candidate in election_def.candidates:
            if candidate.name != toxic_winner.name:
                # Create modified election with this candidate rejecting toxic tactics
                modified_candidates = []
                for c in toxic_candidates:
                    if c.name == candidate.name:
                        # Find original candidate
                        original_c = None
                        for orig_c in election_def.candidates:
                            if (orig_c.ideology == c.ideology and 
                                orig_c.tag == c.tag and
                                orig_c.quality == c.quality):
                                original_c = orig_c
                                break
                        if original_c:
                            modified_candidates.append(original_c)
                        else:
                            modified_candidates.append(c)
                    else:
                        modified_candidates.append(c)
                
                modified_election_def = ElectionDefinition(
                    candidates=modified_candidates,
                    population=election_def.population,
                    config=election_def.config,
                    gaussian_generator=election_def.gaussian_generator
                )
                
                # Run election with non-toxic candidate
                non_toxic_result = self._run_election(modified_election_def, election_process, gaussian_generator)
                
                if non_toxic_result.winner().name == candidate.name:
                    individual_non_toxic_wins.append({
                        'candidate': candidate,
                        'original_winner': toxic_winner
                    })
        
        return {
            'district': getattr(election_def, 'district', 'Unknown'),
            'base_winner': base_winner,
            'toxic_winner': toxic_winner,
            'twin_scenario': twin_result,
            'toxic_base_analysis': toxic_base_analysis,
            'individual_toxic_wins': individual_toxic_wins,
            'individual_non_toxic_wins': individual_non_toxic_wins,
            'total_candidates': len(election_def.candidates)
        }
    
    def analyze_toxicity_effects(self, district_results: List[Dict]) -> Dict:
        """Analyze the overall effects of toxicity across all districts."""
        total_districts = len(district_results)
        
        # Phase 1: Base → Toxic (count districts where at least one candidate could win with toxic tactics)
        toxic_changeable = sum(1 for result in district_results if result['toxic_wins'])
        toxic_changeable_pct = (toxic_changeable / total_districts) * 100 if total_districts > 0 else 0
        
        # Phase 2: Toxic → Non-Toxic (count districts where at least one candidate could win by rejecting toxic tactics)
        non_toxic_changeable = sum(1 for result in district_results if result['non_toxic_wins'])
        non_toxic_changeable_pct = (non_toxic_changeable / total_districts) * 100 if total_districts > 0 else 0
        
        return {
            'total_districts': total_districts,
            'toxic_changeable': toxic_changeable,
            'toxic_changeable_pct': toxic_changeable_pct,
            'non_toxic_changeable': non_toxic_changeable,
            'non_toxic_changeable_pct': non_toxic_changeable_pct
        }
