"""
Gaussian random number generator for simulation.
"""
import random
from typing import Optional

_global_seed = None

class GaussianGenerator:
    """Generates Gaussian random numbers for simulation."""

    def __init__(self, seed: Optional[int] = None):
        """Initialize with optional seed."""
        # ensure that if there is a seed on the initial call to GaussianGenerator, 
        # that we produce a deterministic and reproducable sequence of random numbers

        global _global_seed
        if _global_seed is None:
            if seed is None:
                # if no seed is provided, use a randomly generated seed
                seed = random.randint(0, 1000000)
                # print the seed used so that these results can be reproduced
                print(f"GaussianGenerator: random seed: {seed}")
            self._random = random.Random(seed)
            _global_seed = seed
        else:
            # already created a generator, so increment whatever seed we are using
            _global_seed += 1
            self._random = random.Random(_global_seed)

    def next_boolean(self) -> bool:
        """Generate random boolean."""
        return self._random.choice([True, False])
    
    def next_int(self) -> int:
        """Generate random integer."""
        return self._random.randint(-2**31, 2**31 - 1)
    
    def next_float(self) -> float:
        """Generate random float."""
        return self._random.random()
    
    def __call__(self) -> float:
        """Generate Gaussian random number."""
        v = self._random.gauss(0, 1)
        return v

    @staticmethod
    def reset_global_seed() -> None:
        """Reset the global seed."""
        global _global_seed
        _global_seed = None

