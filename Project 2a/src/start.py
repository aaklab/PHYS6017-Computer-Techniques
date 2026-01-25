#!/usr/bin/env python3
"""
Main entry point for running the vibration signal analysis.
Run this file from the src/ directory.
"""

# Import and run the main report generator
from create_complete_report import create_complete_report

if __name__ == "__main__":
    print("="*60)
    print("VIBRATION SIGNAL ANALYSIS")
    print("="*60)
    print("Output will be saved to: ../complete_vibration_analysis_report.pdf")
    print("="*60)
    print()
    
    create_complete_report()
