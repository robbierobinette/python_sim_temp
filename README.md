# Congressional Election Simulation

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

This Python implementation simulates elections for all 435 congressional districts using ranked choice voting (instant runoff). It's based on the Scala code in the `rcvcore` directory and uses data from the Cook Political Report.

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd python_election_sim
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   # On macOS/Linux:
   python3 -m venv venv
   source venv/bin/activate
   
   # On Windows:
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Alternatively, for development (includes testing tools):
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run the simulation**
   ```bash
   python main.py
   ```

That's it! The simulation will run and save results to `simulation_results.json`.

### Verifying Installation

To verify everything is working correctly, run the test suite:
```bash
pytest tests/
```

All tests should pass.

## Structure

The code is organized into two main parts:

### 1. Base Simulation Libraries (`simulation_base/`)

Core simulation components:
- **`population_tag.py`** - Political party definitions (Democrats, Republicans, Independents, etc.)
- **`candidate.py`** - Candidate representation with ideology, quality, and party affiliation
- **`voter.py`** - Voter behavior and ballot generation
- **`ballot.py`** - Ranked choice voting ballot implementation
- **`election_config.py`** - Election parameters (uncertainty, party loyalty, etc.)
- **`population_group.py`** - Voter population groups with statistical properties
- **`combined_population.py`** - Combined populations from multiple groups
- **`unit_population.py`** - Population generation for simulation
- **`district_voting_record.py`** - District voting history and characteristics
- **`candidate_generator.py`** - Various strategies for generating candidates
- **`simulation_config.py`** - Configuration for different simulation scenarios
- **`instant_runoff_election.py`** - Instant runoff voting implementation
- **`election_result.py`** - Election result representation
- **`election_definition.py`** - Complete election setup
- **`gaussian_generator.py`** - Random number generation for simulation

### 2. Congressional Simulation (`congressional_simulation.py`)

Main simulation logic:
- Loads district data from Cook Political Report CSV
- Simulates elections for all 435 districts
- Generates comprehensive results with statistics

## Usage

### Basic Usage

```bash
python main.py
```

This will:
- Load district data from `CookPoliticalData.csv`
- Run simulation with default unit configuration
- Save results to `simulation_results.json`
- Print summary statistics

### Advanced Usage

```bash
python main.py --help
```

Options:
- `--data-file`: Path to CSV file with district data
- `--output`: Output file for results
- `--seed`: Random seed for reproducible results
- `--candidates`: Number of candidates per party
- `--verbose`: Enable detailed output

### Examples

```bash
# Run with specific seed for reproducibility
python main.py --seed 42

# Run with 2 candidates per party
python main.py --candidates 2

# Verbose output with custom data file
python main.py --data-file my_districts.csv --verbose

# Generate and display plots
python main.py --plot

# Generate only the winner ideology histogram
python main.py --histogram-only

# Save plots to custom directory
python main.py --plot --plot-dir my_plots
```

## Data Format

The CSV file should have columns:
- `State`: State name
- `Number`: District number
- `Member`: Current representative name
- `Party`: Current party (R/D)
- `2025 Cook PVI`: Partisan Voting Index (e.g., "R+27", "D+5")

## Output

The simulation generates:
- **Summary statistics**: Party wins, percentages, voter satisfaction
- **District results**: Winner, margin, ideology, satisfaction for each district
- **JSON file**: Complete results for further analysis
- **Visualizations**: Histograms and plots of results (optional)

## Key Features

1. **Ranked Choice Voting**: Uses instant runoff voting for all elections
2. **Realistic Voter Behavior**: Voters consider ideology, party loyalty, candidate quality, and uncertainty
3. **Multiple Candidate Generation**: Various strategies for creating candidate fields
4. **Statistical Population Modeling**: Gaussian distributions for voter ideologies
5. **Comprehensive Results**: Detailed statistics and district-by-district results
6. **Data Visualization**: Histograms and plots for analysis of results

