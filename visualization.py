"""
Visualization utilities for congressional election simulation results.
"""
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Optional
from congressional_simulation import CongressionalSimulationResult, DistrictResult


def plot_winner_ideology_histogram(result: CongressionalSimulationResult, 
                                 save_path: Optional[str] = None,
                                 show_plot: bool = True) -> None:
    """Plot histogram of winning candidate ideologies."""
    
    # Separate ideologies by party
    dem_ideologies = [dr.winner_ideology for dr in result.district_results if dr.winner_party == "Dem"]
    rep_ideologies = [dr.winner_ideology for dr in result.district_results if dr.winner_party == "Rep"]
    other_ideologies = [dr.winner_ideology for dr in result.district_results if dr.winner_party not in ["Dem", "Rep"]]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot histograms
    if dem_ideologies:
        ax.hist(dem_ideologies, bins=30, alpha=0.7, label=f'Democrats ({len(dem_ideologies)})', 
                color='blue', density=True)
    
    if rep_ideologies:
        ax.hist(rep_ideologies, bins=30, alpha=0.7, label=f'Republicans ({len(rep_ideologies)})', 
                color='red', density=True)
    
    if other_ideologies:
        ax.hist(other_ideologies, bins=30, alpha=0.7, label=f'Other ({len(other_ideologies)})', 
                color='green', density=True)
    
    # Customize plot
    ax.set_xlabel('Winner Ideology', fontsize=12)
    ax.set_ylabel('Density', fontsize=12)
    ax.set_title('Distribution of Winning Candidate Ideologies', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Add vertical line at 0 (center)
    ax.axvline(x=0, color='black', linestyle='--', alpha=0.5, label='Center (0)')
    
    # Add statistics text
    all_ideologies = dem_ideologies + rep_ideologies + other_ideologies
    if all_ideologies:
        mean_ideology = np.mean(all_ideologies)
        std_ideology = np.std(all_ideologies)
        ax.text(0.02, 0.98, f'Mean: {mean_ideology:.2f}\nStd: {std_ideology:.2f}', 
                transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Histogram saved to {save_path}")
    
    if show_plot:
        plt.show()
    else:
        plt.close()


def plot_voter_satisfaction_histogram(result: CongressionalSimulationResult,
                                    save_path: Optional[str] = None,
                                    show_plot: bool = True) -> None:
    """Plot histogram of voter satisfaction by party."""
    
    # Separate satisfaction by party
    dem_satisfaction = [dr.voter_satisfaction for dr in result.district_results if dr.winner_party == "Dem"]
    rep_satisfaction = [dr.voter_satisfaction for dr in result.district_results if dr.winner_party == "Rep"]
    other_satisfaction = [dr.voter_satisfaction for dr in result.district_results if dr.winner_party not in ["Dem", "Rep"]]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot histograms
    if dem_satisfaction:
        ax.hist(dem_satisfaction, bins=20, alpha=0.7, label=f'Democratic Districts ({len(dem_satisfaction)})', 
                color='blue', density=True)
    
    if rep_satisfaction:
        ax.hist(rep_satisfaction, bins=20, alpha=0.7, label=f'Republican Districts ({len(rep_satisfaction)})', 
                color='red', density=True)
    
    if other_satisfaction:
        ax.hist(other_satisfaction, bins=20, alpha=0.7, label=f'Other Districts ({len(other_satisfaction)})', 
                color='green', density=True)
    
    # Customize plot
    ax.set_xlabel('Voter Satisfaction', fontsize=12)
    ax.set_ylabel('Density', fontsize=12)
    ax.set_title('Distribution of Voter Satisfaction by Winning Party', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Add statistics text
    all_satisfaction = dem_satisfaction + rep_satisfaction + other_satisfaction
    if all_satisfaction:
        mean_satisfaction = np.mean(all_satisfaction)
        std_satisfaction = np.std(all_satisfaction)
        ax.text(0.02, 0.98, f'Mean: {mean_satisfaction:.3f}\nStd: {std_satisfaction:.3f}', 
                transform=ax.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Satisfaction histogram saved to {save_path}")
    
    if show_plot:
        plt.show()
    else:
        plt.close()


def plot_ideology_vs_satisfaction_scatter(result: CongressionalSimulationResult,
                                        save_path: Optional[str] = None,
                                        show_plot: bool = True) -> None:
    """Plot scatter plot of winner ideology vs voter satisfaction."""
    
    # Separate data by party
    dem_data = [(dr.winner_ideology, dr.voter_satisfaction) for dr in result.district_results if dr.winner_party == "Dem"]
    rep_data = [(dr.winner_ideology, dr.voter_satisfaction) for dr in result.district_results if dr.winner_party == "Rep"]
    other_data = [(dr.winner_ideology, dr.voter_satisfaction) for dr in result.district_results if dr.winner_party not in ["Dem", "Rep"]]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot scatter points
    if dem_data:
        dem_x, dem_y = zip(*dem_data)
        ax.scatter(dem_x, dem_y, alpha=0.6, label=f'Democrats ({len(dem_data)})', 
                  color='blue', s=30)
    
    if rep_data:
        rep_x, rep_y = zip(*rep_data)
        ax.scatter(rep_x, rep_y, alpha=0.6, label=f'Republicans ({len(rep_data)})', 
                  color='red', s=30)
    
    if other_data:
        other_x, other_y = zip(*other_data)
        ax.scatter(other_x, other_y, alpha=0.6, label=f'Other ({len(other_data)})', 
                  color='green', s=30)
    
    # Customize plot
    ax.set_xlabel('Winner Ideology', fontsize=12)
    ax.set_ylabel('Voter Satisfaction', fontsize=12)
    ax.set_title('Winner Ideology vs Voter Satisfaction', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Add vertical line at 0 (center)
    ax.axvline(x=0, color='black', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Scatter plot saved to {save_path}")
    
    if show_plot:
        plt.show()
    else:
        plt.close()


def plot_party_win_map(result: CongressionalSimulationResult,
                      save_path: Optional[str] = None,
                      show_plot: bool = True) -> None:
    """Plot a simple bar chart of party wins by state."""
    
    # Count wins by state and party
    state_wins = {}
    for dr in result.district_results:
        state = dr.state
        if state not in state_wins:
            state_wins[state] = {'Dem': 0, 'Rep': 0, 'Other': 0}
        state_wins[state][dr.winner_party] += 1
    
    # Sort states by total districts
    states = sorted(state_wins.keys(), key=lambda s: sum(state_wins[s].values()), reverse=True)
    
    # Prepare data for plotting
    dem_wins = [state_wins[state]['Dem'] for state in states]
    rep_wins = [state_wins[state]['Rep'] for state in states]
    other_wins = [state_wins[state]['Other'] for state in states]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(16, 10))
    
    x = np.arange(len(states))
    width = 0.6
    
    # Plot bars
    ax.bar(x, dem_wins, width, label='Democrats', color='blue', alpha=0.8)
    ax.bar(x, rep_wins, width, bottom=dem_wins, label='Republicans', color='red', alpha=0.8)
    if any(other_wins):
        ax.bar(x, other_wins, width, bottom=[d+r for d, r in zip(dem_wins, rep_wins)], 
               label='Other', color='green', alpha=0.8)
    
    # Customize plot
    ax.set_xlabel('State', fontsize=12)
    ax.set_ylabel('Number of Districts Won', fontsize=12)
    ax.set_title('Party Wins by State', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(states, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Party win map saved to {save_path}")
    
    if show_plot:
        plt.show()
    else:
        plt.close()


def create_all_visualizations(result: CongressionalSimulationResult,
                            output_dir: str = "plots",
                            show_plots: bool = False) -> None:
    """Create all visualizations and save them to files."""
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print("Creating visualizations...")
    
    # Create all plots
    plot_winner_ideology_histogram(result, 
                                  save_path=os.path.join(output_dir, "winner_ideology_histogram.png"),
                                  show_plot=show_plots)
    
    plot_voter_satisfaction_histogram(result,
                                    save_path=os.path.join(output_dir, "voter_satisfaction_histogram.png"),
                                    show_plot=show_plots)
    
    plot_ideology_vs_satisfaction_scatter(result,
                                        save_path=os.path.join(output_dir, "ideology_vs_satisfaction.png"),
                                        show_plot=show_plots)
    
    plot_party_win_map(result,
                      save_path=os.path.join(output_dir, "party_wins_by_state.png"),
                      show_plot=show_plots)
    
    print(f"All visualizations saved to {output_dir}/")
