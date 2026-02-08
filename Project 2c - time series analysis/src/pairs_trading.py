"""
Pairs trading analysis (beginner/intermediate style version)

Goal: same outputs as the refactored version:
- same PDF pages (prices, CCF, z-score, equity curve, scatter signals, metrics table, annual returns table)
- same printed metrics + annual returns
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import scipy.signal as signal
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint


# -----------------------------
# Settings (simple + visible)
# -----------------------------

ASSET_1 = "GLD"
ASSET_2 = "RING"

DATA_PATH_1 = "data/GOLD/gld_us_d.csv"
DATA_PATH_2 = "data/GOLD/ring_us_d.csv"

ENTRY_THRESHOLD = 2.0
EXIT_THRESHOLD = 0.0
ROLLING_WINDOW = 504

USE_MAX_HOLDING_PERIOD = False
MAX_HOLDING_DAYS = 60

OUTPUT_PDF = "results/results.pdf"
MAX_LAG_DISPLAY = 100

SHOW_NORMALISED_PLOT = True


# -----------------------------
# Small helpers
# -----------------------------

def ensure_parent_dirs(filepath):
    folder = os.path.dirname(filepath)
    if folder and (not os.path.exists(folder)):
        os.makedirs(folder)


def get_project_dir():
    # Slightly "student-ish" way: try __file__, otherwise use cwd
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        return os.path.abspath(os.path.join(here, ".."))
    except NameError:
        return os.getcwd()


def resolve_paths():
    proj = get_project_dir()
    p1 = os.path.join(proj, DATA_PATH_1)
    p2 = os.path.join(proj, DATA_PATH_2)
    out = os.path.join(proj, OUTPUT_PDF)
    return p1, p2, out


# -----------------------------
# Data loading & preprocessing
# -----------------------------

def load_and_align_prices(path1, path2):
    a1 = pd.read_csv(path1, index_col="Date", parse_dates=True)
    a2 = pd.read_csv(path2, index_col="Date", parse_dates=True)

    df = pd.DataFrame(
        {
            ASSET_1: a1["Close"],
            ASSET_2: a2["Close"],
        }
    ).dropna()

    return df


def add_normalised_series(df):
    df = df.copy()

    # IMPORTANT: ddof=0 matches the refactored version exactly
    df[ASSET_1 + "_z"] = (df[ASSET_1] - df[ASSET_1].mean()) / df[ASSET_1].std(ddof=0)
    df[ASSET_2 + "_z"] = (df[ASSET_2] - df[ASSET_2].mean()) / df[ASSET_2].std(ddof=0)

    return df


def estimate_optimal_lag(df):
    corr = signal.correlate(df[ASSET_1 + "_z"], df[ASSET_2 + "_z"], mode="same")
    lags = signal.correlation_lags(len(df[ASSET_1 + "_z"]), len(df[ASSET_2 + "_z"]), mode="same")
    best_lag = int(lags[np.argmax(corr)])
    return corr, lags, best_lag


# -----------------------------
# Cointegration & hedge ratio
# -----------------------------

def compute_cointegration_pvalue(df):
    _, pvalue, _ = coint(df[ASSET_1], df[ASSET_2])
    return float(pvalue)


def estimate_hedge_ratio(df):
    X = sm.add_constant(df[ASSET_2])
    model = sm.OLS(df[ASSET_1], X).fit()

    beta = float(model.params[ASSET_2])
    intercept = float(model.params["const"])
    return beta, intercept


# -----------------------------
# Spread, signals, positions
# -----------------------------

def compute_spread_and_zscore(df, beta, intercept):
    df = df.copy()

    df["spread"] = df[ASSET_1] - (beta * df[ASSET_2] + intercept)
    df["roll_mean"] = df["spread"].rolling(ROLLING_WINDOW).mean()
    df["roll_std"] = df["spread"].rolling(ROLLING_WINDOW).std()
    df["z_score"] = (df["spread"] - df["roll_mean"]) / df["roll_std"]

    return df


def enforce_max_holding(position_series, max_days):
    pos = position_series.copy()

    days_in_trade = 0
    in_trade = False

    for i in range(len(pos)):
        if pos.iat[i] == 0:
            in_trade = False
            days_in_trade = 0
        else:
            if not in_trade:
                in_trade = True
                days_in_trade = 0
            else:
                days_in_trade += 1
                if days_in_trade >= max_days:
                    pos.iat[i] = 0
                    in_trade = False
                    days_in_trade = 0

    return pos


def generate_positions(df):
    df = df.copy()

    df["signal"] = 0
    df.loc[df["z_score"] > ENTRY_THRESHOLD, "signal"] = -1
    df.loc[df["z_score"] < -ENTRY_THRESHOLD, "signal"] = 1
    df.loc[df["z_score"].abs() < EXIT_THRESHOLD, "signal"] = 0

    # Hold positions: ffill and shift to avoid lookahead (matches refactor)
    df["position"] = df["signal"].replace(0, np.nan).ffill().shift(1).fillna(0)

    if USE_MAX_HOLDING_PERIOD:
        df["position"] = enforce_max_holding(df["position"], MAX_HOLDING_DAYS)

    return df


def compute_strategy_returns(df, beta):
    df = df.copy()

    df["ret1"] = df[ASSET_1].pct_change()
    df["ret2"] = df[ASSET_2].pct_change()

    # Matches refactor exactly
    df["strategy_ret"] = df["position"] * (df["ret1"] - beta * df["ret2"]) / (1.0 + beta)
    df["cum_ret"] = (1.0 + df["strategy_ret"].fillna(0)).cumprod()

    return df


# -----------------------------
# Trade detection + performance
# -----------------------------

def detect_trade_entries(position):
    prev_position = position.shift(1).fillna(0)

    entries_from_flat = (prev_position == 0) & (position != 0)
    sign_changes = (prev_position * position < 0) & (prev_position != 0) & (position != 0)

    return prev_position, entries_from_flat, sign_changes


def compute_trade_durations(position):
    _, entries_from_flat, sign_changes = detect_trade_entries(position)
    entries = entries_from_flat | sign_changes

    durations = []
    current_start = None

    for i in range(len(position)):
        if entries.iloc[i]:
            if current_start is not None:
                durations.append(i - current_start)
            current_start = i
        elif current_start is not None and position.iloc[i] == 0:
            durations.append(i - current_start)
            current_start = None

    if current_start is not None:
        durations.append(len(position) - current_start)

    return durations


def compute_annual_returns(df):
    tmp = df.copy()
    tmp["year"] = tmp.index.year

    rows = []
    for year in sorted(tmp["year"].unique()):
        year_df = tmp[tmp["year"] == year]
        if len(year_df) < 2:
            annual_ret = 0.0
        else:
            start = year_df["cum_ret"].iloc[0]
            end = year_df["cum_ret"].iloc[-1]
            annual_ret = ((end / start) - 1.0) * 100.0 if start > 0 else 0.0

        rows.append({"Year": int(year), "Annual Return (%)": f"{annual_ret:.2f}"})

    return pd.DataFrame(rows)


def compute_performance_metrics(df, coint_pvalue):
    total_return_pct = (df["cum_ret"].iloc[-1] - 1.0) * 100.0
    years = len(df) / 252.0

    if years > 0:
        annual_return_pct = ((df["cum_ret"].iloc[-1]) ** (1.0 / years) - 1.0) * 100.0
    else:
        annual_return_pct = 0.0

    vol_pct = df["strategy_ret"].std() * np.sqrt(252) * 100.0

    sr_denom = df["strategy_ret"].std()
    if sr_denom and sr_denom > 0:
        sharpe = (df["strategy_ret"].mean() / sr_denom) * np.sqrt(252)
    else:
        sharpe = 0.0

    winning_days = int((df["strategy_ret"] > 0).sum())
    losing_days = int((df["strategy_ret"] < 0).sum())
    total_trading_days = winning_days + losing_days

    if total_trading_days > 0:
        win_rate = (winning_days / total_trading_days) * 100.0
    else:
        win_rate = 0.0

    prev_pos, entries_from_flat, sign_changes = detect_trade_entries(df["position"])
    number_of_trades = int((entries_from_flat | sign_changes).sum())

    durations = compute_trade_durations(df["position"])
    avg_holding = float(np.mean(durations)) if durations else 0.0

    running_max = df["cum_ret"].cummax()
    drawdown = (df["cum_ret"] - running_max) / running_max * 100.0
    max_drawdown_pct = float(drawdown.min())

    time_in_market = float((df["position"] != 0).mean() * 100.0)

    metrics = pd.DataFrame(
        {
            "Metric": [
                "Total Return",
                "Annualized Return",
                "Volatility (Annual)",
                "Sharpe Ratio",
                "Max Drawdown",
                "Number of Trades",
                "Average Holding Period (Days)",
                "Winning Days",
                "Losing Days",
                "Total Trading Days",
                "Win Rate",
                "Time in Market",
                "Trading Period (Years)",
                "Cointegration (Full Period)",
            ],
            "Value": [
                f"{total_return_pct:.2f}%",
                f"{annual_return_pct:.2f}%",
                f"{vol_pct:.2f}%",
                f"{sharpe:.2f}",
                f"{max_drawdown_pct:.2f}%",
                f"{number_of_trades}",
                f"{avg_holding:.1f}",
                f"{winning_days}",
                f"{losing_days}",
                f"{total_trading_days}",
                f"{win_rate:.1f}%",
                f"{time_in_market:.1f}%",
                f"{years:.2f}",
                f"{coint_pvalue:.4f}",
            ],
        }
    )

    annual_df = compute_annual_returns(df)
    return metrics, annual_df


# -----------------------------
# Plotting (kept same)
# -----------------------------

def plot_normalised(df):
    plt.figure(figsize=(12, 6))
    plt.plot(df[ASSET_1 + "_z"], label=f"{ASSET_1} (Normalised)")
    plt.plot(df[ASSET_2 + "_z"], label=f"{ASSET_2} (Normalised)")
    plt.title("Normalised Price Series")
    plt.legend()
    plt.tight_layout()
    plt.show()


def add_prices_plot(pdf, df):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df[ASSET_1], label=ASSET_1)
    ax.plot(df[ASSET_2], label=ASSET_2)
    ax.set_title(f"Historical Prices: {ASSET_1} and {ASSET_2}")
    ax.legend()
    ax.grid(True, alpha=0.3)
    pdf.savefig(fig)
    plt.close(fig)


def add_ccf_plot(pdf, lags, corr, best_lag):
    fig, ax = plt.subplots(figsize=(12, 6))

    max_lag = min(MAX_LAG_DISPLAY, len(lags) // 2)
    center = len(lags) // 2
    sl = slice(center - max_lag, center + max_lag)

    ax.plot(lags[sl], corr[sl], linewidth=1.5)
    ax.axvline(best_lag, linestyle="--", linewidth=2, label=f"Optimal Lag: {best_lag} days")
    ax.axvline(0, alpha=0.3)
    ax.axhline(0, alpha=0.3)

    ax.set_title("Cross-Correlation Function (CCF)")
    ax.set_xlabel("Lag (days)")
    ax.set_ylabel("Cross-correlation")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)


def add_zscore_plot(pdf, df):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df["z_score"], label="Spread Z-Score")
    ax.axhline(ENTRY_THRESHOLD, linestyle="--", label="Entry Threshold")
    ax.axhline(-ENTRY_THRESHOLD, linestyle="--")
    ax.axhline(EXIT_THRESHOLD, linestyle=":", label="Exit Threshold")
    ax.axhline(0, alpha=0.3)
    ax.set_title("Trading Signals (Z-Score)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)


def add_equity_plot(pdf, df):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df["cum_ret"], label="Strategy Equity")
    ax.set_title("Cumulative Strategy Returns")
    ax.set_ylabel("Growth of $1")
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)


def add_signal_scatter_plot(pdf, df):
    fig, ax = plt.subplots(figsize=(14, 7))

    ax.plot(df.index, df["z_score"], linewidth=1, alpha=0.7, label="Z-Score")
    ax.axhline(ENTRY_THRESHOLD, linestyle="--", linewidth=1.5, label=f"Entry Threshold (±{ENTRY_THRESHOLD})")
    ax.axhline(-ENTRY_THRESHOLD, linestyle="--", linewidth=1.5)
    ax.axhline(EXIT_THRESHOLD, linestyle=":", linewidth=1.5, label=f"Exit Threshold ({EXIT_THRESHOLD})")
    ax.axhline(0, alpha=0.3)

    prev_pos, entries_from_flat, sign_changes = detect_trade_entries(df["position"])
    entries = entries_from_flat | sign_changes
    entry_points = df[entries]

    long_entries = entry_points[entry_points["position"] > 0]
    short_entries = entry_points[entry_points["position"] < 0]

    ax.scatter(long_entries.index, long_entries["z_score"], marker="^", s=80, label="Long Entry", zorder=5, alpha=0.8)
    ax.scatter(short_entries.index, short_entries["z_score"], marker="v", s=80, label="Short Entry", zorder=5, alpha=0.8)

    ax.set_title("Trading Signals Based on Z-Score")
    ax.set_xlabel("Date")
    ax.set_ylabel("Z-Score")
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    pdf.savefig(fig)
    plt.close(fig)


def add_table_plot(pdf, title, table_df, col_widths):
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis("tight")
    ax.axis("off")

    table = ax.table(
        cellText=table_df.values,
        colLabels=table_df.columns,
        cellLoc="center" if len(table_df.columns) == 2 else "left",
        loc="center",
        colWidths=col_widths,
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    plt.title(title, fontsize=14, pad=20)
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def export_pdf(outpath, df, corr, lags, best_lag, metrics_df, annual_df):
    ensure_parent_dirs(outpath)

    with PdfPages(outpath) as pdf:
        add_prices_plot(pdf, df)
        add_ccf_plot(pdf, lags, corr, best_lag)
        add_zscore_plot(pdf, df)
        add_equity_plot(pdf, df)
        add_signal_scatter_plot(pdf, df)
        add_table_plot(pdf, "Strategy Performance Metrics", metrics_df, col_widths=[0.6, 0.4])
        add_table_plot(pdf, f"Annual Returns\n(Rolling Window: {ROLLING_WINDOW} days)", annual_df, col_widths=[0.3, 0.7])


# -----------------------------
# Main script
# -----------------------------

if __name__ == "__main__":
    path1, path2, out_pdf = resolve_paths()
    ensure_parent_dirs(out_pdf)

    print("Loading and aligning prices...")
    df = load_and_align_prices(path1, path2)
    print("Synchronized data points:", len(df))

    df = add_normalised_series(df)

    # print(df.head())  # debug
    # print(df.describe())  # debug

    if SHOW_NORMALISED_PLOT:
        plot_normalised(df)

    corr, lags, best_lag = estimate_optimal_lag(df)
    print("Optimal temporal lag:", best_lag, "steps")

    pvalue = compute_cointegration_pvalue(df)
    print("Cointegration p-value:", f"{pvalue:.4f}")

    beta, intercept = estimate_hedge_ratio(df)
    print("Hedge Ratio (Beta):", f"{beta:.4f}")

    df = compute_spread_and_zscore(df, beta, intercept)
    df = generate_positions(df)
    df = compute_strategy_returns(df, beta)

    metrics_df, annual_df = compute_performance_metrics(df, pvalue)

    export_pdf(out_pdf, df, corr, lags, best_lag, metrics_df, annual_df)

    print("\nAnalysis complete. All plots saved to", out_pdf)

    print("\n" + "=" * 70)
    print("PERFORMANCE METRICS SUMMARY")
    print("=" * 70)
    print(metrics_df.to_string(index=False))
    print("=" * 70)

    print("\n" + "=" * 70)
    print("ANNUAL PERFORMANCE (Rolling Window: {} days)".format(ROLLING_WINDOW))
    print("=" * 70)
    print(annual_df.to_string(index=False))
    print("=" * 70)