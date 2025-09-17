# Congressional Election Simulation

This Python implementation simulates elections for all 435 congressional districts using ranked choice voting (instant runoff). It's based on the Scala code in the `rcvcore` directory and uses data from the Cook Political Report.

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

# Run with 5 candidates per party
python main.py --candidates 5

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

- **Core simulation**: No external dependencies required - uses only Python standard library
- **Visualizations**: Requires matplotlib and numpy for plotting functionality
  ```bash
  pip install matplotlib numpy
  ```

## Implementation Notes

This Python implementation closely follows the structure and logic of the original Scala code in `rcvcore/`, adapting the object-oriented design to Python idioms while maintaining the same simulation algorithms and parameters.
