"""
IR Drop Simulator — Streamlit UI
==================================
Interactive power grid IR drop analysis tool.
Built to demonstrate Python loops + Physical Design concepts.
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.ticker as ticker

from simulator import (
    run_ir_drop_simulation,
    build_current_map,
    generate_load_positions,
    get_vdd_pin_positions,
)

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="IR Drop Simulator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }

  /* Header banner */
  .ir-header {
    background: linear-gradient(135deg, #0f0c29, #1a1a2e, #16213e);
    border-radius: 12px;
    padding: 28px 32px 20px;
    margin-bottom: 24px;
    border: 1px solid #2a2a4a;
  }
  .ir-header h1 {
    font-family: 'JetBrains Mono', monospace;
    color: #e8ff7a;
    font-size: 28px;
    font-weight: 600;
    margin: 0 0 4px 0;
    letter-spacing: -0.5px;
  }
  .ir-header p {
    color: #8888aa;
    font-size: 14px;
    margin: 0;
  }

  /* Metric cards */
  .metric-card {
    background: #0f0c29;
    border: 1px solid #2a2a4a;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 10px;
  }
  .metric-label {
    font-size: 11px;
    color: #6666aa;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-family: 'JetBrains Mono', monospace;
  }
  .metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 22px;
    font-weight: 600;
    color: #e8ff7a;
    margin-top: 4px;
  }
  .metric-value.danger { color: #ff6b6b; }
  .metric-value.safe   { color: #6bffb8; }

  /* Status badge */
  .badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    letter-spacing: 0.5px;
  }
  .badge-converged  { background: #1a3a2a; color: #6bffb8; border: 1px solid #2a6a4a; }
  .badge-diverged   { background: #3a1a1a; color: #ff6b6b; border: 1px solid #6a2a2a; }
  .badge-violation  { background: #3a1a1a; color: #ff6b6b; border: 1px solid #6a2a2a; }
  .badge-clean      { background: #1a3a2a; color: #6bffb8; border: 1px solid #2a6a4a; }

  /* Section heading */
  .section-heading {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #6666aa;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 20px 0 10px;
    padding-bottom: 6px;
    border-bottom: 1px solid #2a2a4a;
  }

  /* Loop info box */
  .loop-box {
    background: #0a0a1a;
    border-left: 3px solid #e8ff7a;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin: 10px 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #aaaacc;
    line-height: 1.8;
  }
  .loop-box .kw  { color: #e8ff7a; }
  .loop-box .fn  { color: #79c0ff; }
  .loop-box .cm  { color: #4a4a6a; }

  /* Violation table */
  .vtable {
    width: 100%;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    border-collapse: collapse;
  }
  .vtable th {
    background: #1a1a2e;
    color: #6666aa;
    padding: 6px 10px;
    text-align: left;
    font-size: 11px;
    letter-spacing: 0.5px;
  }
  .vtable td {
    color: #ccccee;
    padding: 5px 10px;
    border-bottom: 1px solid #1a1a2e;
  }
  .vtable tr:hover td { background: #1a1a2e; }

  /* Sidebar styling */
  [data-testid="stSidebar"] {
    background: #0a0a18 !important;
  }
  [data-testid="stSidebar"] label {
    color: #8888aa !important;
    font-size: 13px !important;
  }

  /* Run button */
  div.stButton > button {
    background: linear-gradient(135deg, #e8ff7a, #a8ef3a);
    color: #0a0a1a;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    font-size: 14px;
    border: none;
    border-radius: 8px;
    padding: 12px 0;
    width: 100%;
    letter-spacing: 0.5px;
    cursor: pointer;
    transition: opacity 0.2s;
  }
  div.stButton > button:hover { opacity: 0.85; }

  /* Hide default streamlit elements */
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }
  header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown("""
