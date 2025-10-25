"""
Smart primary election that reads election_types.json and creates the appropriate ComposableElection.
"""
import json
import os
from typing import Dict, Any, List
from .election_process import ElectionProcess
from .ballot import RCVBallot
from .election_result import ElectionResult
from .composable_election import ComposableElection
from .closed_primary import ClosedPrimary, ClosedPrimaryConfig
from .open_primary import OpenPrimary, OpenPrimaryConfig
from .topn_primary import TopNPrimary
from .candidate import Candidate
from .simple_plurality import SimplePlurality
from .instant_runoff_election import InstantRunoffElection
from .plurality_with_runoff import PluralityWithRunoff


class SmartPrimaryElection(ElectionProcess):
    """Smart primary election that creates the appropriate ComposableElection based on state."""
    
    def __init__(self, election_types_file: str, debug: bool):
        """Initialize smart primary election.
        
        Args:
            election_types_file: Path to the election types JSON file
            debug: Whether to enable debug output
        """
        self.election_types_file = election_types_file
        self.debug = debug
        self._election_types = None
        self._election_cache = {}  # Cache for created elections
    
    def _load_election_types(self) -> Dict[str, Any]:
        """Load election types from JSON file."""
        if self._election_types is None:
            # Get the directory of this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Go up one level to the project root
            project_root = os.path.dirname(current_dir)
            file_path = os.path.join(project_root, self.election_types_file)
            
            try:
                with open(file_path, 'r') as f:
                    self._election_types = json.load(f)
            except FileNotFoundError:
                if self.debug:
                    print(f"Warning: {file_path} not found, using default TX configuration")
                # Default to Texas configuration
                self._election_types = {
                    "Texas": {
                        "abbr": "TX",
                        "primary": "open-partisan",
                        "primary_runoff": True,
                        "general": "plurality",
                        "general_runoff": False
                    }
                }
            except json.JSONDecodeError as e:
                if self.debug:
                    print(f"Warning: Error parsing {file_path}: {e}, using default TX configuration")
                # Default to Texas configuration
                self._election_types = {
                    "Texas": {
                        "abbr": "TX",
                        "primary": "open-partisan",
                        "primary_runoff": True,
                        "general": "plurality",
                        "general_runoff": False
                    }
                }
        
        return self._election_types
    
    def _get_state_config(self, state: str) -> Dict[str, Any]:
        """Get election configuration for a state."""
        election_types = self._load_election_types()
        
        # Find state by abbreviation
        for state_name, config in election_types.items():
            if config.get("abbr") == state.upper():
                return config
        
        # Default to Texas if state not found
        if self.debug:
            print(f"Warning: State {state} not found in election types, using TX default")
        return {
            "abbr": "TX",
            "primary": "open-partisan",
            "primary_runoff": True,
            "general": "plurality",
            "general_runoff": False
        }
    
    def _create_primary_process(self, state_config: Dict[str, Any]) -> ElectionProcess:
        """Create the appropriate primary election process."""
        primary_type = state_config.get("primary", "open-partisan")
        primary_runoff = state_config.get("primary_runoff", False)
        
        if primary_type == "closed-partisan":
            config = ClosedPrimaryConfig(use_runoff=primary_runoff)
            return ClosedPrimary(config=config, debug=self.debug)
        
        elif primary_type == "open-partisan":
            config = OpenPrimaryConfig(use_runoff=primary_runoff)
            return OpenPrimary(config=config, debug=self.debug)
        
        elif primary_type == "top-2":
            return TopNPrimary(n=2, debug=self.debug)
        
        elif primary_type == "top-4":
            return TopNPrimary(n=4, debug=self.debug)
        
        elif primary_type == "semi-closed-partisan":
            # For now, treat semi-closed as closed
            if self.debug:
                print("Warning: semi-closed primary not implemented, using closed")
            config = ClosedPrimaryConfig(use_runoff=primary_runoff)
            return ClosedPrimary(config=config, debug=self.debug)
        
        else:
            if self.debug:
                print(f"Warning: Unknown primary type '{primary_type}', using open-partisan")
            config = OpenPrimaryConfig(use_runoff=primary_runoff)
            return OpenPrimary(config=config, debug=self.debug)
    
    def _create_general_process(self, state_config: Dict[str, Any]) -> ElectionProcess:
        """Create the appropriate general election process."""
        general_type = state_config.get("general", "plurality")
        general_runoff = state_config.get("general_runoff", False)
        
        if general_type == "plurality":
            if general_runoff:
                return PluralityWithRunoff(debug=self.debug)
            else:
                return SimplePlurality(debug=self.debug)
        
        elif general_type == "IRV":
            return InstantRunoffElection(debug=self.debug)
        
        else:
            if self.debug:
                print(f"Warning: Unknown general type '{general_type}', using plurality")
            if general_runoff:
                return PluralityWithRunoff(debug=self.debug)
            else:
                return SimplePlurality(debug=self.debug)
    
    def _get_election_for_state(self, state: str) -> ComposableElection:
        """Get or create the ComposableElection for a state."""
        if state not in self._election_cache:
            state_config = self._get_state_config(state)
            
            primary_process = self._create_primary_process(state_config)
            general_process = self._create_general_process(state_config)
            
            self._election_cache[state] = ComposableElection(
                primary_process=primary_process,
                general_process=general_process,
                debug=self.debug
            )
            
            if self.debug:
                print(f"Created election for {state}: primary={state_config['primary']}, general={state_config['general']}")
        
        return self._election_cache[state]
    
    @property
    def name(self) -> str:
        """Name of the election process."""
        return "smartPrimary"
    
    def run(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> ElectionResult:
        """Run smart primary election based on state configuration.
        
        Args:
            candidates: List of candidates in the election
            ballots: List of ballots from voters
            
        Returns:
            Election result from the appropriate ComposableElection
        """
        # For now, default to Texas configuration since we don't have state info in the new interface
        # TODO: Consider how to handle state-specific logic in the new interface
        state = "Texas"
        
        if self.debug:
            print(f"Running smart primary election for state: {state}")
        
        # Get the appropriate election for this state
        election = self._get_election_for_state(state)
        
        # Run the election
        return election.run(candidates, ballots)
