import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import scipy.signal as signal
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint


# -----------------------------
# Settings (simple constants)
# -----------------------------

ASSET_1 = "GLD"
ASSET_2 = "RING"

# Get paths relative to script location
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)

DATA_PATH_1 = os.path.join(project_dir, "data", "GOLD", "gld_us_d.csv")
DATA_PATH_2 = os.path.join(project_dir, "data", "GOLD", "ring_us_d.csv")

ENTRY_THRESHOLD = 2.0
EXIT_THRESHOLD = 0.0
ROLLING_WINDOW = 504

USE_MAX_HOLDING = False
MAX_HOLDING_DAYS = 60

OUTPUT_PDF = os.path.join(project_dir, "results", "results.pdf")
MAX_LAG_DISPLAY = 100


# -----------------------------
# Helpers
# -----------------------------

def make_output_folder(output_file):
    folder = os.path.dirname(output_file)
    if folder != "" and not os.path.exists(folder):
        os.makedirs(folder)


def load_prices():
    df1 = pd.read_csv(DATA_PATH_1)
    df2 = pd.read_csv(DATA_PATH_2)

    df1["Date"] = pd.to_datetime(df1["Date"])
    df2["Date"] = pd.to_datetime(df2["Date"])

    df1 = df1.set_index("Date")
    df2 = df2.set_index("Date")

    df = pd.DataFrame()
    df[ASSET_1] = df1["Close"]
    df[ASSET_2] = df2["Close"]

    df = df.dropna()

    return df


def normalise_series(df):
    df = df.copy()

    df[ASSET_1 + "_z"] = (df[ASSET_1] - df[ASSET_1].mean()) / df[ASSET_1].std()
    df[ASSET_2 + "_z"] = (df[ASSET_2] - df[ASSET_2].mean()) / df[ASSET_2].std()

    return df


def compute_lag(df):
    a = df[ASSET_1 + "_z"].values
    b = df[ASSET_2 + "_z"].values

    corr = signal.correlate(a, b, mode="same")
    lags = signal.correlation_lags(len(a), len(b), mode="same")
    best_lag = int(lags[np.argmax(corr)])

    return corr, lags, best_lag


def cointegration_test(df):
    # Engle-Granger test
    score, pvalue, _ = coint(df[ASSET_1], df[ASSET_2])
    return float(pvalue)


def hedge_ratio(df):
    X = sm.add_constant(df[ASSET_2])
    model = sm.OLS(df[ASSET_1], X).fit()

    beta = float(model.params[ASSET_2])
    intercept = float(model.params["const"])

    return beta, intercept


def spread_and_zscore(df, beta, intercept):
    df = df.copy()

    df["spread"] = df[ASSET_1] - (beta * df[ASSET_2] + intercept)
    df["roll_mean"] = df["spread"].rolling(ROLLING_WINDOW).mean()
    df["roll_std"] = df["spread"].rolling(ROLLING_WINDOW).std()
    df["z_score"] = (df["spread"] - df["roll_mean"]) / df["roll_std"]

    return df


def apply_signals(df):
    df = df.copy()
    df["signal"] = 0

    df.loc[df["z_score"] > ENTRY_THRESHOLD, "signal"] = -1
    df.loc[df["z_score"] < -ENTRY_THRESHOLD, "signal"] = 1

    # Exit rule
    df.loc[df["z_score"].abs() < EXIT_THRESHOLD, "signal"] = 0

    # Hold positions: replace 0 with NaN, ffill, then shift to avoid lookahead
    df["position"] = df["signal"].replace(0, np.nan).ffill()
    df["position"] = df["position"].shift(1)
    df["position"] = df["position"].fillna(0)

    if USE_MAX_HOLDING:
        df["position"] = max_holding_period(df["position"])

    return df


def max_holding_period(position_series):
    pos = position_series.copy()

    days = 0
    in_trade = False

    for i in range(len(pos)):
        if pos.iloc[i] == 0:
            in_trade = False
            days = 0
        else:
            if not in_trade:
                in_trade = True
                days = 0
            else:
                days += 1
                if days >= MAX_HOLDING_DAYS:
                    pos.iloc[i] = 0
                    in_trade = False
                    days = 0

    return pos


def compute_returns(df, beta):
    df = df.copy()

    df["ret1"] = df[ASSET_1].pct_change()
    df["ret2"] = df[ASSET_2].pct_change()

    df["strategy_ret"] = df["position"] * (df["ret1"] - beta * df["ret2"]) / (1 + beta)
    df["cum_ret"] = (1 + df["strategy_ret"].fillna(0)).cumprod()

    return df


