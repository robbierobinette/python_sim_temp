#!/usr/bin/env python3
"""
Generate ideology histogram from results-actual.json file.

This script creates a histogram visualization where each winner is represented
as a circle, and the circles are stacked to form a histogram. The visualization
is based on the TypeScript/D3 code in tscode/HistogramLayout.ts but simplified
for static output using matplotlib.

Usage:
    python ideology_histogram.py

Output:
    ideology_histogram.png - Histogram showing ideology distribution of winners
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
from typing import List, Tuple
from dataclasses import dataclass
import argparse
import sys


@dataclass
class DataPoint:
    """Represents a data point with value and optional metadata."""
    value: float
    label: str = ""
    color: str = "#1f77b4"


class IdeologyHistogram:
    """Creates histogram visualization of winner ideologies."""
    
    def __init__(self, 
                 width: int = 1000,
                 height: int = 600,
                 radius: float = 12.0,
                 domain_min: float = None,
                 domain_max: float = None,
                 gradient_min: float = -1.5,
                 gradient_max: float = 1.5,
                 title: str = "Histogram"):
        """
        Initialize the histogram parameters.
        
        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels  
            radius: Radius of circles representing winners
            domain_min: Minimum value (if None, will be calculated from data)
            domain_max: Maximum value (if None, will be calculated from data)
            gradient_min: Minimum value for blue in gradient (default: -1.5)
            gradient_max: Maximum value for red in gradient (default: 1.5)
            title: Title for the histogram (default: "Histogram")
        """
        self.width = width
        self.height = height
        self.radius = radius
        self.domain_min = domain_min
        self.domain_max = domain_max
        self.range = self.domain_max - self.domain_min
        self.gradient_min = gradient_min
        self.gradient_max = gradient_max
        self.title = title
        
        # Calculate layout parameters similar to TypeScript code
        self.diameter = 2 * self.radius
        self.spacing = self.diameter - 2
        self.n_buckets = int(self.width / self.spacing)
        
        # Y position where histogram bars start (from bottom)
        self.y_floor = self.height - 50  # Leave space for axis labels
        
        # Create color map for ideology gradient (blue to purple to red)
        self.color_map = mcolors.LinearSegmentedColormap.from_list(
            'ideology', ['#0000ff', '#8000ff', '#ff0000']
        )
    
    def value_to_color(self, value: float) -> str:
        """Convert an ideology value to a color using the gradient."""
        # Normalize value to [0, 1] range based on gradient_min and gradient_max
        normalized = (value - self.gradient_min) / (self.gradient_max - self.gradient_min)
        normalized = max(0.0, min(1.0, normalized))  # Clamp to [0, 1]
        
        # Get RGB color from colormap
        rgb = self.color_map(normalized)
        
        # Convert to hex color
        return mcolors.rgb2hex(rgb)
    
    def create_data_points(self, values: List[float], labels: List[str] = None, colors: List[str] = None) -> List[DataPoint]:
        """Create DataPoint objects from a list of values."""
        if labels is None:
            labels = [""] * len(values)
        
        data_points = []
        for i, value in enumerate(values):
            # Use gradient color based on value if no colors provided
            if colors is None:
                color = self.value_to_color(value)
            else:
                color = colors[i] if i < len(colors) else self.value_to_color(value)
            
            data_point = DataPoint(
                value=value,
                label=labels[i] if i < len(labels) else "",
                color=color
            )
            data_points.append(data_point)
        
        return data_points
    
    def bucket_index(self, value: float) -> int:
        return int((value - self.domain_min) / self.range * self.n_buckets)
        
    def calculate_circle_positions(self, data_points: List[DataPoint]) -> Tuple[List[Tuple[float, float, DataPoint]], List[int]]:
        """
        Calculate x,y positions for all circles in the histogram.
        
        Returns:
            Tuple of (circle_positions, bucket_counts)
        """
        # Group data points by bucket
        bucket_data_points = [[] for _ in range(self.n_buckets)]
        
        for data_point in data_points:
            index = self.bucket_index(data_point.value)
            if 0 <= index < self.n_buckets:
                bucket_data_points[index].append(data_point)
        
        # Calculate bucket counts
        bucket_counts = [len(bucket) for bucket in bucket_data_points]
        
        circle_positions = []
        
        # Process each bucket separately
        for bucket_index in range(self.n_buckets):
            if not bucket_data_points[bucket_index]:
                continue
                
            # Calculate bucket center - all circles in this bucket will be centered
            x = bucket_index * self.spacing + self.spacing / 2
            
            # Position circles within this bucket - all centered at bucket_center
            for i, data_point in enumerate(bucket_data_points[bucket_index]):
                # Calculate y position (stack circles from bottom up)
                y = 25 + (i * self.spacing + self.radius)
                
                circle_positions.append((x, y, data_point))
        
        return circle_positions, bucket_counts
    
    def create_histogram(self, data_points: List[DataPoint], x_labels: List[str] = None, x_label_values: List[float] = None, output_filename: str = None, display: bool = False, xlabel: str = 'Values'):
        """Create and save the histogram visualization."""
        # Calculate circle positions
        circle_positions, bucket_counts = self.calculate_circle_positions(data_points)
        
        # Set y-axis height based on actual data with padding for title and labels
        max_bucket_height = max(bucket_counts) * self.spacing
        padding = 100  # Space for title and labels
        max_height = max_bucket_height + padding
        
        # Create figure with fixed aspect ratio to prevent circle distortion
        # Use a minimum height to ensure circles don't get too distorted
        min_height = 400  # Minimum figure height in pixels
        actual_height = max(max_height, min_height)
        
        fig, ax = plt.subplots(figsize=(self.width/100, actual_height/100), dpi=100)
        ax.set_xlim(0, self.width)
        ax.set_ylim(0, max_height)
        
        # Set equal aspect ratio to prevent circle distortion
        ax.set_aspect('equal', adjustable='box')
        
        # Draw circles for each data point
        for x, y, data_point in circle_positions:
            circle = patches.Circle((x, y), self.radius, 
                                  facecolor=data_point.color, 
                                  edgecolor='white', 
                                  linewidth=0.5,
                                  alpha=0.8)
            ax.add_patch(circle)
        
        # Create x-axis labels - use provided labels or default empty labels
        if x_labels is None:
            x_labels = [''] * self.n_buckets
        
        # Map labels to their proper positions based on their values
        if x_label_values is not None:
            # Calculate positions based on actual values in the domain
            label_positions = []
            for val in x_label_values:
                # Convert value to x position: (value - domain_min) / range * width
                x_pos = (val - self.domain_min) / self.range * self.width
                label_positions.append(x_pos)
        else:
            # Fall back to evenly distributed labels
            label_positions = np.linspace(0, self.width, len(x_labels))
        
        ax.set_xticks(label_positions)
        ax.set_xticklabels(x_labels)
        ax.set_xlabel(xlabel, fontsize=12)
        
        # Remove y-axis tick labels but keep the axis
        ax.set_yticks([])
        ax.set_ylabel('Count', fontsize=12)
        ax.set_title(self.title, fontsize=14, fontweight='bold')
        
        # No legend needed for gradient coloring
        
        # Set proper y-axis limits (0 at bottom, growing upward)
        ax.set_ylim(0, max_height)
        
        # Remove top and right spines for cleaner look
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add grid for better readability
        ax.grid(True, alpha=0.3, axis='y')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save to file or display based on flags
        if output_filename:
            plt.savefig(output_filename, dpi=300, bbox_inches='tight')
        
        if display:
            plt.show()
        else:
            plt.close()  # Close the figure to free memory
        

def load_ideology_data(filename: str, use_nominate: bool = False) -> Tuple[List[float], List[str]]:
    """Load ideology data from JSON file and return values and labels.
    
    Args:
        filename: Path to JSON file with district results
        use_nominate: If True, use nominate_dim1 values; if False, use winner_ideology
    
    Returns:
        Tuple of (values, party_labels)
    """
    with open(filename, 'r') as f:
        data = json.load(f)
    
    values = []
    party = []
    
    for district_result in data['district_results']:
        if use_nominate:
            # Use nominate_dim1 if available, otherwise skip
            if 'nominate_dim1' in district_result:
                values.append(district_result['nominate_dim1'])
                party.append(district_result['winner_party'])
        else:
            values.append(district_result['winner_ideology'])
            party.append(district_result['winner_party'])
    
    return values, party


def main():
    """Main function to generate the ideology histogram."""
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Generate ideology histogram from JSON file')
    parser.add_argument('json_file', nargs='?', default='results-actual.json',
                       help='JSON file containing ideology data (default: results-actual.json)')
    parser.add_argument('-o', '--output', default=None,
                       help='Output filename for the histogram (if not specified, no file is saved)')
    parser.add_argument('--display', action='store_true',
                       help='Display the histogram on screen')
    parser.add_argument('--radius', type=float, default=12.0,
                       help='Radius of circles in pixels (default: 12.0)')
    parser.add_argument('--min', type=float, default=-2.5,
                       help='Minimum domain value (default: -2.5)')
    parser.add_argument('--max', type=float, default=2.5,
                       help='Maximum domain value (default: 2.5)')
    parser.add_argument('--title', type=str, default='Histogram',
                       help='Title for the histogram (default: "Histogram")')
    parser.add_argument('--xlabel', type=str, default='Member Partisanship',
                       help='Label for the x-axis (default: "Member Partisanship")')
    parser.add_argument('--labels', type=str, default="",
                       help='Labels for the histogram (default: is numeric lables if not specified)')
    parser.add_argument('--nominate', action='store_true',
                       help='Use nominate_dim1 values instead of winner_ideology (typically ranges from -1 to 1)')
    
    args = parser.parse_args()
    
    # Adjust defaults for nominate mode
    if args.nominate:
        # If min/max are at defaults, adjust them for nominate range
        if args.min == -2.5 and args.max == 2.5:
            args.min = -1.0
            args.max = 1.0
    
    gradient_min = -1.5
    gradient_max = 1.5
    if args.nominate:
        gradient_min = -0.5
        gradient_max = 0.5

    # Create histogram generator with custom domain and radius
    histogram = IdeologyHistogram(radius=args.radius, 
                    domain_min=args.min, 
                    domain_max=args.max, 
                    gradient_min=gradient_min,
                    gradient_max=gradient_max,
                    title=args.title)
    
    try:
        # Load data from JSON file
        values, party = load_ideology_data(args.json_file, use_nominate=args.nominate)
        
        # Check if we have any data
        if len(values) == 0:
            if args.nominate:
                print("Error: No nominate_dim1 values found in the JSON file.")
                print("The --nominate flag requires data with nominate_dim1 fields.")
                print("Try running without --nominate to use winner_ideology values instead.")
            else:
                print("Error: No winner_ideology values found in the JSON file.")
            sys.exit(1)
        
        # Create data points (colors will be generated from gradient)
        data_points = histogram.create_data_points(values, party)
        
        # Define ideology labels for x-axis
        if args.labels:
            ideology_labels = args.labels.split(",")
            ideology_values = None  # User-provided labels, evenly distribute them
        else:
            # Generate numeric labels based on mode
            if args.nominate:
                # For nominate mode, use -1 to 1 range
                ideology_labels = ['-1.0', '-0.5', '0.0', '0.5', '1.0']
                ideology_values = [-1.0, -0.5, 0.0, 0.5, 1.0]
            else:
                # For winner_ideology mode, use -2 to 2 range
                ideology_labels = ['-2', '-1', '0', '1', '2']
                ideology_values = [-2.0, -1.0, 0.0, 1.0, 2.0]

        # Generate histogram
        histogram.create_histogram(data_points, ideology_labels, ideology_values, args.output, args.display, args.xlabel)
        
    except FileNotFoundError:
        print(f"Error: {args.json_file} not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error generating histogram: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
