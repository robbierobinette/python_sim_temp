"""
ActualCustom election type that creates custom composable elections based on state specifications.
"""
import json
from typing import List, Dict, Any
from .election_process import ElectionProcess
from .election_result import ElectionResult
from .candidate import Candidate
from .ballot import RCVBallot
from .composable_election import ComposableElection, ComposableElectionResult
from .closed_primary import ClosedPrimary
from .open_primary import OpenPrimary
from .topn_primary import TopNPrimary
from .simple_plurality import SimplePlurality
from .instant_runoff_election import InstantRunoffElection
from .plurality_with_runoff import PluralityWithRunoff
from .condorcet_election import CondorcetElection


class ActualCustomElection(ElectionProcess):
    """Custom election process that uses state-specific election configurations."""
    
    def __init__(self, state_abbr: str, primary_skew: float, debug: bool):
        """Initialize ActualCustom election.
        
        Args:
            state_abbr: Two-letter state abbreviation (e.g., 'CA', 'TX', 'NY')
            primary_skew: Skew factor for primary elections
            debug: Whether to enable debug output
        """
        self.state_abbr = state_abbr.upper()
        self.primary_skew = primary_skew
        self.debug = debug
        self._election_config = None
        self._composable_election = None
        
        # Load and validate state configuration
        self._load_state_config()
        self._create_composable_election()
    
    def _load_state_config(self) -> None:
        """Load election configuration for the specified state."""
        try:
            with open("election_types.json", "r") as f:
                election_types = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError("election_types.json not found in current directory")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in election_types.json: {e}")
        
        # Find state by abbreviation
        state_config = None
        for state_name, config in election_types.items():
            if config.get("abbr") == self.state_abbr:
                state_config = config
                break
        
        if state_config is None:
            raise ValueError(f"No election configuration found for state abbreviation '{self.state_abbr}'")
        
        self._election_config = state_config
        
        if self.debug:
            print(f"Loaded election config for {self.state_abbr}: {state_config}")
    
    def _create_composable_election(self) -> None:
        """Create the composable election based on state configuration."""
        if self._election_config is None:
            raise RuntimeError("State configuration not loaded")
        
        # Special case for Louisiana-2: single PluralityWithRunoff process
        if self._election_config.get("primary") == "Louisiana-2":
            self._composable_election = PluralityWithRunoff(debug=self.debug)
            if self.debug:
                print(f"Created Louisiana-2 election for {self.state_abbr}: single PluralityWithRunoff")
            return
        
        # Create primary process
        primary_process = self._create_primary_process()
        
        # Create general process
        general_process = self._create_general_process()
        
        # Create composable election
        self._composable_election = ComposableElection(
            primary_process=primary_process,
            general_process=general_process,
            debug=self.debug
        )
        
        if self.debug:
            print(f"Created ActualCustom election for {self.state_abbr}: "
                  f"primary={self._election_config['primary']}, "
                  f"general={self._election_config['general']}")
    
    def _create_primary_process(self) -> ElectionProcess:
        """Create the appropriate primary election process."""
        primary_type = self._election_config.get("primary")
        primary_runoff = self._election_config.get("primary_runoff", False)
        
        if primary_type == "closed-partisan":
            return ClosedPrimary(
                use_runoff=primary_runoff, 
                primary_skew=self.primary_skew, 
                debug=self.debug
            )
        elif primary_type == "open-partisan":
            return OpenPrimary(
                use_runoff=primary_runoff, 
                primary_skew=self.primary_skew, 
                debug=self.debug,
                semi_closed=False
            )
        elif primary_type == "top-2":
            return TopNPrimary(n=2, primary_skew=self.primary_skew, debug=self.debug)
        elif primary_type == "top-4":
            return TopNPrimary(n=4, primary_skew=self.primary_skew, debug=self.debug)
        elif primary_type == "top-5":
            return TopNPrimary(n=5, primary_skew=self.primary_skew, debug=self.debug)
        elif primary_type == "semi-closed-partisan":
            return OpenPrimary(
                use_runoff=primary_runoff, 
                primary_skew=self.primary_skew, 
                debug=self.debug,
                semi_closed=True
            )
    
    def _create_general_process(self) -> ElectionProcess:
        """Create the appropriate general election process."""
        general_type = self._election_config.get("general", "plurality")
        general_runoff = self._election_config.get("general_runoff", False)
        
        if general_type == "plurality":
            if general_runoff:
                return PluralityWithRunoff(debug=self.debug)
            else:
                return SimplePlurality(debug=self.debug)
        elif general_type == "IRV":
            return InstantRunoffElection(debug=self.debug)
        elif general_type == "CCV":
            return CondorcetElection(debug=self.debug)
        else:
            raise ValueError(f"bad general_election type: {general_type}")
    @property
    def name(self) -> str:
        """Name of the election process."""
        return f"actual_custom_{self.state_abbr}"
    
    def run(self, candidates: List[Candidate], ballots: List[RCVBallot]) -> ElectionResult:
        """Run the custom election for the specified state.
        
        Args:
            candidates: List of candidates in the election
            ballots: List of ballots from voters
            
        Returns:
            ElectionResult with results from the election process
        """
        if self._composable_election is None:
            raise RuntimeError("Composable election not initialized")
        
        if self.debug:
            print(f"Running ActualCustom election for {self.state_abbr}")
        
        return self._composable_election.run(candidates, ballots)
    
    def get_state_config(self) -> Dict[str, Any]:
        """Get the election configuration for this state."""
        return self._election_config.copy() if self._election_config else {}
    
    def get_election_description(self) -> str:
        """Get a human-readable description of the election type."""
        if not self._election_config:
            return f"Unknown election type for {self.state_abbr}"
        
        primary_name = self._election_config['primary']
        if self._election_config.get('primary_runoff', False):
            primary_name += "-R"
        
        general_name = self._election_config['general']
        if self._election_config.get('general_runoff', False):
            general_name += "-R"
        
        return f"{primary_name}-{general_name}"
