# Vibration Signal Analysis for Mechanical Wear Detection

This project demonstrates early detection of mechanical wear in rotating machinery using computational signal processing techniques. The implementation focuses on Fourier analysis and digital filtering to extract physically meaningful information from noisy vibration signals.

## Project Structure

```
├── src/                                    # ALL Python source code here
│   ├── start.py                           # Main entry point - START HERE (generates complete report)
│   ├── wear_modeling_section.py           # Wear modeling documentation generator
│   ├── signal_generator.py                # Vibration signal generation
│   ├── vibration_analysis.py              # Signal processing and analysis
│   ├── demo_notebook.ipynb                # Interactive demonstration
│   └── __init__.py                        # Package initialization
├── reporting/                             # Generated PDF reports
│   ├── complete_vibration_analysis_report.pdf  # Complete analysis report (9 pages)
│   └── wear_modeling_supplement.pdf       # Wear modeling methodology (4 pages)
├── docs/                                  # Documentation and references
│   ├── wear_modeling_section.tex          # LaTeX methodology section
│   └── Assignment PDFs
├── requirements.txt                       # Python dependencies
└── README.md                              # This file
```

## Key Features

- Physics-based signal generation with configurable wear parameters
- FFT-based frequency domain analysis
- Digital filtering (low-pass, high-pass, band-pass)
- Quantitative indicators (RMS, band-limited power, harmonic ratios)
- Comprehensive visualization and reporting

## Usage

### Quick Start
```bash
cd src
python start.py
```

This generates the complete 9-page analysis report.

### Interactive Analysis
```bash
cd src
jupyter notebook demo_notebook.ipynb
```

## Installation

```bash
pip install -r requirements.txt
```

## Academic Context

**Course:** PHYS6017 - Computer Techniques for Physics  
**Assignment:** Early Detection of Mechanical Wear in Rotating Machinery  
**Focus:** Computational physics methods for signal processing and diagnostics