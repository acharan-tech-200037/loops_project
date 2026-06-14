"""
IR Drop Simulator — Core Engine
================================
Models a chip power grid as a 2D resistor network.
Uses iterative Gauss-Seidel relaxation to solve node voltages.

Physical Design concepts covered:
  - Power grid modeling
  - IR Drop = VDD - V(node)
  - Iterative convergence (like SPICE solvers)
  - Hotspot / violation detection
"""

import numpy as np


def build_current_map(grid_size, load_positions, load_current):
    current_map = np.zeros((grid_size, grid_size))
    for (r, c) in load_positions:
        if 0 <= r < grid_size and 0 <= c < grid_size:
            current_map[r, c] = load_current
    return current_map


def run_ir_drop_simulation(
    grid_size,
    resistance,
    vdd,
    current_map,
    vdd_pins,
    max_iterations=5000,
    convergence_threshold=1e-6,
):
    """
    Solve node voltages using iterative Gauss-Seidel relaxation.

    Algorithm:
      1. Initialize all nodes to VDD
      2. Clamp VDD pin nodes to VDD (fixed boundary condition)
      3. WHILE loop: iterate until convergence
           FOR each row:
             FOR each col:
               - Skip VDD pins (they are fixed)
               - Collect valid neighbors (up, down, left, right)
               - New voltage = average of neighbors - I*R drop
      4. Check convergence: max(|V_new - V_old|) < threshold -> break
      5. Compute IR drop map and flag violations
    """

    # Step 1: Initialize voltage grid to VDD
    voltage = np.full((grid_size, grid_size), vdd, dtype=np.float64)

    # VDD pin mask
    vdd_mask = np.zeros((grid_size, grid_size), dtype=bool)
    for (r, c) in vdd_pins:
        if 0 <= r < grid_size and 0 <= c < grid_size:
            vdd_mask[r, c] = True
            voltage[r, c] = vdd

    iterations_run = 0
    converged = False
    convergence_history = []

    # Step 2: OUTER WHILE LOOP — runs until convergence
    for iteration in range(max_iterations):
        voltage_old = voltage.copy()

        # Step 3: NESTED FOR LOOPS — sweep every grid node
        for row in range(grid_size):
            for col in range(grid_size):

                # Skip VDD pins — their voltage is fixed
                if vdd_mask[row, col]:
                    continue

                # Collect neighbor voltages (up, down, left, right)
                neighbors = []
                if row > 0:
                    neighbors.append(voltage[row - 1, col])
                if row < grid_size - 1:
                    neighbors.append(voltage[row + 1, col])
                if col > 0:
                    neighbors.append(voltage[row, col - 1])
                if col < grid_size - 1:
                    neighbors.append(voltage[row, col + 1])

                if not neighbors:
                    continue

                # New voltage = average of neighbors - local IR drop
                avg_neighbor_voltage = sum(neighbors) / len(neighbors)
                local_ir_drop = current_map[row, col] * resistance
                voltage[row, col] = max(0.0, avg_neighbor_voltage - local_ir_drop)

        iterations_run += 1

        # Step 4: CONVERGENCE CHECK
        delta = float(np.max(np.abs(voltage - voltage_old)))
        convergence_history.append(delta)

        if delta < convergence_threshold:
            converged = True
            break

    # Step 5: Compute IR Drop map
    ir_drop_map = vdd - voltage

    # Violation detection using list comprehension
    violation_threshold = 0.1 * vdd
    violation_nodes = [
        (r, c)
        for r in range(grid_size)
        for c in range(grid_size)
        if ir_drop_map[r, c] > violation_threshold
    ]

    stats = {
        "max_ir_drop"        : float(np.max(ir_drop_map)),
        "avg_ir_drop"        : float(np.mean(ir_drop_map)),
        "min_voltage"        : float(np.min(voltage)),
        "max_voltage"        : float(np.max(voltage)),
        "violation_count"    : len(violation_nodes),
        "violation_nodes"    : violation_nodes,
        "violation_threshold": violation_threshold,
        "total_nodes"        : grid_size * grid_size,
        "violation_percent"  : 100.0 * len(violation_nodes) / (grid_size * grid_size),
    }

    return {
        "voltage_map"         : voltage,
        "ir_drop_map"         : ir_drop_map,
        "iterations"          : iterations_run,
        "converged"           : converged,
        "vdd_mask"            : vdd_mask,
        "stats"               : stats,
        "convergence_history" : convergence_history,
    }


def generate_load_positions(grid_size, num_loads, seed=42):
    """Randomly place standard cell loads on the grid."""
    rng = np.random.default_rng(seed)
    positions = set()
    corners = {(0, 0), (0, grid_size - 1), (grid_size - 1, 0), (grid_size - 1, grid_size - 1)}
    attempts = 0
    while len(positions) < num_loads and attempts < num_loads * 10:
        r = int(rng.integers(1, grid_size - 1))
        c = int(rng.integers(1, grid_size - 1))
        if (r, c) not in corners:
            positions.add((r, c))
        attempts += 1
    return list(positions)


def get_vdd_pin_positions(grid_size, pin_style="corners"):
    """Return VDD pin positions based on layout style."""
    mid = grid_size // 2
    pins = []

    if pin_style == "Corners only":
        pins = [(0,0),(0,grid_size-1),(grid_size-1,0),(grid_size-1,grid_size-1)]

    elif pin_style == "Full ring (border)":
        for c in range(grid_size):
            pins.append((0, c))
            pins.append((grid_size - 1, c))
        for r in range(1, grid_size - 1):
            pins.append((r, 0))
            pins.append((r, grid_size - 1))

    elif pin_style == "Center cross + corners":
        pins = [(0,0),(0,grid_size-1),(grid_size-1,0),(grid_size-1,grid_size-1)]
        for i in range(grid_size):
            pins.append((mid, i))
            pins.append((i, mid))

    return list(set(pins))