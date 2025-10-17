"""
Draw a US map of congressional districts using topojson data.

This script uses Altair with the albersUsa projection type, which properly
handles the positioning of Alaska, Hawaii, and Puerto Rico (similar to d3.geoAlbersUsa).

Based on g1d.py implementation.

Colors districts by various metrics from results JSON file.
"""

import altair as alt
import geopandas as gpd
import json
import argparse
import matplotlib.colors as mcolors
import pandas as pd
from typing import Optional, Dict, Any
import warnings
warnings.filterwarnings('ignore')


def load_results(results_path: str) -> Optional[Dict[str, Any]]:
    """
    Load election results from JSON file.
    
    Args:
        results_path: Path to the results JSON file
        
    Returns:
        Dictionary containing results data, or None if file cannot be loaded
    """
    try:
        with open(results_path, 'r') as f:
            data = json.load(f)
        print(f"Loaded results from '{results_path}'")
        print(f"  Total districts: {data.get('total_districts', 'unknown')}")
        print(f"  Democratic wins: {data.get('democratic_wins', 'unknown')}")
        print(f"  Republican wins: {data.get('republican_wins', 'unknown')}")
        return data
    except FileNotFoundError:
        print(f"Warning: Results file '{results_path}' not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Warning: Error parsing JSON from '{results_path}': {e}")
        return None
    except Exception as e:
        print(f"Warning: Error loading '{results_path}': {e}")
        return None


# Create color maps using LinearSegmentedColormap (same as ideology_histogram.py)
IDEOLOGY_COLORMAP = mcolors.LinearSegmentedColormap.from_list(
    'ideology', ['#0000ff', '#8000ff', '#ff0000']  # Blue -> Purple -> Red
)

REPRESENTATION_COLORMAP = mcolors.LinearSegmentedColormap.from_list(
    'representation', ['#000000', '#000000', '#A52A2A', '#FFA500', '#ffff00', '#008000']  # Black -> Brown -> Orange -> Yellow -> Green
)


def get_representation_color(satisfaction: float) -> str:
    """
    Get color for voter satisfaction (representation).
    
    Scale: 0.0 = black, 1.0 = green (with gradient through brown, orange, yellow)
    Uses LinearSegmentedColormap for smooth color interpolation.
    
    Args:
        satisfaction: Voter satisfaction value (0.0 to 1.0)
        
    Returns:
        Hex color string
    """
    # Clamp to valid range
    satisfaction = max(0.0, min(1.0, satisfaction))
    
    # Get RGB color from colormap
    rgb = REPRESENTATION_COLORMAP(satisfaction)
    
    # Convert to hex color
    return mcolors.rgb2hex(rgb)


def get_ideology_color(ideology: float, gradient_min: float = -1.5, gradient_max: float = 1.5) -> str:
    """
    Get color for winner ideology.
    
    Scale: -1.5 = blue, 0 = purple, 1.5 = red
    Uses LinearSegmentedColormap for smooth color interpolation (same as ideology_histogram.py).
    
    Args:
        ideology: Winner ideology value (-1.5 to 1.5, typically)
        gradient_min: Minimum value for blue in gradient (default: -1.5)
        gradient_max: Maximum value for red in gradient (default: 1.5)
        
    Returns:
        Hex color string
    """
    # Normalize value to [0, 1] range based on gradient_min and gradient_max
    normalized = (ideology - gradient_min) / (gradient_max - gradient_min)
    normalized = max(0.0, min(1.0, normalized))  # Clamp to [0, 1]
    
    # Get RGB color from colormap
    rgb = IDEOLOGY_COLORMAP(normalized)
    
    # Convert to hex color
    return mcolors.rgb2hex(rgb)


