#include <algorithm>
#include <chrono>
#include <fstream>
#include <iostream>
#include <random>
#include <thread>
#include <vector>

// States
const uint8_t EMPTY = 0;
const uint8_t TREE = 1;
const uint8_t FIRE = 2;

struct Simulation {
  int size;
  std::vector<uint8_t> grid;
  std::vector<uint8_t> next_grid;

  Simulation(int s) : size(s), grid(s * s), next_grid(s * s) {
    std::mt19937 rng(std::random_device{}());
    std::uniform_real_distribution<float> dist(0.0, 1.0);

    for (int i = 0; i < size * size; ++i) {
      grid[i] = (dist(rng) < 0.6) ? TREE : EMPTY;
    }

    // Ignite center
    int center = size / 2;
    grid[center * size + center] = FIRE;
  }

  bool has_burning_neighbor(int r, int c) const {
    const int dr[] = {-1, 1, 0, 0};
    const int dc[] = {0, 0, -1, 1};

    for (int i = 0; i < 4; ++i) {
      int nr = r + dr[i];
      int nc = c + dc[i];
      if (nr >= 0 && nr < size && nc >= 0 && nc < size) {
        if (grid[nr * size + nc] == FIRE) {
          return true;
        }
      }
    }
    return false;
  }

  void update_chunk(int start_row, int end_row) {
    for (int r = start_row; r < end_row; ++r) {
      for (int c = 0; c < size; ++c) {
        int idx = r * size + c;
        uint8_t state = grid[idx];

        if (state == FIRE) {
          next_grid[idx] = EMPTY;
        } else if (state == TREE) {
          if (has_burning_neighbor(r, c)) {
            next_grid[idx] = FIRE;
          } else {
            next_grid[idx] = TREE;
          }
        } else {
          next_grid[idx] = EMPTY;
        }
      }
    }
  }

  void step_parallel(int num_threads) {
    std::vector<std::thread> threads;
    int chunk_size = size / num_threads;

    for (int i = 0; i < num_threads; ++i) {
      int start = i * chunk_size;
      int end = (i == num_threads - 1) ? size : (i + 1) * chunk_size;
      threads.emplace_back(&Simulation::update_chunk, this, start, end);
    }

    for (auto &t : threads) {
      t.join();
    }

    std::swap(grid, next_grid);
  }
};

int main(int argc, char *argv[]) {
  int size = 100;
  int steps = 100;
  std::string append_to = "";
  int threads = std::thread::hardware_concurrency();

  for (int i = 1; i < argc; ++i) {
    std::string arg = argv[i];
    if (arg == "--size" && i + 1 < argc)
      size = std::stoi(argv[++i]);
    else if (arg == "--steps" && i + 1 < argc)
      steps = std::stoi(argv[++i]);
    else if (arg == "--append-to" && i + 1 < argc)
      append_to = argv[++i];
  }

  std::cout << "Initializing Grid: " << size << "x" << size
            << " | Threads: " << threads << std::endl;
  Simulation sim(size);

  auto start_time = std::chrono::high_resolution_clock::now();

  for (int i = 0; i < steps; ++i) {
    sim.step_parallel(threads);
  }

  auto end_time = std::chrono::high_resolution_clock::now();
  std::chrono::duration<double> duration = end_time - start_time;

  std::cout << "Simulation completed in: " << duration.count() << " seconds"
            << std::endl;
  std::cout << "Time per step: " << duration.count() / steps << " seconds"
            << std::endl;

  if (!append_to.empty()) {
    std::ofstream outfile;
    outfile.open(append_to, std::ios_base::app);
    outfile << "C++," << size << "," << duration.count() << "\n";
  }

  return 0;
}
