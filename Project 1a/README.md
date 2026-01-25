# Monte Carlo Heat Diffusion Simulation

A Monte Carlo simulation for modeling heat diffusion in computer heat sinks using random-walk heat packets.

## 🔧 Recent Fixes Applied

This implementation addresses all feedback issues:

- ✅ **Critical Fix**: Initial packets are now properly seeded in hotspot region
- ✅ **Sampling Fix**: Hotspot injection uses proper uniform disk sampling (r = R√u)
- ✅ **Type Fix**: Q parameter is now integer packets per timestep
- ✅ **Naming Fix**: Consistent class naming (MonteCarloSimulator)
- ✅ **Implementation**: ExperimentRunner class fully implemented
- ✅ **Performance**: Optimized version available using numpy arrays

## Quick Start

```bash
# Install dependencies
pip install numpy matplotlib

# Run the main simulation (all source code is in src/)
python start.py

# Or run directly from src directory
cd src
python generate_required_results.py
```

## Project Structure

```
Project 1a/
├── README.md
├── requirements.txt
├── start.py               # Main entry point - START HERE
├── src/                   # All source code here
│   ├── __init__.py
│   ├── config.py          # Configuration parameters (Q now integer)
│   ├── grid.py            # Grid management (fixed disk sampling)
│   ├── rng.py             # Random number generation
│   ├── model.py           # Heat packet model
│   ├── model_optimized.py # Performance-optimized version
│   ├── simulate.py        # Main simulation engine (fixed initialization)
│   ├── observables.py     # Data collection and metrics
│   ├── experiments.py     # Experiment framework (fully implemented)
│   └── generate_required_results.py  # Generate all required figures and tables
├── notebooks/
│   └── report_figures.ipynb
├── reporting/             # Output directory
│   └── required_results.pdf
└── outputs/
    ├── data/              # Simulation results
    └── figures/           # Generated plots
```

## Key Fixes Implemented

### 1. Critical Bug Fix: Initial Packet Seeding
**Problem**: Simulation started with zero packets, affecting early-time behavior
**Solution**: `_seed_initial_packets()` method places initial packets in hotspot

### 2. Hotspot Sampling Fix  
**Problem**: `r = rng.uniform(0, radius)` creates bias toward center
**Solution**: `r = radius * sqrt(rng.random())` for uniform area distribution

### 3. Type Consistency
**Problem**: Q declared as float but should be integer packets
**Solution**: Q parameter is now `int` type with proper validation

### 4. Naming Consistency
**Problem**: Import mismatch between `MonteCarloSim` and `MonteCarloSimulator`
**Solution**: Consistent naming throughout codebase

### 5. Missing Implementation
**Problem**: `ExperimentRunner` exported but not implemented
**Solution**: Full implementation with material comparison, parameter sweeps, convergence studies

## Features

- ✅ Modular Monte Carlo simulation framework
- ✅ Proper physics implementation (fixed initialization and sampling)
- ✅ Material comparison studies
- ✅ Design parameter optimization
- ✅ Statistical convergence analysis
- ✅ Performance optimization for large simulations
- ✅ Comprehensive visualization suite

## Example Usage

```python
from src.config import SimulationConfig
from src.simulate import MonteCarloSimulator
from src.experiments import ExperimentRunner

# Basic simulation
config = SimulationConfig.copper_config(t_max=2.0, Q=25)
simulator = MonteCarloSimulator(config)
results = simulator.run()

# Material comparison
runner = ExperimentRunner()
materials = {'Copper': 1.1e-4, 'Aluminum': 1.0e-4}
comparison = runner.compare_materials(materials, config)

# Convergence study
convergence = runner.convergence_study([1000, 2000, 5000], config)
```

## Validation

All fixes have been validated:
- Initial temperature curves now show proper hotspot behavior from t=0
- Hotspot sampling distribution verified as uniform over disk area
- Monte Carlo convergence follows expected 1/√N scaling
- Performance optimization maintains identical results