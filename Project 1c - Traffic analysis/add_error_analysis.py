# Add this cell after the fundamental_diagram function definition
# This is the error analysis version that runs multiple simulations

def fundamental_diagram_with_errors(L, v_max, p, N_values, warmup=200, measure_steps=500, n_runs=20):
    """
    Calculate flow vs density with error bars using multiple independent runs.
    
    Parameters:
    - L: road length
    - v_max: maximum velocity
    - p: randomization probability
    - N_values: list of car numbers to test
    - warmup: number of warmup steps
    - measure_steps: number of measurement steps
    - n_runs: number of independent runs per density (default 20)
    
    Returns:
    - densities: array of density values
    - mean_flows: mean flow at each density
    - std_flows: standard deviation at each density
    - sem_flows: standard error of mean at each density
    """
    densities = []
    mean_flows = []
    std_flows = []
    sem_flows = []
    
    for N in N_values:
        density = N / L
        flows_at_this_density = []
        
        # Run multiple simulations with different seeds
        for run in range(n_runs):
            rng = np.random.default_rng(1000 + run)  # Unique seed for each run
            road = init_road(L, N, rng)
            
            # Warmup phase to reach steady state
            for _ in range(warmup):
                road, _ = step(road, v_max, p, rng)
            
            # Measurement phase
            total_distance = 0
            for _ in range(measure_steps):
                road, dist = step(road, v_max, p, rng)
                total_distance += dist
            
            # Calculate flow for this run
            flow = total_distance / (L * measure_steps)
            flows_at_this_density.append(flow)
        
        # Compute statistics for this density
        densities.append(density)
        mean_flows.append(np.mean(flows_at_this_density))
        std_flows.append(np.std(flows_at_this_density, ddof=1))
        sem_flows.append(np.std(flows_at_this_density, ddof=1) / np.sqrt(n_runs))
    
    return np.array(densities), np.array(mean_flows), np.array(std_flows), np.array(sem_flows)


# ============================================================================
# Investigation 2 - Effect of randomness (p) WITH ERROR BARS
# ============================================================================

print("\n--- Running Investigation 2 with Error Analysis ---")
print("Comparing p=0.0 vs p=0.5 with error bars...")

L = 200
N_values = range(10, 151, 10)
n_runs = 20  # Use 20 runs per density point (can reduce to 10 if runtime is an issue)

# Run for p=0.0
print("Running simulations for p=0.0...")
densities_p0, flows_p0, std_p0, sem_p0 = fundamental_diagram_with_errors(
    L, v_max=5, p=0.0, N_values=N_values, n_runs=n_runs, warmup=200, measure_steps=500
)

# Run for p=0.5
print("Running simulations for p=0.5...")
densities_p5, flows_p5, std_p5, sem_p5 = fundamental_diagram_with_errors(
    L, v_max=5, p=0.5, N_values=N_values, n_runs=n_runs, warmup=200, measure_steps=500
)

# Plot fundamental diagrams with error bars
fig, ax = plt.subplots(figsize=(10, 6))

# Plot with error bars (using SEM for error bars)
ax.errorbar(densities_p0, flows_p0, yerr=sem_p0, fmt='o-', color='blue', 
            label='p=0.0 (deterministic)', capsize=5, capthick=2, markersize=6)
ax.errorbar(densities_p5, flows_p5, yerr=sem_p5, fmt='s-', color='red', 
            label='p=0.5 (stochastic)', capsize=5, capthick=2, markersize=6)

ax.set_xlabel('Density (ρ = N/L)', fontsize=12)
ax.set_ylabel('Flow (J)', fontsize=12)
ax.set_title('Investigation 2: Effect of Randomization\nFundamental Diagram with Error Bars (SEM)', fontsize=14)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('images/investigation_2_fundamental_diagram_with_errors.png', dpi=300, bbox_inches='tight')
plt.show()

print(f"✓ Investigation 2 complete (n={n_runs} runs per density)")
print(f"  Note: p=0.0 has very small error bars (deterministic)")
print(f"  Note: p=0.5 shows larger variability due to stochasticity")


# ============================================================================
# Investigation 3 - Effect of Speed Limit WITH ERROR BARS
# ============================================================================

print("\n--- Running Investigation 3 with Error Analysis ---")
print("Comparing v_max=5 vs v_max=2 with error bars...")

p_fixed = 0.5  # Use stochastic model

# Run for v_max=5
print("Running simulations for v_max=5...")
densities_v5, flows_v5, std_v5, sem_v5 = fundamental_diagram_with_errors(
    L, v_max=5, p=p_fixed, N_values=N_values, n_runs=n_runs, warmup=200, measure_steps=500
)

# Run for v_max=2
print("Running simulations for v_max=2...")
densities_v2, flows_v2, std_v2, sem_v2 = fundamental_diagram_with_errors(
    L, v_max=2, p=p_fixed, N_values=N_values, n_runs=n_runs, warmup=200, measure_steps=500
)

# Plot fundamental diagrams with error bars
fig, ax = plt.subplots(figsize=(10, 6))

# Plot with error bars (using SEM)
ax.errorbar(densities_v5, flows_v5, yerr=sem_v5, fmt='o-', color='green', 
            label='v_max=5', capsize=5, capthick=2, markersize=6)
ax.errorbar(densities_v2, flows_v2, yerr=sem_v2, fmt='s-', color='orange', 
            label='v_max=2', capsize=5, capthick=2, markersize=6)

ax.set_xlabel('Density (ρ = N/L)', fontsize=12)
ax.set_ylabel('Flow (J)', fontsize=12)
ax.set_title(f'Investigation 3: Effect of Maximum Speed\nFundamental Diagram with Error Bars (p={p_fixed}, SEM)', fontsize=14)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('images/investigation_3_fundamental_diagram_with_errors.png', dpi=300, bbox_inches='tight')
plt.show()

print(f"✓ Investigation 3 complete (n={n_runs} runs per density)")
print(f"  Analysis: Check if curves are separated beyond uncertainty at low density")
print(f"  Analysis: Check if curves overlap within uncertainty at high density")
