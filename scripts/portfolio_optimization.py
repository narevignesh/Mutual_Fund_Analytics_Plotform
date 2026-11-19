"""
Bluestock Fintech - Mutual Fund Analytics Platform
Script: scripts/portfolio_optimization.py
Objective: Bonus Educational Modules:
1. Monte Carlo Simulation for illustrative NAV projections.
2. Markowitz Efficient Frontier Portfolio Optimization (MPT).
"""

import os
import sqlite3
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DB_PATH = os.path.join("db", "bluestock_mf.db")
CHARTS_DIR = os.path.join("reports", "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

def run_monte_carlo_simulation(amfi_code: int = 125497, num_simulations: int = 1000, num_days: int = 252):
    """
    Simulates 1,000 geometric Brownian motion paths over 1 year (252 trading days).
    """
    conn = sqlite3.connect(DB_PATH)
    f_nav = pd.read_sql_query(f"SELECT date, nav FROM fact_nav WHERE amfi_code = {amfi_code} ORDER BY date", conn)
    f_name = pd.read_sql_query(f"SELECT scheme_name FROM dim_fund WHERE amfi_code = {amfi_code}", conn)["scheme_name"].iloc[0]
    conn.close()
    
    returns = f_nav["nav"].pct_change().dropna()
    mu = returns.mean()
    sigma = returns.std()
    last_nav = f_nav["nav"].iloc[-1]
    
    np.random.seed(42)
    dt = 1.0
    sim_paths = np.zeros((num_days, num_simulations))
    sim_paths[0] = last_nav
    
    for t in range(1, num_days):
        shocks = np.random.normal(0, 1, num_simulations)
        sim_paths[t] = sim_paths[t - 1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * shocks)
        
    p5 = np.percentile(sim_paths, 5, axis=1)
    p50 = np.percentile(sim_paths, 50, axis=1)
    p95 = np.percentile(sim_paths, 95, axis=1)
    
    plt.figure(figsize=(10, 5), dpi=300)
    plt.plot(sim_paths[:, :40], color="#94a3b8", alpha=0.15, lw=1)
    plt.plot(p50, color="#0284c7", lw=2.5, label=f"Median Projection (₹{p50[-1]:.2f})")
    plt.plot(p95, color="#22c55e", lw=1.8, linestyle="--", label=f"95th Percentile Bull (₹{p95[-1]:.2f})")
    plt.plot(p5, color="#ef4444", lw=1.8, linestyle="--", label=f"5th Percentile Bear (₹{p5[-1]:.2f})")
    
    plt.title(f"Illustrative Monte Carlo NAV Projection (1-Year, N=1,000 Simulations)\n{f_name[:45]}", fontsize=11, fontweight="bold")
    plt.xlabel("Trading Days Ahead (T+252)", fontsize=10)
    plt.ylabel("Projected NAV (INR)", fontsize=10)
    plt.legend(frameon=True, fontsize=9)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    
    out_path = os.path.join(CHARTS_DIR, "monte_carlo_simulation.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Monte Carlo simulation chart saved to {out_path}!")

def run_markowitz_optimization():
    """
    Computes Markowitz Efficient Frontier across representative fund categories.
    """
    conn = sqlite3.connect(DB_PATH)
    # Select 5 representative schemes across categories
    query = """
    SELECT n.date, f.category, n.nav
    FROM fact_nav n
    JOIN dim_fund f ON n.amfi_code = f.amfi_code
    WHERE f.amfi_code IN (119551, 125494, 100346, 100356, 100016)
    ORDER BY n.date;
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    piv = df.pivot_table(index="date", columns="category", values="nav").pct_change().dropna()
    mean_ret = piv.mean() * 250.0
    cov_matrix = piv.cov() * 250.0
    
    num_portfolios = 3000
    np.random.seed(42)
    all_weights = np.zeros((num_portfolios, len(piv.columns)))
    ret_arr = np.zeros(num_portfolios)
    vol_arr = np.zeros(num_portfolios)
    sharpe_arr = np.zeros(num_portfolios)
    rf = 0.065
    
    for i in range(num_portfolios):
        weights = np.random.random(len(piv.columns))
        weights /= np.sum(weights)
        all_weights[i, :] = weights
        ret_arr[i] = np.sum(mean_ret * weights)
        vol_arr[i] = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_arr[i] = (ret_arr[i] - rf) / (vol_arr[i] + 1e-9)
        
    max_sharpe_idx = sharpe_arr.argmax()
    min_vol_idx = vol_arr.argmin()
    
    plt.figure(figsize=(10, 5.5), dpi=300)
    sc = plt.scatter(vol_arr * 100.0, ret_arr * 100.0, c=sharpe_arr, cmap="viridis", marker="o", s=15, alpha=0.7)
    plt.colorbar(sc, label="Sharpe Ratio (Rf = 6.5%)")
    
    # Highlight Max Sharpe & Min Vol
    plt.scatter(vol_arr[max_sharpe_idx] * 100.0, ret_arr[max_sharpe_idx] * 100.0, c="red", s=120, edgecolors="black", marker="*", label=f"Max Sharpe ({sharpe_arr[max_sharpe_idx]:.2f})")
    plt.scatter(vol_arr[min_vol_idx] * 100.0, ret_arr[min_vol_idx] * 100.0, c="orange", s=100, edgecolors="black", marker="D", label=f"Min Volatility ({vol_arr[min_vol_idx]*100:.1f}%)")
    
    plt.title("Markowitz Efficient Frontier: Multi-Asset Mutual Fund Optimization", fontsize=11, fontweight="bold")
    plt.xlabel("Annualized Volatility / Risk (%)", fontsize=10)
    plt.ylabel("Expected Annualized Return (%)", fontsize=10)
    plt.legend(frameon=True, fontsize=9)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    
    out_path = os.path.join(CHARTS_DIR, "efficient_frontier.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Markowitz efficient frontier chart saved to {out_path}!")

if __name__ == "__main__":
    run_monte_carlo_simulation()
    run_markowitz_optimization()

