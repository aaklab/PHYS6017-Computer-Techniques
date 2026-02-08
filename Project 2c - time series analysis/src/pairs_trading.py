"""
Pairs Trading Analysis - New Implementation
"""

# ============================================================================
# Cell 1: Environment Setup
# ============================================================================
# This cell imports the necessary libraries for statistical analysis, signal processing, and PDF generation.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from statsmodels.tsa.stattools import coint, adfuller
import statsmodels.api as sm
import scipy.signal as signal
import os

# Get script directory for absolute paths
script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
project_dir = os.path.dirname(script_dir)  # Go up one level to project root

# Create data directory if it doesn't exist
data_dir = os.path.join(project_dir, 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Create results directory if it doesn't exist
results_dir = os.path.join(project_dir, 'results')
if not os.path.exists(results_dir):
    os.makedirs(results_dir)

# ============================================================================
# Cell 2: Configuration
# ============================================================================
# All main parameters are centralized here to ensure the notebook is flexible for different asset pairs and data folders.

# ============================================================================
# CONFIGURATION
# ============================================================================
ASSET_1_NAME = 'GLD'
ASSET_2_NAME = 'RING'

# Use absolute paths to avoid working directory issues
import os
script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
project_dir = os.path.dirname(script_dir)  # Go up one level to project root
DATA_PATH_1 = os.path.join(project_dir, 'data', 'GOLD', 'gld_us_d.csv')
DATA_PATH_2 = os.path.join(project_dir, 'data', 'GOLD', 'ring_us_d.csv')

# Strategy Parameters
ENTRY_THRESHOLD = 2.0      # Enter when |z-score| > threshold
EXIT_THRESHOLD = 0.0       # Exit when z-score returns to mean
ROLLING_WINDOW = 504        # Window for rolling mean/std calculation

# Maximum holding period
USE_MAX_HOLDING_PERIOD = False  # True = enforce max holding, False = no limit
MAX_HOLDING_DAYS = 60           # Maximum days to hold a position

# PDF Output file - save to project results folder
OUTPUT_PDF = os.path.join(project_dir, 'results', 'results.pdf')

# ============================================================================
# Cell 3: Data Acquisition and Alignment
# ============================================================================
# This cell loads the CSV files and merges them on common dates to ensure a synchronized "two-body" system.

# Load assets
asset1 = pd.read_csv(DATA_PATH_1, index_col='Date', parse_dates=True)
asset2 = pd.read_csv(DATA_PATH_2, index_col='Date', parse_dates=True)

# Align data on close prices
df = pd.DataFrame({
    ASSET_1_NAME: asset1['Close'],
    ASSET_2_NAME: asset2['Close']
}).dropna()

print(f"Synchronized data points: {len(df)}")

# ============================================================================
# Cell 4: Normalization (Z-Score)
# ============================================================================
# Prices are transformed into dimensionless quantities to enable scale-independent comparison.

df[f'{ASSET_1_NAME}_z'] = (df[ASSET_1_NAME] - df[ASSET_1_NAME].mean()) / df[ASSET_1_NAME].std()
df[f'{ASSET_2_NAME}_z'] = (df[ASSET_2_NAME] - df[ASSET_2_NAME].mean()) / df[ASSET_2_NAME].std()

plt.figure(figsize=(12,6))
plt.plot(df[f'{ASSET_1_NAME}_z'], label=f'{ASSET_1_NAME} (Normalized)')
plt.plot(df[f'{ASSET_2_NAME}_z'], label=f'{ASSET_2_NAME} (Normalized)')
plt.title('Normalized Price Series')
plt.legend()
plt.show()

# ============================================================================
# Cell 5: Lag Analysis (CCF)
# ============================================================================
# Using the Cross-Correlation Function to identify temporal latency between the two assets.

correlation = signal.correlate(df[f'{ASSET_1_NAME}_z'], df[f'{ASSET_2_NAME}_z'], mode='same')
lags = signal.correlation_lags(len(df[f'{ASSET_1_NAME}_z']), len(df[f'{ASSET_2_NAME}_z']), mode='same')
optimal_lag = lags[np.argmax(correlation)]

print(f"Optimal temporal lag: {optimal_lag} steps")

# ============================================================================
# Cell 6: Cointegration and Hedge Ratio
# ============================================================================
# Testing for a long-term equilibrium relationship and calculating the Beta (hedge ratio) via OLS regression.

# Cointegration test
score, pvalue, _ = coint(df[ASSET_1_NAME], df[ASSET_2_NAME])
print(f"Cointegration p-value: {pvalue:.4f}")

# OLS for Hedge Ratio (full period)
X = sm.add_constant(df[ASSET_2_NAME])
model = sm.OLS(df[ASSET_1_NAME], X).fit()
hedge_ratio = model.params[ASSET_2_NAME]
intercept = model.params['const']

print(f"Hedge Ratio (Beta): {hedge_ratio:.4f}")

# ============================================================================
# Cell 7: Spread Construction and Signal Generation
# ============================================================================
# Constructing the mean-reverting spread and defining trade entries/exits based on the rolling Z-score.

# Calculate spread and rolling Z-score
df['spread'] = df[ASSET_1_NAME] - (hedge_ratio * df[ASSET_2_NAME] + intercept)
df['roll_mean'] = df['spread'].rolling(ROLLING_WINDOW).mean()
df['roll_std'] = df['spread'].rolling(ROLLING_WINDOW).std()
df['z_score'] = (df['spread'] - df['roll_mean']) / df['roll_std']

# Trading Logic
df['signal'] = 0
df.loc[df['z_score'] > ENTRY_THRESHOLD, 'signal'] = -1  # Short spread
df.loc[df['z_score'] < -ENTRY_THRESHOLD, 'signal'] = 1  # Long spread
df.loc[abs(df['z_score']) < EXIT_THRESHOLD, 'signal'] = 0

# Track active position (hold until exit)
# Use the original logic: replace 0 with NaN, forward fill, then shift by 1 day
df['position'] = df['signal'].replace(0, np.nan).ffill().shift(1).fillna(0)

# Enforce maximum holding period if enabled
if USE_MAX_HOLDING_PERIOD:
    position_entry_idx = None
    position_days = 0
    
    for i in range(len(df)):
        current_position = df.iloc[i]['position']
        
        if current_position != 0:
            if position_entry_idx is None:
                # New position entry
                position_entry_idx = i
                position_days = 0
            else:
                # Continuing position
                position_days += 1
                
                # Force exit if max holding period reached
                if position_days >= MAX_HOLDING_DAYS:
                    df.iloc[i, df.columns.get_loc('position')] = 0
                    position_entry_idx = None
                    position_days = 0
        else:
            # Position closed
            position_entry_idx = None
            position_days = 0

# ============================================================================
# Cell 8: Performance Calculation
# ============================================================================
# Calculating strategy returns and the cumulative equity curve.

df['ret1'] = df[ASSET_1_NAME].pct_change()
df['ret2'] = df[ASSET_2_NAME].pct_change()

# Strategy Return: position * (Return_Asset1 - Beta * Return_Asset2) / (1 + Beta)
# Normalize by total capital invested in both legs
df['strategy_ret'] = df['position'] * (df['ret1'] - hedge_ratio * df['ret2']) / (1 + hedge_ratio)
df['cum_ret'] = (1 + df['strategy_ret'].fillna(0)).cumprod()

# ============================================================================
# Cell 9: Plot Generation and PDF Export
# ============================================================================
# This final cell creates all visualizations and exports them into the required results_pt.pdf file.

with PdfPages(OUTPUT_PDF) as pdf:
    # Plot 1: Prices
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(df[ASSET_1_NAME], label=ASSET_1_NAME)
    ax1.plot(df[ASSET_2_NAME], label=ASSET_2_NAME)
    ax1.set_title(f'Historical Prices: {ASSET_1_NAME} and {ASSET_2_NAME}')
    ax1.legend()
    pdf.savefig(fig1)
    plt.close()
    
    # Plot 2: Cross-Correlation Function
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    
    # Limit the lag range for better visualization (e.g., ±100 days)
    max_lag_display = min(100, len(lags) // 2)
    center_idx = len(lags) // 2
    lag_slice = slice(center_idx - max_lag_display, center_idx + max_lag_display)
    
    ax2.plot(lags[lag_slice], correlation[lag_slice], linewidth=1.5, color='darkblue')
    ax2.axvline(optimal_lag, color='red', linestyle='--', linewidth=2, 
                label=f'Optimal Lag: {optimal_lag} days')
    ax2.axvline(0, color='black', linestyle='-', alpha=0.3)
    ax2.axhline(0, color='black', linestyle='-', alpha=0.3)
    
    ax2.set_title('Cross-Correlation Function (CCF)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Lag (days)', fontsize=11)
    ax2.set_ylabel('Cross-Correlation', fontsize=11)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    pdf.savefig(fig2)
    plt.close()
    
    # Plot 3: Z-Score Signals
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    ax3.plot(df['z_score'], label='Spread Z-Score')
    ax3.axhline(ENTRY_THRESHOLD, color='r', linestyle='--', label='Entry Threshold')
    ax3.axhline(-ENTRY_THRESHOLD, color='r', linestyle='--')
    ax3.axhline(0, color='black')
    ax3.set_title('Trading Signals (Z-Score)')
    ax3.legend()
    pdf.savefig(fig3)
    plt.close()
    
    # Plot 4: Equity Curve
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    ax4.plot(df['cum_ret'], color='gold', label='Strategy Equity')
    ax4.set_title('Cumulative Strategy Returns')
    ax4.set_ylabel('Growth of $1')
    ax4.grid(True)
    pdf.savefig(fig4)
    plt.close()
    
    # Plot 5: Z-Score with Trading Signals
    fig5, ax5 = plt.subplots(figsize=(14, 7))
    
    # Plot z-score
    ax5.plot(df.index, df['z_score'], linewidth=1, color='blue', alpha=0.7, label='Z-Score')
    
    # Add threshold lines
    ax5.axhline(ENTRY_THRESHOLD, color='red', linestyle='--', linewidth=1.5, 
                label=f'Entry Threshold (±{ENTRY_THRESHOLD})')
    ax5.axhline(-ENTRY_THRESHOLD, color='red', linestyle='--', linewidth=1.5)
    ax5.axhline(EXIT_THRESHOLD, color='green', linestyle=':', linewidth=1.5, 
                label=f'Exit Threshold ({EXIT_THRESHOLD})')
    ax5.axhline(0, color='black', linestyle='-', alpha=0.3)
    
    # Mark ACTUAL trade entry points (matching the trade counting logic)
    prev_position = df['position'].shift(1).fillna(0)
    
    # Entry from flat: was 0, now non-zero
    entries_from_flat = (prev_position == 0) & (df['position'] != 0)
    
    # Sign change: was long now short, or was short now long
    sign_changes = (prev_position * df['position'] < 0) & (prev_position != 0) & (df['position'] != 0)
    
    # All trade entries
    all_entries = entries_from_flat | sign_changes
    entry_points = df[all_entries]
    
    # Separate long and short entries based on the NEW position
    long_entries = entry_points[entry_points['position'] > 0]
    short_entries = entry_points[entry_points['position'] < 0]
    
    ax5.scatter(long_entries.index, long_entries['z_score'], 
                color='green', marker='^', s=100, label='Long Entry', zorder=5, alpha=0.8)
    ax5.scatter(short_entries.index, short_entries['z_score'], 
                color='red', marker='v', s=100, label='Short Entry', zorder=5, alpha=0.8)
    
    ax5.set_title('Trading Signals Based on Z-Score', fontsize=14, fontweight='bold')
    ax5.set_xlabel('Date', fontsize=11)
    ax5.set_ylabel('Z-Score', fontsize=11)
    ax5.legend(fontsize=10, loc='best')
    ax5.grid(True, alpha=0.3)
    plt.tight_layout()
    pdf.savefig(fig5)
    plt.close()
    
    # Plot 6: Performance Metrics Table
    # Calculate metrics
    total_return = (df['cum_ret'].iloc[-1] - 1) * 100
    years = len(df) / 252
    annual_return = ((df['cum_ret'].iloc[-1]) ** (1/years) - 1) * 100
    volatility = df['strategy_ret'].std() * np.sqrt(252) * 100
    sharpe_ratio = (df['strategy_ret'].mean() / df['strategy_ret'].std()) * np.sqrt(252) if df['strategy_ret'].std() > 0 else 0
    
    # Trade statistics
    winning_days = (df['strategy_ret'] > 0).sum()
    losing_days = (df['strategy_ret'] < 0).sum()
    total_trading_days = winning_days + losing_days
    win_rate = (winning_days / total_trading_days * 100) if total_trading_days > 0 else 0
    
    # Count actual position entries (for transaction costs)
    # An entry occurs when:
    # 1. Position goes from 0 to non-zero (entry from flat)
    # 2. Position changes sign (long to short or short to long)
    
    # Detect position changes
    prev_position = df['position'].shift(1).fillna(0)
    
    # Entry from flat: was 0, now non-zero
    entries_from_flat = (prev_position == 0) & (df['position'] != 0)
    
    # Sign change: was long now short, or was short now long
    sign_changes = (prev_position * df['position'] < 0) & (prev_position != 0) & (df['position'] != 0)
    
    # Total trades
    number_of_trades = (entries_from_flat | sign_changes).sum()
    
    print(f"\nDEBUG: Entries from flat: {entries_from_flat.sum()}")
    print(f"DEBUG: Sign changes: {sign_changes.sum()}")
    print(f"DEBUG: Total trades: {number_of_trades}")
    
    # Calculate average holding period per trade
    # Track each trade's duration
    trade_durations = []
    current_trade_start = None
    
    for i in range(len(df)):
        # Check if this is a trade entry
        if (entries_from_flat.iloc[i] or sign_changes.iloc[i]):
            # If we were already in a trade, record its duration
            if current_trade_start is not None:
                duration = i - current_trade_start
                trade_durations.append(duration)
            # Start new trade
            current_trade_start = i
        # Check if position closed (went to 0)
        elif current_trade_start is not None and df.iloc[i]['position'] == 0:
            duration = i - current_trade_start
            trade_durations.append(duration)
            current_trade_start = None
    
    # Handle case where last trade is still open
    if current_trade_start is not None:
        duration = len(df) - current_trade_start
        trade_durations.append(duration)
    
    avg_holding_period = np.mean(trade_durations) if trade_durations else 0
    
    # Max drawdown
    cumulative = df['cum_ret']
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max * 100
    max_drawdown = drawdown.min()
    
    # Time in market
    days_in_position = (df['position'] != 0).sum()
    time_in_market = (days_in_position / len(df)) * 100
    
    # Full-period cointegration (already calculated earlier)
    # Use the pvalue from Cell 6
    full_period_coint = pvalue
    
    # Create performance summary table
    metrics_data = {
        'Metric': [
            'Total Return',
            'Annualized Return',
            'Volatility (Annual)',
            'Sharpe Ratio',
            'Max Drawdown',
            'Number of Trades',
            'Average Holding Period (Days)',
            'Winning Days',
            'Losing Days',
            'Total Trading Days',
            'Win Rate',
            'Time in Market',
            'Trading Period (Years)',
            'Cointegration (Full Period)'
        ],
        'Value': [
            f'{total_return:.2f}%',
            f'{annual_return:.2f}%',
            f'{volatility:.2f}%',
            f'{sharpe_ratio:.2f}',
            f'{max_drawdown:.2f}%',
            f'{number_of_trades}',
            f'{avg_holding_period:.1f}',
            f'{winning_days}',
            f'{losing_days}',
            f'{total_trading_days}',
            f'{win_rate:.1f}%',
            f'{time_in_market:.1f}%',
            f'{years:.2f}',
            f'{full_period_coint:.4f}'
        ]
    }
    
    metrics_df = pd.DataFrame(metrics_data)
    
    # Create table figure
    fig6, ax6 = plt.subplots(figsize=(10, 8))
    ax6.axis('tight')
    ax6.axis('off')
    
    table = ax6.table(cellText=metrics_df.values, 
                      colLabels=metrics_df.columns,
                      cellLoc='left',
                      loc='center',
                      colWidths=[0.6, 0.4])
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2)
    
    # Style header
    for i in range(len(metrics_df.columns)):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(metrics_df) + 1):
        for j in range(len(metrics_df.columns)):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#E7E6E6')
    
    plt.title('Strategy Performance Metrics', fontsize=14, fontweight='bold', pad=20)
    pdf.savefig(fig6, bbox_inches='tight')
    plt.close()
    
    # ============================================================================
    # Plot 7: Annual Performance Table
    # ============================================================================
    # Calculate annual returns
    
    # Group by year
    df['year'] = df.index.year
    annual_data = []
    
    for year in sorted(df['year'].unique()):
        year_df = df[df['year'] == year]
        
        # Calculate annual return
        if len(year_df) > 0 and year_df['cum_ret'].iloc[0] > 0:
            year_start = year_df['cum_ret'].iloc[0]
            year_end = year_df['cum_ret'].iloc[-1]
            annual_return = ((year_end / year_start) - 1) * 100
        else:
            annual_return = 0
        
        annual_data.append({
            'Year': year,
            'Annual Return (%)': f'{annual_return:.2f}'
        })
    
    annual_df = pd.DataFrame(annual_data)
    
    # Create annual table figure
    fig7, ax7 = plt.subplots(figsize=(10, 8))
    ax7.axis('tight')
    ax7.axis('off')
    
    table2 = ax7.table(cellText=annual_df.values, 
                       colLabels=annual_df.columns,
                       cellLoc='center',
                       loc='center',
                       colWidths=[0.3, 0.7])
    
    table2.auto_set_font_size(False)
    table2.set_fontsize(10)
    table2.scale(1, 2)
    
    # Style header
    for i in range(len(annual_df.columns)):
        table2[(0, i)].set_facecolor('#4472C4')
        table2[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(annual_df) + 1):
        for j in range(len(annual_df.columns)):
            if i % 2 == 0:
                table2[(i, j)].set_facecolor('#E7E6E6')
    
    plt.title(f'Annual Returns\n(Rolling Window: {ROLLING_WINDOW} days)', 
              fontsize=14, fontweight='bold', pad=20)
    pdf.savefig(fig7, bbox_inches='tight')
    plt.close()

print(f"Analysis complete. All plots saved to {OUTPUT_PDF}")

# Print metrics to console
print('\n' + '='*70)
print('PERFORMANCE METRICS SUMMARY')
print('='*70)
print(metrics_df.to_string(index=False))
print('='*70)

# Print annual performance to console
print('\n' + '='*70)
print(f'ANNUAL PERFORMANCE & COINTEGRATION (Rolling Window: {ROLLING_WINDOW} days)')
print('='*70)
print(annual_df.to_string(index=False))
print('='*70)