<div class="ir-header">
  <h1>⚡ IR Drop Simulator</h1>
  <p>Power grid voltage analysis · Gauss-Seidel iterative solver · Physical Design</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Sidebar — Controls
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-heading">Grid Configuration</div>', unsafe_allow_html=True)
    grid_size   = st.slider("Grid size (N×N)", 8, 40, 20, 1)
    num_loads   = st.slider("Number of load cells", 5, grid_size * grid_size // 4, min(20, grid_size * grid_size // 5), 1)
    random_seed = st.slider("Random seed", 0, 99, 42, 1)

    st.markdown('<div class="section-heading">Electrical Parameters</div>', unsafe_allow_html=True)
    vdd        = st.slider("VDD supply voltage (V)", 0.5, 1.8, 1.0, 0.05)
    resistance = st.slider("Wire resistance per segment (Ω)", 0.01, 2.0, 0.5, 0.01)
    load_ma    = st.slider("Current per cell load (mA)", 1, 100, 20, 1)
    load_current = load_ma / 1000.0   # convert to Amps

    st.markdown('<div class="section-heading">VDD Pin Placement</div>', unsafe_allow_html=True)
    pin_style = st.selectbox(
        "VDD pin layout",
        ["Corners only", "Full ring (border)", "Center cross + corners"],
        index=0,
    )

    st.markdown('<div class="section-heading">Solver Settings</div>', unsafe_allow_html=True)
    max_iter  = st.slider("Max iterations", 500, 10000, 3000, 100)
    conv_thr  = st.select_slider(
        "Convergence threshold",
        options=[1e-3, 1e-4, 1e-5, 1e-6, 1e-7],
        value=1e-6,
        format_func=lambda x: f"{x:.0e}",
    )

    st.markdown("")
    run_btn = st.button("▶  Run Simulation")


# ─────────────────────────────────────────────
# Run simulation
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def cached_simulate(grid_size, resistance, vdd, num_loads, load_current, pin_style, max_iter, conv_thr, seed):
    load_positions = generate_load_positions(grid_size, num_loads, seed=seed)
    vdd_pins       = get_vdd_pin_positions(grid_size, pin_style)
    current_map    = build_current_map(grid_size, load_positions, load_current)
    result         = run_ir_drop_simulation(
        grid_size=grid_size,
        resistance=resistance,
        vdd=vdd,
        current_map=current_map,
        vdd_pins=vdd_pins,
        max_iterations=max_iter,
        convergence_threshold=conv_thr,
    )
    return result, load_positions, vdd_pins, current_map


if "result" not in st.session_state or run_btn:
    with st.spinner("⚙️  Solving power grid..."):
        result, load_positions, vdd_pins, current_map = cached_simulate(
            grid_size, resistance, vdd, num_loads, load_current,
            pin_style, max_iter, conv_thr, random_seed
        )
    st.session_state.result         = result
    st.session_state.load_positions = load_positions
    st.session_state.vdd_pins       = vdd_pins
    st.session_state.current_map    = current_map

result         = st.session_state.result
load_positions = st.session_state.load_positions
vdd_pins       = st.session_state.vdd_pins
current_map    = st.session_state.current_map
stats          = result["stats"]


# ─────────────────────────────────────────────
# Top metric row
# ─────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Max IR Drop</div>
      <div class="metric-value {'danger' if stats['max_ir_drop'] > stats['violation_threshold'] else 'safe'}">
        {stats['max_ir_drop']*1000:.1f} mV
      </div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Avg IR Drop</div>
      <div class="metric-value">{stats['avg_ir_drop']*1000:.2f} mV</div>
    </div>""", unsafe_allow_html=True)

with col3:
    vclass = "danger" if stats["violation_count"] > 0 else "safe"
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Violations</div>
      <div class="metric-value {vclass}">{stats['violation_count']}</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Min Voltage</div>
      <div class="metric-value">{stats['min_voltage']:.4f} V</div>
    </div>""", unsafe_allow_html=True)

