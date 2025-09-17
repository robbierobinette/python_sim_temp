"""
Gaussian random number generator for simulation.
"""
import random
import math
from typing import Optional


class GaussianGenerator:
    """Generates Gaussian random numbers for simulation."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize with optional seed."""
        self._random = random.Random(seed)
    
    def set_seed(self, seed: int) -> None:
        """Set the random seed."""
        self._random.seed(seed)
    
    def next_boolean(self) -> bool:
        """Generate random boolean."""
        return self._random.choice([True, False])
    
    def next_int(self) -> int:
        """Generate random integer."""
        return self._random.randint(-2**31, 2**31 - 1)
    
    def __call__(self) -> float:
        """Generate Gaussian random number."""
        return self._random.gauss(0, 1)


# Global generator instance
_generator = GaussianGenerator()


def next_gaussian() -> float:
    """Get next Gaussian random number from global generator."""
    return _generator()


def set_seed(seed: int) -> None:
    """Set seed for global generator."""
    _generator.set_seed(seed)