## Visualizations

The simulation can generate several types of visualizations:

1. **Winner Ideology Histogram**: Distribution of winning candidate ideologies by party
2. **Voter Satisfaction Histogram**: Distribution of voter satisfaction by winning party
3. **Ideology vs Satisfaction Scatter Plot**: Relationship between winner ideology and voter satisfaction
4. **Party Wins by State**: Bar chart showing party wins by state

Visualizations are saved as high-resolution PNG files and can be displayed interactively.

## Configuration

The simulation uses a single, optimized configuration:
- **Uncertainty**: 0.5 (moderate voter uncertainty)
- **Party Loyalty**: 1.0 (moderate party loyalty)
- **Quality Scale**: 1.0 (candidate quality impact)
- **Party Bonus Scale**: 1.0 (party affiliation bonus)
- **Wasted Vote Factor**: 0.0 (no wasted vote penalty)
- **Population Skew**: 0.5/30 (slight population skew)
- **Primary Skew**: 0.5 (moderate primary skew)

## Dependencies

The project has minimal dependencies to keep it lightweight:

- **matplotlib** (>=3.4.0) - For generating visualizations
- **numpy** (>=1.21.0, <2.0.0) - For numerical computations in plots
- **pytest** (>=7.0.0) - Optional, only needed for running tests

All dependencies are listed in `requirements.txt` and will be installed automatically when you run `pip install -r requirements.txt`.

## Troubleshooting

### Common Issues

**Issue: `ModuleNotFoundError: No module named 'matplotlib'`**
- **Solution**: Make sure you've activated your virtual environment and installed dependencies:
  ```bash
  source venv/bin/activate  # or venv\Scripts\activate on Windows
  pip install -r requirements.txt
  ```

**Issue: `FileNotFoundError: [Errno 2] No such file or directory: 'CookPoliticalData.csv'`**
- **Solution**: Make sure you're running the script from the project root directory where `CookPoliticalData.csv` is located:
  ```bash
  cd python_election_sim
  python main.py
  ```

**Issue: Tests fail with import errors**
- **Solution**: Install pytest and make sure the project is in your Python path:
  ```bash
  pip install pytest
  # Run from project root
  pytest tests/
  ```

**Issue: Plots don't display**
- **Solution**: On some systems (especially headless servers or WSL), matplotlib may need a different backend. Either:
  - Save plots to files instead of displaying: `python main.py --plot-dir output`
  - Or install a GUI backend for matplotlib (system-dependent)

### Getting Help

If you encounter issues not covered here:
1. Check that you're using Python 3.8 or higher: `python --version`
2. Verify all dependencies are installed: `pip list`
3. Try running the tests to isolate the issue: `pytest tests/ -v`

## Performance

The simulation typically takes:
- **Basic run** (435 districts): ~10-30 seconds
- **With visualizations**: ~30-60 seconds
- Running on a modern CPU with Python 3.9+

Results are deterministic when using the same random seed via `--seed` parameter.

## Project Structure

```
python_election_sim/
├── simulation_base/          # Core simulation engine
│   ├── ballot.py            # Ranked choice ballot implementation
│   ├── candidate.py         # Candidate representation
│   ├── voter.py             # Voter behavior
│   ├── election_*.py        # Various election types
│   └── ...
├── tests/                   # Comprehensive test suite
├── main.py                  # Main entry point
├── visualization.py         # Plotting utilities
├── CookPoliticalData.csv    # District data
├── requirements.txt         # Python dependencies
├── setup.py                # Package installation script
└── README.md               # This file
```

## Implementation Notes

This Python implementation closely follows the structure and logic of the original Scala code in `rcvcore/`, adapting the object-oriented design to Python idioms while maintaining the same simulation algorithms and parameters.

The simulation uses only Python standard library for core functionality, with matplotlib and numpy required only for visualization features.