def create_gradient_scale(height: int = 400) -> alt.Chart:
    """
    Create a vertical gradient scale for the representation colormap.
    
    The scale shows values from 20 to 100, with labels at 20, 40, 60, 80, and 100.
    Colors correspond to the representation colormap (satisfaction values 0.2 to 1.0).
    
    Args:
        height: Height of the gradient scale in pixels
        
    Returns:
        Altair chart object containing the gradient scale
    """
    # Create data points for the gradient (from 20 to 100)
    gradient_data = pd.DataFrame({
        'y': range(20, 101),
        'y2': range(21, 102),  # Next value for rectangle height
        'x': [0] * 81,
        'x2': [1] * 81
    })
    
    # Add colors based on the representation colormap
    # Map 20-100 to 0.2-1.0 in the satisfaction scale
    gradient_data['color'] = gradient_data['y'].apply(
        lambda v: get_representation_color((v - 20) / 80 * 0.8 + 0.2)
    )
    
    # Create the gradient bar using mark_rect with y and y2
    gradient_bar = alt.Chart(gradient_data).mark_rect().encode(
        y=alt.Y('y:Q', 
                axis=None,
                scale=alt.Scale(domain=[20, 100])),
        y2='y2:Q',
        x=alt.X('x:Q', axis=None, scale=alt.Scale(domain=[-0.5, 1.5])),
        x2='x2:Q',
        color=alt.Color('color:N', scale=None, legend=None)
    ).properties(
        width=30,
        height=height
    )
    
    # Create labels at 20, 40, 60, 80, 100
    label_data = pd.DataFrame({
        'value': [20, 40, 60, 80, 100],
        'label': ['20', '40', '60', '80', '100'],
        'x': [1.2] * 5
    })
    
    # Create text labels
    labels = alt.Chart(label_data).mark_text(
        align='left',
        fontSize=12
    ).encode(
        y=alt.Y('value:Q', 
                axis=None,
                scale=alt.Scale(domain=[20, 100])),
        x=alt.X('x:Q', axis=None, scale=alt.Scale(domain=[-0.5, 1.5])),
        text='label:N'
    ).properties(
        width=30,
        height=height
    )
    
    # Combine bar and labels
    scale_chart = (gradient_bar + labels).properties(
        title=alt.TitleParams(
            text='Representation %',
            anchor='middle',
            fontSize=13,
            offset=10
        )
    )
    
    return scale_chart


def draw_us_map(
    topojson_path: str = "districts.20250701.topo.json",
    output_path: str = "us_districts_map.png",
    results_path: Optional[str] = None,
    colorization: str = "none",
    title: str = "US Congressional Districts (119th Congress)",
    width: int = 950,
    height: int = 550
):
    """
    Draw a map of US congressional districts using AlbersUSA projection.
    
    This uses Altair's built-in 'albersUsa' projection type, which is equivalent
    to d3.geoAlbersUsa() and properly positions Alaska, Hawaii, and Puerto Rico
    in the lower-left corner of the map.
    
    Args:
        topojson_path: Path to the topojson file
        output_path: Path to save the output PNG
        results_path: Optional path to results JSON file for coloring districts
        colorization: Color scheme to use ('none', 'representation', 'winner_ideology')
        title: Title for the map
        width: Width of the output map in pixels
        height: Height of the output map in pixels
    """
    # Load results data if provided
    results_data = None
    if results_path:
        results_data = load_results(results_path)
    
    print(f"Loading topojson data from '{topojson_path}'...")
    
    try:
        # Read the topojson file directly with geopandas
        # The 'layer' parameter specifies which object from the topojson to read
        districts_gdf = gpd.read_file(topojson_path, layer="districts")
    except Exception as e:
        print(f"Error reading file with GeoPandas: {e}")
        return
    
    print(f"Loaded {len(districts_gdf)} districts")
    
    # Find the GEOID column (matching MapController.ts behavior)
    geoid_col_name = None
    possible_names = ['GEOID', 'geoid', 'GeoID']
    for name in possible_names:
        if name in districts_gdf.columns:
            geoid_col_name = name
            break
    
    if not geoid_col_name:
        print("Warning: Could not find a GEOID column in the data.")
        print(f"Available columns are: {districts_gdf.columns.tolist()}")
    else:
        print(f"Using GEOID column: '{geoid_col_name}'")
    
    # Set default color for all districts (lightgray with white borders)
    districts_gdf['color'] = 'lightgray'
    
    # ========================================================================
    # Color districts based on results data if available
    # ========================================================================
    if results_data and 'district_results' in results_data and colorization != 'none':
        print(f"Processing results data for colorization: {colorization}")
        
        # Create a mapping from district to result data
        # Results JSON uses format like "AL-03", topojson OFFICE_ID uses "AL03"
        # We'll create mappings for both formats
        district_map = {}
        for result in results_data['district_results']:
            district_id = result.get('district')
            if district_id:
                # Store with original format (e.g., "AL-03")
                district_map[district_id] = result
                # Also store without hyphen (e.g., "AL03")
                district_map[district_id.replace('-', '')] = result
                # if the district_id is XX-01, store that also as XX00
                if district_id[-2:] == '01':
                    district_map[district_id[0:2] + '00'] = result
        
        print(f"  Found results for {len(results_data['district_results'])} districts")
        
        # Apply colorization based on scheme
        colored_count = 0
        for idx, row in districts_gdf.iterrows():
            office_id = row.get('OFFICE_ID')
            if office_id and office_id in district_map:
                result = district_map[office_id]
                
                if colorization == 'representation':
                    # Color by voter satisfaction
                    satisfaction = result.get('voter_satisfaction')
                    if satisfaction is not None:
                        districts_gdf.at[idx, 'color'] = get_representation_color(satisfaction)
                        colored_count += 1
                
                elif colorization == 'winner_ideology':
                    # Color by winner ideology
                    ideology = result.get('winner_ideology')
                    if ideology is not None:
                        districts_gdf.at[idx, 'color'] = get_ideology_color(ideology)
                        colored_count += 1
        
        print(f"  Colored {colored_count} districts using '{colorization}' scheme")
    # ========================================================================
    
    print("Creating Altair chart...")
    
    # Create the base geographic chart
    districts_layer = alt.Chart(districts_gdf).mark_geoshape(
        stroke='white',
        strokeWidth=0.5
    ).encode(
        color=alt.Color('color:N', scale=None)  # Use colors as-is, no scale transformation
    ).properties(
        title=title
    )
    
    # Apply the albersUsa projection (this is the key!)
    # This projection automatically positions Alaska, Hawaii, and Puerto Rico
    # in the lower-left corner, just like d3.geoAlbersUsa()
    map_chart = districts_layer.project(
        type='albersUsa'
    ).properties(
        width=width,
        height=height
    )
    
    # Add gradient scale on the left if using representation colorization
    if colorization == 'representation':
        gradient_scale = create_gradient_scale(height=height)
        final_map = alt.hconcat(gradient_scale, map_chart, spacing=20).configure_view(
            strokeWidth=0  # Remove border around the chart
        )
    else:
        final_map = map_chart.configure_view(
            strokeWidth=0  # Remove border around the chart
        )
    
    print(f"Saving map to '{output_path}'...")
    final_map.save(output_path)
    print("Map saved successfully!")


