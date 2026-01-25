#!/usr/bin/env python3
"""
Create a table of convection parameters used in the Monte Carlo simulation.
"""

import sys
sys.path.append('src')

import matplotlib.pyplot as plt
import numpy as np
from config import SimulationConfig

def create_convection_parameters_table():
    """Create a professional table of convection parameters."""
    
    # Ensure output directories exist in the parent directory (Project 1a root)
    import os
    reporting_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reporting")
    figures_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs", "figures")
    os.makedirs(reporting_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)
    
    # Set up the figure
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('tight')
    ax.axis('off')
    
    # Table title
    title = ("Table 3: Convection parameters used in the Monte Carlo simulations. The convection\n"
             "probability represents the likelihood of heat packet removal via air cooling per time step.\n"
             "Calibrated against industrial heat sink performance data to achieve realistic temperatures.")
    
    # Convection parameter data
    convection_data = [
        ["Parameter", "Value", "Units", "Description"],
        ["Convection probability (P_conv)", "0.004", "per time step", "Packet removal probability"],
        ["Time step (Δt)", "0.002", "s", "Simulation time increment"],
        ["Simulation time", "2.0", "s", "Total simulation duration"],
        ["Grid spacing (Δx)", "0.002", "m", "Spatial discretization"],
        ["Heat sink size", "25×25", "mm", "Physical dimensions"],
        ["Ambient temperature", "21", "°C", "Reference temperature"],
        ["Target cooling regime", "Medium forced air", "—", "2-4 m/s airflow"],
        ["Calibration target", "45-60", "°C", "Copper heat sink under load"]
    ]
    
    # Create table
    table = ax.table(cellText=convection_data[1:], 
                    colLabels=convection_data[0],
                    cellLoc='left',
                    loc='center',
                    colWidths=[0.35, 0.15, 0.15, 0.35])
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.0)
    
    # Header styling
    for i in range(len(convection_data[0])):
        table[(0, i)].set_facecolor('#E6E6E6')
        table[(0, i)].set_text_props(weight='bold')
    
    # Alternate row colors
    for i in range(1, len(convection_data)):
        if i % 2 == 0:
            for j in range(len(convection_data[0])):
                table[(i, j)].set_facecolor('#F8F8F8')
    
    # Add title
    plt.figtext(0.5, 0.85, title, ha='center', va='top', fontsize=12, wrap=True)
    
    # Save the table
    plt.tight_layout()
    plt.subplots_adjust(top=0.75)
    plt.savefig(os.path.join(reporting_dir, 'convection_parameters_table.pdf'), 
                bbox_inches='tight', dpi=300, facecolor='white')
    plt.savefig(os.path.join(figures_dir, 'convection_parameters_table.png'), 
                bbox_inches='tight', dpi=300, facecolor='white')
    
    print("✅ Convection parameters table saved:")
    print(f"   - {reporting_dir}/convection_parameters_table.pdf")
    print(f"   - {figures_dir}/convection_parameters_table.png")
    
    plt.close()

def create_validation_results_table():
    """Create a table showing validation results for different materials."""
    
    # Set up the figure
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('tight')
    ax.axis('off')
    
    # Table title
    title = ("Table 4: Convection model validation results. Simulation temperatures compared\n"
             "with industrial heat sink performance targets for typical operating conditions.")
    
    # Validation data (from our calibration results)
    validation_data = [
        ["Material", "Simulation Temp (°C)", "Absolute Temp (°C)", "Industrial Target (°C)", "Status"],
        ["Silver", "30.0", "51.0", "40-55", "✓ Realistic"],
        ["Copper", "29.0", "50.0", "45-60", "✓ Realistic"],
        ["Steel (carbon)", "91.7", "112.7", "70-120", "✓ Realistic"],
        ["", "", "", "", ""],
        ["Convection effectiveness", "", "", "", ""],
        ["Silver", "38.7%", "—", "85-95%", "Lower (high diffusivity)"],
        ["Copper", "50.1%", "—", "85-95%", "Moderate"],
        ["Steel (carbon)", "92.9%", "—", "85-95%", "✓ Literature match"]
    ]
    
    # Create table
    table = ax.table(cellText=validation_data[1:], 
                    colLabels=validation_data[0],
                    cellLoc='center',
                    loc='center',
                    colWidths=[0.2, 0.2, 0.2, 0.2, 0.2])
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.8)
    
    # Header styling
    for i in range(len(validation_data[0])):
        table[(0, i)].set_facecolor('#E6E6E6')
        table[(0, i)].set_text_props(weight='bold')
    
    # Section separator
    for j in range(len(validation_data[0])):
        table[(4, j)].set_facecolor('#D0D0D0')
        table[(5, j)].set_text_props(weight='bold')
    
    # Alternate row colors
    for i in range(1, len(validation_data)):
        if i not in [4, 5] and i % 2 == 0:
            for j in range(len(validation_data[0])):
                table[(i, j)].set_facecolor('#F8F8F8')
    
    # Add title
    plt.figtext(0.5, 0.85, title, ha='center', va='top', fontsize=12, wrap=True)
    
    # Save the table
    plt.tight_layout()
    plt.subplots_adjust(top=0.75)
    plt.savefig(os.path.join(reporting_dir, 'convection_validation_table.pdf'), 
                bbox_inches='tight', dpi=300, facecolor='white')
    plt.savefig(os.path.join(figures_dir, 'convection_validation_table.png'), 
                bbox_inches='tight', dpi=300, facecolor='white')
    
    print("✅ Convection validation table saved:")
    print(f"   - {reporting_dir}/convection_validation_table.pdf")
    print(f"   - {figures_dir}/convection_validation_table.png")
    
    plt.close()

