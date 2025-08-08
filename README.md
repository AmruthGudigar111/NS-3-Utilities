# NS-3 Utilities 🛠️

A collection of tools to simplify and enhance post-simulation analysis in the [NS-3 Network Simulator](https://www.nsnam.org/). This project includes utilities for trace file parsing, flow monitor analysis, and scenario visualization.

## 📦 Components

### 1. Trace File Analyzer
- Parses NS-3 trace files (`.tr`) to extract key performance metrics.
- Supports analysis of packet drops, delays, throughput, and more.
- Outputs structured summaries for easier interpretation.

### 2. Flow Monitor Analyzer
- Works with NS-3’s FlowMonitor module to analyze flow-level statistics.
- Tracks:
  - Packet transmission and reception
  - End-to-end delay and jitter
  - Byte and packet counts per flow
- Useful for evaluating protocol efficiency and network behavior.

### 3. Scenario Viewer
- Visualizes simulation scenarios including:
  - Node placement
  - Network topology
- Helps users understand and debug simulation setups.

## 🚀 Getting Started

### Prerequisites
- NS-3 installed and configured
- Python 3.x (for analyzer scripts)
- Matplotlib or other visualization libraries (optional, for scenario viewer)

### Installation
Clone the repository:
```bash
git clone https://github.com/AmruthGudigar111/NS-3-Utilities.git
cd NS-3-Utilities
