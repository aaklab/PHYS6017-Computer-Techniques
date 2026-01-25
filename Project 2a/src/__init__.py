"""
Vibration Signal Analysis Package

This package contains modules for detecting mechanical wear in rotating machinery
using computational signal processing techniques.

Modules:
- signal_generator: Generate synthetic vibration signals with wear characteristics
- vibration_analysis: Analyze signals using FFT, filtering, and quantitative indicators
"""

from .signal_generator import VibrationSignalGenerator
from .vibration_analysis import VibrationAnalyzer

__version__ = "1.0.0"
__author__ = "PHYS6017 Assignment"

__all__ = ['VibrationSignalGenerator', 'VibrationAnalyzer']