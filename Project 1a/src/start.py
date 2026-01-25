#!/usr/bin/env python3
"""
Main entry point for running the Monte Carlo heat diffusion simulation.
Run this file from the src/ directory.
"""

# Import and run the main simulation
from generate_required_results import generate_required_results

if __name__ == "__main__":
    print("="*60)
    print("MONTE CARLO HEAT DIFFUSION SIMULATION")
    print("="*60)
    print("Output will be saved to: ../reporting/required_results.pdf")
    print("="*60)
    print()
    
    generate_required_results()
