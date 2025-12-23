# Fire Simulation - Rust Implementation

This directory contains the Rust implementation of the fire propagation simulation. It uses `rayon` for data parallelism to achieve high performance on multi-core processors.

## 🚀 Quick Start

### Prerequisites
- **Rust**: Install via [rustup.rs](https://rustup.rs).
  ```bash
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
  source $HOME/.cargo/env
  ```

### Build & Run
The project is configured to run with `cargo`. For benchmarks, always use the `--release` flag.

1. **Build**:
   ```bash
   cargo build --release
   ```

2. **Run**:
   ```bash
   # Run with default settings (1000x1000 grid, 100 steps)
   cargo run --release

   # Run with custom parameters
   cargo run --release -- --size 2000 --steps 500 --density 0.7
   ```

## 🛠 Project Structure
- `src/main.rs`: Source code containing the `Simulation` struct and parallel update logic.
- `Cargo.toml`: Configuration and dependencies (`rayon`, `rand`, `clap`).
