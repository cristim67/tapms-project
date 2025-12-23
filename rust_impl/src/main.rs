use clap::Parser;
use rand::Rng;
use rayon::prelude::*;
use std::time::Instant;

#[derive(Clone, Copy, PartialEq, Eq)]
enum CellState {
    Empty = 0,
    Tree = 1,
    Fire = 2,
}

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    #[arg(short, long, default_value_t = 1000)]
    size: usize,

    #[arg(short, long, default_value_t = 100)]
    steps: usize,

    #[arg(short, long, default_value_t = 0.6)]
    density: f64,

    #[arg(long)]
    append_to: Option<String>,
}

struct Simulation {
    grid: Vec<CellState>,
    size: usize,
}

impl Simulation {
    fn new(size: usize, density: f64) -> Self {
        let mut rng = rand::thread_rng();
        let mut grid = Vec::with_capacity(size * size);

        for _ in 0..size * size {
            let r: f64 = rng.gen();
            if r < density {
                grid.push(CellState::Tree);
            } else {
                grid.push(CellState::Empty);
            }
        }
        
        // Ignite the center
        grid[size * size / 2 + size / 2] = CellState::Fire;

        Simulation { grid, size }
    }

    fn get_index(&self, r: usize, c: usize) -> usize {
        r * self.size + c
    }

    // Parallel update step
    fn step_parallel(&self) -> Vec<CellState> {
        let size = self.size;
        
        // We use par_iter to iterate over indices in parallel
        (0..size * size).into_par_iter().map(|idx| {
            let r = idx / size;
            let c = idx % size;

            match self.grid[idx] {
                CellState::Fire => CellState::Empty, // Fire burns out
                CellState::Empty => CellState::Empty, // Remains empty
                CellState::Tree => {
                    // Check neighbors for fire
                    let mut on_fire = false;
                    
                    // Neighbors: Up, Down, Left, Right
                    let neighbors = [
                        (r.wrapping_sub(1), c),
                        (r.wrapping_add(1), c),
                        (r, c.wrapping_sub(1)),
                        (r, c.wrapping_add(1)),
                    ];

                    for (nr, nc) in neighbors {
                        if nr < size && nc < size {
                            if self.grid[nr * size + nc] == CellState::Fire {
                                on_fire = true;
                                break;
                            }
                        }
                    }

                    if on_fire {
                        CellState::Fire
                    } else {
                        CellState::Tree
                    }
                }
            }
        }).collect()
    }
}

fn main() {
    let args = Args::parse();
    
    println!("Initializing Grid: {}x{}", args.size, args.size);
    let mut sim = Simulation::new(args.size, args.density);

    let start = Instant::now();
    
    for i in 0..args.steps {
        sim.grid = sim.step_parallel();
    }

    let duration = start.elapsed();
    println!("Simulation completed in: {:?}", duration);
    println!("Time per step: {:?}", duration / args.steps as u32);

    if let Some(file_path) = args.append_to {
        use std::fs::OpenOptions;
        use std::io::Write;
        
        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(file_path)
            .unwrap();
            
        writeln!(file, "Rust,{},{},{}", args.size, args.steps, duration.as_secs_f64()).unwrap();
    }
}