def main():
    """Main entry point for the script."""
    import os
    
    parser = argparse.ArgumentParser(
        description='Draw a US map of congressional districts with optional coloring from results data.'
    )
    parser.add_argument(
        '--results',
        type=str,
        default='results-actual.json',
        help='Path to results JSON file (default: results-actual.json)'
    )
    parser.add_argument(
        '--topojson',
        type=str,
        default='districts.20250701.topo.json',
        help='Path to topojson file (default: districts.20250701.topo.json)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='us_districts_map.png',
        help='Path to output PNG file (default: us_districts_map.png)'
    )
    parser.add_argument(
        '--title',
        type=str,
        default='US Congressional Districts (119th Congress)',
        help='Title for the map'
    )
    parser.add_argument(
        '--width',
        type=int,
        default=950,
        help='Width of output map in pixels (default: 950)'
    )
    parser.add_argument(
        '--height',
        type=int,
        default=550,
        help='Height of output map in pixels (default: 550)'
    )
    parser.add_argument(
        '--colorization',
        type=str,
        default='none',
        choices=['none', 'representation', 'winner_ideology'],
        help='Colorization scheme: none (gray), representation (satisfaction gradient), or winner_ideology (ideology gradient)'
    )
    
    args = parser.parse_args()
    
    # Check if topojson file exists
    if not os.path.exists(args.topojson):
        print(f"Error: Could not find topojson file '{args.topojson}'")
        print("Please make sure the file exists.")
        return
    
    # Results file is optional - if it doesn't exist, just print a warning
    results_path = None
    if os.path.exists(args.results):
        results_path = args.results
    else:
        print(f"Note: Results file '{args.results}' not found - drawing map without coloring")
    
    # Draw the map
    draw_us_map(
        topojson_path=args.topojson,
        output_path=args.output,
        results_path=results_path,
        colorization=args.colorization,
        title=args.title,
        width=args.width,
        height=args.height
    )


if __name__ == '__main__':
    main()