def create_literature_comparison_table():
    """Create a table comparing with literature heat transfer percentages."""
    
    # Set up the figure
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.axis('tight')
    ax.axis('off')
    
    # Table title
    title = ("Table 5: Literature comparison of heat transfer mechanisms in heat sinks.\n"
             "Sources: Culham & Muzychka (2001), Teertstra et al. (2000), Kraus & Bar-Cohen (1995).")
    
    # Literature comparison data
    literature_data = [
        ["Cooling Method", "Convection %", "Other %", "Application", "Reference"],
        ["Natural convection", "85", "15", "Passive cooling", "Kraus & Bar-Cohen (1995)"],
        ["Forced convection (low)", "92", "8", "Desktop PC fans", "Teertstra et al. (2000)"],
        ["Forced convection (medium)", "95", "5", "Server cooling", "Culham & Muzychka (2001)"],
        ["Forced convection (high)", "97", "3", "Industrial cooling", "Electronics Cooling Mag."],
        ["", "", "", "", ""],
        ["Monte Carlo Results", "", "", "", ""],
        ["Silver (high α)", "38.7", "61.3", "Fast heat spreading", "This work"],
        ["Copper (medium α)", "50.1", "49.9", "Balanced behavior", "This work"],
        ["Steel carbon (low α)", "92.9", "7.1", "Residence time effect", "This work"]
    ]
    
    # Create table
    table = ax.table(cellText=literature_data[1:], 
                    colLabels=literature_data[0],
                    cellLoc='center',
                    loc='center',
                    colWidths=[0.25, 0.15, 0.15, 0.25, 0.2])
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.8)
    
    # Header styling
    for i in range(len(literature_data[0])):
        table[(0, i)].set_facecolor('#E6E6E6')
        table[(0, i)].set_text_props(weight='bold')
    
    # Section separator
    for j in range(len(literature_data[0])):
        table[(5, j)].set_facecolor('#D0D0D0')
        table[(6, j)].set_text_props(weight='bold')
    
    # Alternate row colors
    for i in range(1, len(literature_data)):
        if i not in [5, 6] and i % 2 == 0:
            for j in range(len(literature_data[0])):
                table[(i, j)].set_facecolor('#F8F8F8')
    
    # Add title
    plt.figtext(0.5, 0.88, title, ha='center', va='top', fontsize=12, wrap=True)
    
    # Save the table
    plt.tight_layout()
    plt.subplots_adjust(top=0.78)
    plt.savefig(os.path.join(reporting_dir, 'literature_comparison_table.pdf'), 
                bbox_inches='tight', dpi=300, facecolor='white')
    plt.savefig(os.path.join(figures_dir, 'literature_comparison_table.png'), 
                bbox_inches='tight', dpi=300, facecolor='white')
    
    print("✅ Literature comparison table saved:")
    print(f"   - {reporting_dir}/literature_comparison_table.pdf")
    print(f"   - {figures_dir}/literature_comparison_table.png")
    
    plt.close()

if __name__ == "__main__":
    print("Creating Convection Parameter Tables")
    print("=" * 40)
    
    # Create all tables
    create_convection_parameters_table()
    create_validation_results_table()
    create_literature_comparison_table()
    
    print("\n" + "=" * 40)
    print("All convection tables created successfully!")
    print("Files saved in reporting/ folder")