with col5:
    conv_badge = '<span class="badge badge-converged">✓ CONVERGED</span>' if result["converged"] else '<span class="badge badge-diverged">✗ NOT CONVERGED</span>'
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Solver Status</div>
      <div style="margin-top:8px">{conv_badge}</div>
      <div style="color:#6666aa;font-size:12px;margin-top:6px;font-family:monospace">{result['iterations']} iterations</div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Custom colormaps
# ─────────────────────────────────────────────
ir_cmap    = LinearSegmentedColormap.from_list("ir", ["#0a1628","#1a3a5a","#2a6a3a","#e8c23a","#e85a2a","#ff2222"])
volt_cmap  = LinearSegmentedColormap.from_list("volt", ["#ff2222","#e85a2a","#e8c23a","#2a6a3a","#1a3a8a","#0a1628"])
curr_cmap  = LinearSegmentedColormap.from_list("curr", ["#0a1628","#1a2a4a","#2a3a8a","#4a6aff","#aaccff"])


# ─────────────────────────────────────────────
# Main plots — row 1
# ─────────────────────────────────────────────
st.markdown('<div class="section-heading">Power Grid Analysis</div>', unsafe_allow_html=True)

fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
fig.patch.set_facecolor("#080814")

def style_ax(ax, title):
    ax.set_facecolor("#080814")
    ax.set_title(title, color="#aaaacc", fontsize=12, pad=10, fontfamily="monospace")
    ax.tick_params(colors="#444466", labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor("#2a2a4a")

# — Plot 1: IR Drop Heatmap —
ax = axes[0]
im = ax.imshow(result["ir_drop_map"] * 1000, cmap=ir_cmap, interpolation="bilinear", aspect="equal")
style_ax(ax, "IR Drop Map (mV)")
cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.ax.yaxis.set_tick_params(color="#444466")
cbar.ax.tick_params(labelsize=8, colors="#aaaacc")
cbar.set_label("IR Drop (mV)", color="#6666aa", fontsize=9)

# Overlay VDD pins
for (r, c) in vdd_pins:
    ax.plot(c, r, "s", color="#e8ff7a", markersize=4, alpha=0.9)

# Overlay violation nodes
for (r, c) in stats["violation_nodes"]:
    ax.plot(c, r, "x", color="#ff4444", markersize=5, markeredgewidth=1.5, alpha=0.8)

# Legend
vdd_patch  = mpatches.Patch(color="#e8ff7a", label="VDD pins")
viol_patch = mpatches.Patch(color="#ff4444", label="Violations")
ax.legend(handles=[vdd_patch, viol_patch], loc="lower right", fontsize=8,
          framealpha=0.5, facecolor="#0a0a1a", edgecolor="#2a2a4a", labelcolor="#ccccee")

# — Plot 2: Voltage Map —
ax = axes[1]
im2 = ax.imshow(result["voltage_map"], cmap=volt_cmap, interpolation="bilinear",
                aspect="equal", vmin=0, vmax=vdd)
style_ax(ax, f"Voltage Map (V)  [VDD = {vdd}V]")
cbar2 = fig.colorbar(im2, ax=ax, fraction=0.046, pad=0.04)
cbar2.ax.tick_params(labelsize=8, colors="#aaaacc")
cbar2.set_label("Voltage (V)", color="#6666aa", fontsize=9)

# Contour lines
try:
    cs = ax.contour(result["voltage_map"], levels=6, colors="#ffffff", alpha=0.15, linewidths=0.5)
    ax.clabel(cs, inline=True, fontsize=7, colors="#aaaacc", fmt="%.3f")
except Exception:
    pass

# — Plot 3: Current Load Map —
ax = axes[2]
im3 = ax.imshow(current_map * 1000, cmap=curr_cmap, interpolation="nearest",
                aspect="equal")
style_ax(ax, "Current Load Map (mA)")
cbar3 = fig.colorbar(im3, ax=ax, fraction=0.046, pad=0.04)
cbar3.ax.tick_params(labelsize=8, colors="#aaaacc")
cbar3.set_label("Current (mA)", color="#6666aa", fontsize=9)

for (r, c) in load_positions:
    ax.plot(c, r, "o", color="#79c0ff", markersize=5, alpha=0.9)
for (r, c) in vdd_pins:
    ax.plot(c, r, "s", color="#e8ff7a", markersize=4, alpha=0.9)

plt.tight_layout(pad=2.0)
st.pyplot(fig)
plt.close(fig)


# ─────────────────────────────────────────────
# Second row: Convergence + Violation + Loop Info
# ─────────────────────────────────────────────
col_a, col_b, col_c = st.columns([2, 1.5, 1.5])

with col_a:
    st.markdown('<div class="section-heading">Convergence History</div>', unsafe_allow_html=True)
    history = result["convergence_history"]
    if history:
        fig2, ax2 = plt.subplots(figsize=(6, 3))
        fig2.patch.set_facecolor("#080814")
        ax2.set_facecolor("#080814")
        ax2.plot(range(1, len(history)+1), history, color="#e8ff7a", linewidth=1.5)
        ax2.axhline(y=conv_thr, color="#ff6b6b", linewidth=1, linestyle="--", label=f"threshold={conv_thr:.0e}")
        ax2.set_yscale("log")
        ax2.set_xlabel("Iteration", color="#6666aa", fontsize=10)
        ax2.set_ylabel("Max |ΔV|", color="#6666aa", fontsize=10)
        ax2.tick_params(colors="#444466", labelsize=8)
        ax2.legend(fontsize=8, framealpha=0.5, facecolor="#0a0a1a",
                   edgecolor="#2a2a4a", labelcolor="#ccccee")
        for spine in ax2.spines.values():
            spine.set_edgecolor("#2a2a4a")
        ax2.fill_between(range(1, len(history)+1), history, alpha=0.1, color="#e8ff7a")
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

with col_b:
    st.markdown('<div class="section-heading">Violation Nodes</div>', unsafe_allow_html=True)
    viol_nodes = stats["violation_nodes"]
    if not viol_nodes:
        st.markdown('<span class="badge badge-clean">✓ No violations found</span>', unsafe_allow_html=True)
        st.markdown(f"<p style='color:#6666aa;font-size:13px;margin-top:12px'>All nodes within {stats['violation_threshold']*1000:.0f} mV of VDD</p>", unsafe_allow_html=True)
    else:
        pct = stats["violation_percent"]
        st.markdown(f'<span class="badge badge-violation">⚠ {len(viol_nodes)} violations ({pct:.1f}%)</span>', unsafe_allow_html=True)
        
        # Show top 10 worst violations
        ir_map = result["ir_drop_map"]
        sorted_viols = sorted(viol_nodes, key=lambda rc: ir_map[rc[0], rc[1]], reverse=True)[:10]
        
        rows_html = "".join([
            f"<tr><td>({r},{c})</td><td style='color:#ff6b6b'>{ir_map[r,c]*1000:.2f}</td><td>{result['voltage_map'][r,c]:.4f}</td></tr>"
            for r, c in sorted_viols
        ])
        st.markdown(f"""
        <table class="vtable">
          <thead><tr><th>Node (r,c)</th><th>IR Drop (mV)</th><th>Voltage (V)</th></tr></thead>
          <tbody>{rows_html}</tbody>
        </table>
        """, unsafe_allow_html=True)
        if len(viol_nodes) > 10:
            st.caption(f"Showing top 10 of {len(viol_nodes)} violations")

with col_c:
    st.markdown('<div class="section-heading">Python Loops Used</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="loop-box">
      <span class="cm"># Outer convergence loop</span><br>
      <span class="kw">for</span> iteration <span class="kw">in</span> <span class="fn">range</span>(max_iter):<br>
      &nbsp;&nbsp;voltage_old = voltage.<span class="fn">copy</span>()<br><br>
      &nbsp;&nbsp;<span class="cm"># Nested node sweep</span><br>
      &nbsp;&nbsp;<span class="kw">for</span> row <span class="kw">in</span> <span class="fn">range</span>(N):<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<span class="kw">for</span> col <span class="kw">in</span> <span class="fn">range</span>(N):<br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;V[r,c] = avg(neighbors)<br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; - I×R<br><br>
      &nbsp;&nbsp;<span class="cm"># Convergence check</span><br>
      &nbsp;&nbsp;<span class="kw">if</span> delta &lt; threshold:<br>
      &nbsp;&nbsp;&nbsp;&nbsp;<span class="kw">break</span> <span class="cm"># done!</span><br><br>
      <span class="cm"># Violation filter</span><br>
      viols = [<span class="fn">...</span> <span class="kw">for</span> r,c<br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <span class="kw">if</span> drop &gt; 10%VDD]
    </div>
    <div style="margin-top:14px">
      <div style="color:#6666aa;font-size:11px;font-family:monospace;margin-bottom:6px">LOOP STATS</div>
      <div style="color:#aaaacc;font-size:12px;font-family:monospace;line-height:2">
        Iterations run: <span style="color:#e8ff7a">{result['iterations']}</span><br>
        Nodes per pass: <span style="color:#e8ff7a">{grid_size}×{grid_size} = {grid_size*grid_size}</span><br>
        Total ops: <span style="color:#e8ff7a">{result['iterations'] * grid_size * grid_size:,}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Bottom: IR drop histogram
# ─────────────────────────────────────────────
st.markdown('<div class="section-heading">IR Drop Distribution</div>', unsafe_allow_html=True)
fig3, ax3 = plt.subplots(figsize=(14, 3))
fig3.patch.set_facecolor("#080814")
ax3.set_facecolor("#080814")

ir_vals = result["ir_drop_map"].flatten() * 1000  # in mV
viol_thr_mv = stats["violation_threshold"] * 1000

safe_vals = ir_vals[ir_vals <= viol_thr_mv]
viol_vals = ir_vals[ir_vals > viol_thr_mv]

bins = np.linspace(ir_vals.min(), ir_vals.max(), 50)
ax3.hist(safe_vals, bins=bins, color="#2a8a4a", alpha=0.85, label="Safe nodes", edgecolor="#0a0a1a", linewidth=0.3)
ax3.hist(viol_vals, bins=bins, color="#e84a2a", alpha=0.85, label="Violation nodes", edgecolor="#0a0a1a", linewidth=0.3)
ax3.axvline(x=viol_thr_mv, color="#e8ff7a", linewidth=1.5, linestyle="--", label=f"Threshold ({viol_thr_mv:.0f} mV = 10% VDD)")

ax3.set_xlabel("IR Drop (mV)", color="#6666aa", fontsize=10)
ax3.set_ylabel("Node count", color="#6666aa", fontsize=10)
ax3.tick_params(colors="#444466", labelsize=9)
ax3.legend(fontsize=9, framealpha=0.5, facecolor="#0a0a1a", edgecolor="#2a2a4a", labelcolor="#ccccee")
for spine in ax3.spines.values():
    spine.set_edgecolor("#2a2a4a")

plt.tight_layout()
st.pyplot(fig3)
plt.close(fig3)

# Footer
st.markdown("""
<div style="margin-top:32px;padding-top:16px;border-top:1px solid #1a1a2e;
            color:#3a3a5a;font-size:11px;font-family:monospace;text-align:center">
  IR Drop Simulator · Physical Design · Python Loops Demo
  · Gauss-Seidel Iterative Solver · NumPy + Matplotlib + Streamlit
</div>
""", unsafe_allow_html=True)