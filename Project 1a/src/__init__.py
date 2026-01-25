"""
Monte Carlo Heat Diffusion Simulation Package
=============================================

A modular framework for simulating heat diffusion in computer heat sinks
using Monte Carlo random-walk methods.
"""

__version__ = "1.0.0"
__author__ = "Heat Sink Simulation Team"

from .config import SimulationConfig
from .model import HeatPacket, HeatSink
from .simulate import MonteCarloSimulator
from .observables import ObservableCollector
from .experiments import ExperimentRunner

__all__ = [
    'SimulationConfig',
    'HeatPacket', 
    'HeatSink',
    'MonteCarloSimulator',
    'ObservableCollector',
    'ExperimentRunner'
]