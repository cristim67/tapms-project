# Fire Simulation - Go Implementation

This directory contains the Go implementation using **Goroutines** and **Channels/WaitGroups**. It demonstrates how Go's concurrency model can be applied to grid-based simulations.

## 🚀 Quick Start

### Prerequisites
- **Go 1.20+**: Install from [go.dev](https://go.dev/dl/).

### Build & Run

1. **Build**:
   ```bash
   go build -o fire_simulation_go main.go
   ```

2. **Run**:
   ```bash
   # Run with default settings
   ./fire_simulation_go

   # Run with custom parameters
   ./fire_simulation_go -size 1500 -steps 200
   ```

## 🛠 Implementation Details
- **Parallelism**: The grid is split into horizontal chunks. Each chunk is processed by a separate worker Goroutine.
- **Synchronization**: A `sync.WaitGroup` is used to ensure all workers finish a step before the next iteration begins.
