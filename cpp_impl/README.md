# Fire Propagation Simulation - C++ Implementation

This directory contains a high-performance C++ implementation of the fire propagation simulation. It utilizes the STL `<thread>` library for manual thread management, avoiding the overhead of external runtimes while providing maximum control over execution.

## Prerequisites

- **G++ Compiler**: Must support C++17 (e.g., GCC 7+ or Clang 5+).
- **Make** (Optional, but command is simple enough to run directly).

## Build Instructions

Compile with optimization level 3 (`-O3`) and threading support (`-pthread`):

```bash
g++ -O3 -std=c++17 -pthread main.cpp -o fire_simulation_cpp
```

## Running the Simulation

Run the compiled binary. You can specify parameters via command-line flags (simulated):

```bash
./fire_simulation_cpp --size 1000 --steps 100
```

### Arguments (Positional simulation)
- `--size [N]`: Sets the grid size to NxN (default: 100).
- `--steps [N]`: Sets the number of simulation steps (default: 100).
- `--append-to [FILE]`: Appends the execution time to a CSV file.

## Implementation Details

- **Paradigm**: Manual Multi-Threading (`std::thread`).
- **Memory**: Vectors of `uint8_t` for cache efficiency. Double-buffering is used to avoid race conditions and eliminate the need for mutexes in the core loop.
- **Optimization**: The grid is partitioned into chunks, with each thread processing a distinct range of rows. This "Domain Decomposition" strategy scales linearly with the number of physical cores.
