# Vibration Signal Analysis for Mechanical Wear Detection

This project demonstrates early detection of mechanical wear in rotating machinery using computational signal processing techniques. The implementation focuses on Fourier analysis and digital filtering to extract physically meaningful information from noisy vibration signals.

## Project Structure

```
├── src/                                    # Source code
│   ├── __init__.py                        # Package initialization
│   ├── signal_generator.py                # Vibration signal generation
│   ├── vibration_analysis.py              # Signal processing and analysis
│   └── demo_notebook.ipynb                # Interactive demonstration
├── create_complete_report.py              # Generate comprehensive PDF report
├── complete_vibration_analysis_report.pdf # Complete analysis report (9 pages)
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

### Interactive Analysis
```bash
cd src
jupyter notebook demo_notebook.ipynb
```

### Generate Complete Report
```bash
python create_complete_report.py
```

This creates `complete_vibration_analysis_report.pdf` with all figures, tables, and analysis results.

## Installation

```bash
pip install -r requirements.txt
```

## Academic Context

**Course:** PHYS6017 - Computer Techniques for Physics  
**Assignment:** Early Detection of Mechanical Wear in Rotating Machinery  
**Focus:** Computational physics methods for signal processing and diagnostics