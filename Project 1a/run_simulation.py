#!/usr/bin/env python3
"""
Main entry point for running the Monte Carlo heat diffusion simulation.
All source code is in the src/ directory.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main simulation
from generate_required_results import generate_required_results

if __name__ == "__main__":
    print("="*60)
    print("MONTE CARLO HEAT DIFFUSION SIMULATION")
    print("="*60)
    print("All source code is in: src/")
    print("Output will be saved to: reporting/required_results.pdf")
    print("="*60)
    print()
    
    generate_required_results()
