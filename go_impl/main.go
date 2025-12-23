package main

import (
	"flag"
	"fmt"
	"math/rand"
	"os"
	"runtime"
	"sync"
	"time"
)

const (
	Empty = 0
	Tree  = 1
	Fire  = 2
)

type Simulation struct {
	grid   []uint8
	width  int
	height int
}

func NewSimulation(width, height int, density float64) *Simulation {
	grid := make([]uint8, width*height)
	rand.Seed(time.Now().UnixNano())

	for i := 0; i < width*height; i++ {
		if rand.Float64() < density {
			grid[i] = Tree
		} else {
			grid[i] = Empty
		}
	}

	// Ignite center
	cx, cy := width/2, height/2
	grid[cy*width+cx] = Fire

	return &Simulation{
		grid:   grid,
		width:  width,
		height: height,
	}
}

// updateChunk processes a range of rows
func (s *Simulation) updateChunk(startRow, endRow int, nextGrid []uint8, wg *sync.WaitGroup) {
	defer wg.Done()

	for r := startRow; r < endRow; r++ {
		for c := 0; c < s.width; c++ {
			idx := r*s.width + c
			cell := s.grid[idx]

			if cell == Fire {
				nextGrid[idx] = Empty
			} else if cell == Empty {
				nextGrid[idx] = Empty
			} else if cell == Tree {
				// Check neighbors
				onFire := false
				
				// Neighbors: Up, Down, Left, Right (with boundary checks)
				// Up
				if r > 0 && s.grid[(r-1)*s.width+c] == Fire {
					onFire = true
				}
				// Down
				if !onFire && r < s.height-1 && s.grid[(r+1)*s.width+c] == Fire {
					onFire = true
				}
				// Left
				if !onFire && c > 0 && s.grid[r*s.width+(c-1)] == Fire {
					onFire = true
				}
				// Right
				if !onFire && c < s.width-1 && s.grid[r*s.width+(c+1)] == Fire {
					onFire = true
				}

				if onFire {
					nextGrid[idx] = Fire
				} else {
					nextGrid[idx] = Tree
				}
			}
		}
	}
}

func (s *Simulation) Step(workers int) {
	nextGrid := make([]uint8, len(s.grid))
	var wg sync.WaitGroup

	rowsPerWorker := s.height / workers
	if rowsPerWorker == 0 {
		rowsPerWorker = 1
		workers = s.height
	}

	for w := 0; w < workers; w++ {
		startRow := w * rowsPerWorker
		endRow := (w + 1) * rowsPerWorker
		if w == workers-1 {
			endRow = s.height
		}

		wg.Add(1)
		go s.updateChunk(startRow, endRow, nextGrid, &wg)
	}

	wg.Wait()
	s.grid = nextGrid
}

func main() {
	var size int
	var steps int
	var density float64
	var appendTo string

	flag.IntVar(&size, "size", 1000, "Grid size (NxN)")
	flag.IntVar(&steps, "steps", 100, "Number of simulation steps")
	flag.Float64Var(&density, "density", 0.6, "Tree density")
	flag.StringVar(&appendTo, "append-to", "", "Append results to CSV file")
	flag.Parse()

	fmt.Printf("Initializing Grid: %dx%d\n", size, size)
	sim := NewSimulation(size, size, density)

	// Use number of logical CPUs for workers
	workers := runtime.NumCPU()

	start := time.Now()

	for i := 0; i < steps; i++ {
		sim.Step(workers)
	}

	duration := time.Since(start)
	seconds := duration.Seconds()
	
	fmt.Printf("Simulation completed in: %v\n", duration)
	fmt.Printf("Time per step: %v\n", duration/time.Duration(steps))

	if appendTo != "" {
		f, err := os.OpenFile(appendTo, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error opening file: %v\n", err)
			return
		}
		defer f.Close()

		fmt.Fprintf(f, "Go,%d,%d,%.6f\n", size, steps, seconds)
	}
}
