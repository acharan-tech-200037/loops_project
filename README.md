# ⚡ IR Drop Simulator

An interactive power grid IR drop analysis tool built with Streamlit, demonstrating physical design concepts and iterative solvers in Python.

## 📋 Overview

This tool simulates voltage drops (IR drops) across a power grid network using a Gauss-Seidel iterative solver. It helps visualize how current loads affect voltage distribution and identifies potential violations where voltage drops exceed 10% of VDD.

## 🎯 Features

- **Interactive Grid Configuration**: Adjust grid size, number of loads, and VDD pin placement
- **Real-time Simulation**: Run Gauss-Seidel solver with configurable convergence parameters
- **Visual Analytics**:
  - IR Drop Heatmap
  - Voltage Distribution Map
  - Current Load Map
  - Convergence History Plot
  - IR Drop Histogram
- **Violation Detection**: Identifies nodes exceeding 10% VDD drop
- **Multiple VDD Pin Layouts**:
  - Corners only
  - Full ring (border)
  - Center cross + corners

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git

### Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/acharan-tech-200037/loops_project.git

# 2. Navigate to project directory
cd loops_project

# 3. Create virtual environment
python -m venv .venv

# 4. Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt
