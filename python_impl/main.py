import numpy as np
import time
import argparse
import matplotlib.pyplot as plt
import os

# States
EMPTY = 0
TREE = 1
FIRE = 2

def initialize_grid(size, density):
    grid = np.random.choice([TREE, EMPTY], size=(size, size), p=[density, 1-density])
    # Ignite center
    grid[size//2, size//2] = FIRE
    return grid

def update_grid(grid):
    # Vectorized update
    
    # Identify masks
    burning_mask = (grid == FIRE)
    tree_mask = (grid == TREE)
    
    # Next state base: Trees stay trees, Holes stay holes, Fire becomes holes
    next_grid = grid.copy()
    next_grid[burning_mask] = EMPTY # Fire burns out
    
    # Fire propagation
    # Shift grid to check neighbors (Up, Down, Left, Right) - von Neumann neighborhood
    # Shifted arrays (padding with 0/Empty)
    
    # Neighbors that are burning
    fire_neighbors = np.zeros_like(grid, dtype=bool)
    
    # Up
    fire_neighbors[:-1, :] |= (grid[1:, :] == FIRE)
    # Down
    fire_neighbors[1:, :] |= (grid[:-1, :] == FIRE)
    # Left
    fire_neighbors[:, :-1] |= (grid[:, 1:] == FIRE)
    # Right
    fire_neighbors[:, 1:] |= (grid[:, :-1] == FIRE)
    
    # Trees catches fire if neighbor is burning
    igniting_mask = tree_mask & fire_neighbors
    next_grid[igniting_mask] = FIRE
    
    return next_grid

def save_snapshot(grid, step, output_dir):
    plt.figure(figsize=(10, 10))
    # Custom colormap: 0=Black(Empty), 1=Green(Tree), 2=Red(Fire)
    cmap = plt.cm.colors.ListedColormap(['black', 'forestgreen', 'red'])
    bounds = [0, 0.5, 1.5, 2.5]
    norm = plt.cm.colors.BoundaryNorm(bounds, cmap.N)
    
    plt.imshow(grid, cmap=cmap, norm=norm, interpolation='nearest')
    plt.title(f"Step {step}")
    plt.axis('off')
    
    filename = os.path.join(output_dir, f"step_{step:04d}.png")
    plt.savefig(filename, bbox_inches='tight')
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="Fire Simulation in Python")
    parser.add_argument("--size", type=int, default=1000, help="Grid size")
    parser.add_argument("--steps", type=int, default=100, help="Number of steps")
    parser.add_argument("--density", type=float, default=0.6, help="Tree density")
    parser.add_argument("--append-to", type=str, help="Append result to CSV file")
    parser.add_argument("--snapshot-dir", type=str, help="Directory to save snapshots")
    parser.add_argument("--snapshot-interval", type=int, default=10, help="Interval for snapshots")
    
    args = parser.parse_args()
    
    print(f"Initializing Grid: {args.size}x{args.size}")
    grid = initialize_grid(args.size, args.density)
    
    if args.snapshot_dir:
        if not os.path.exists(args.snapshot_dir):
            os.makedirs(args.snapshot_dir)
        save_snapshot(grid, 0, args.snapshot_dir)

    start_time = time.time()
    
    for i in range(args.steps):
        grid = update_grid(grid)
        if args.snapshot_dir and (i + 1) % args.snapshot_interval == 0:
            save_snapshot(grid, i + 1, args.snapshot_dir)
        
    duration = time.time() - start_time
    print(f"Simulation completed in: {duration:.4f} seconds")
    print(f"Time per step: {duration/args.steps:.6f} seconds")

    if args.append_to:
        with open(args.append_to, "a") as f:
            f.write(f"Python,{args.size},{args.steps},{duration:.6f}\n")

if __name__ == "__main__":
    main()