def performance_metrics(df, coint_pvalue):
    # Basic summary stats, written "student-style"
    total_return = (df["cum_ret"].iloc[-1] - 1) * 100

    years = len(df) / 252.0
    if years > 0:
        annual_return = (df["cum_ret"].iloc[-1] ** (1 / years) - 1) * 100
    else:
        annual_return = 0

    vol = df["strategy_ret"].std() * np.sqrt(252) * 100

    if df["strategy_ret"].std() != 0:
        sharpe = (df["strategy_ret"].mean() / df["strategy_ret"].std()) * np.sqrt(252)
    else:
        sharpe = 0

    running_max = df["cum_ret"].cummax()
    dd = (df["cum_ret"] - running_max) / running_max
    max_dd = dd.min() * 100

    time_in_market = (df["position"] != 0).mean() * 100

    metrics = [
        ("Total Return", f"{total_return:.2f}%"),
        ("Annualised Return", f"{annual_return:.2f}%"),
        ("Volatility (Annual)", f"{vol:.2f}%"),
        ("Sharpe Ratio", f"{sharpe:.2f}"),
        ("Max Drawdown", f"{max_dd:.2f}%"),
        ("Time in Market", f"{time_in_market:.1f}%"),
        ("Cointegration p-value", f"{coint_pvalue:.4f}"),
    ]

    metrics_df = pd.DataFrame(metrics, columns=["Metric", "Value"])
    return metrics_df


# -----------------------------
# Plotting
# -----------------------------

def save_pdf(df, corr, lags, best_lag, metrics_df):
    make_output_folder(OUTPUT_PDF)

    with PdfPages(OUTPUT_PDF) as pdf:

        # Prices
        fig = plt.figure(figsize=(10, 6))
        plt.plot(df[ASSET_1], label=ASSET_1)
        plt.plot(df[ASSET_2], label=ASSET_2)
        plt.title("Historical Prices")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        # CCF
        fig = plt.figure(figsize=(12, 6))
        center = len(lags) // 2
        m = min(MAX_LAG_DISPLAY, center - 1)
        sl = slice(center - m, center + m)

        plt.plot(lags[sl], corr[sl])
        plt.axvline(best_lag, linestyle="--", label="Best Lag = " + str(best_lag))
        plt.axhline(0, alpha=0.3)
        plt.title("Cross-Correlation Function")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        # Z-score
        fig = plt.figure(figsize=(10, 6))
        plt.plot(df["z_score"], label="Z-score")
        plt.axhline(ENTRY_THRESHOLD, linestyle="--", label="Entry")
        plt.axhline(-ENTRY_THRESHOLD, linestyle="--")
        plt.axhline(EXIT_THRESHOLD, linestyle=":", label="Exit")
        plt.axhline(0, alpha=0.3)
        plt.title("Z-score and Thresholds")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        # Equity curve
        fig = plt.figure(figsize=(10, 6))
        plt.plot(df["cum_ret"], label="Equity curve")
        plt.title("Cumulative Returns")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        # Metrics table
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.axis("off")
        table = ax.table(
            cellText=metrics_df.values,
            colLabels=metrics_df.columns,
            cellLoc="center",
            loc="center",
            colWidths=[0.6, 0.4],
        )
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        plt.title("Performance Metrics", pad=20)
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)


# -----------------------------
# Main script
# -----------------------------

if __name__ == "__main__":
    print("Loading data...")
    df = load_prices()
    print("Data points after alignment:", len(df))

    df = normalise_series(df)

    # print(df.head())  # Debug
    # print(df.describe())  # Debug

    corr, lags, best_lag = compute_lag(df)
    print("Best lag (days):", best_lag)

    pvalue = cointegration_test(df)
    print("Cointegration p-value:", round(pvalue, 4))

    beta, intercept = hedge_ratio(df)
    print("Hedge ratio (beta):", round(beta, 4))

    df = spread_and_zscore(df, beta, intercept)
    df = apply_signals(df)
    df = compute_returns(df, beta)

    metrics_df = performance_metrics(df, pvalue)
    # print(metrics_df)  # Debug

    save_pdf(df, corr, lags, best_lag, metrics_df)
    print("Saved PDF to:", OUTPUT_PDF)