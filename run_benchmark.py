import subprocess
import os
import time
import matplotlib.pyplot as plt
import csv

# Configuration
# Configuration
SIZES = [100, 300, 500, 800, 1000, 1500, 2000, 2500, 3000, 4000, 5000]
STEPS = 100
REPEATS = 5
OUTPUT_FILE = "benchmark_results.csv"

# Paths
RUST_BIN = "rust_impl/target/release/fire_simulation_rust"
PYTHON_SCRIPT = "python_impl/main.py"
GO_BIN = "go_impl/fire_simulation_go"
CPP_BIN = "cpp_impl/fire_simulation_cpp"

def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}\n{e}")

def main():
    # Initialize CSV
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    
    with open(OUTPUT_FILE, "w") as f:
        f.write("Language,Size,Steps,TimeSeconds\n")

    # Build Rust 
    print("Building Rust project...")
    run_command("source $HOME/.cargo/env && cd rust_impl && cargo build --release")

    # Build Go
    print("Building Go project...")
    run_command(f"cd go_impl && go build -o fire_simulation_go main.go")

    # Build C++
    print("Building C++ project...")
    run_command(f"g++ -O3 -std=c++17 -pthread cpp_impl/main.cpp -o {CPP_BIN}")

    for size in SIZES:
        print(f"\n--- Testing Grid Size: {size}x{size} ---")
        
        for _ in range(REPEATS):
            # Run Rust
            print(f"Running Rust ({size}x{size})...")
            run_command(f"{RUST_BIN} --size {size} --steps {STEPS} --append-to {OUTPUT_FILE}")
            
            # Run Go
            print(f"Running Go ({size}x{size})...")
            run_command(f"{GO_BIN} -size {size} -steps {STEPS} -append-to {OUTPUT_FILE}")

            # Run C++
            print(f"Running C++ ({size}x{size})...")
            run_command(f"{CPP_BIN} --size {size} --steps {STEPS} --append-to {OUTPUT_FILE}")

            # Run Python
            print(f"Running Python ({size}x{size})...")
            # Use specific python path if needed, or default python3
            # Using /opt/anaconda3/bin/python3 based on previous success
            run_command(f"/opt/anaconda3/bin/python3 {PYTHON_SCRIPT} --size {size} --steps {STEPS} --append-to {OUTPUT_FILE}")

    print("\nBenchmark completed. Generating plot...")
    plot_results()

def plot_results():
    data = {"Rust": {}, "Python": {}, "Go": {}, "C++": {}}
    
    with open(OUTPUT_FILE, "r") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            return

        for row in reader:
            if not row or len(row) < 3:
                continue

            lang = row[0]
            size = int(row[1])
            
            # Helper to safely parse float
            try:
                if len(row) == 3:
                    # C++ format: [lang, size, time]
                    time_sec = float(row[2])
                else:
                    # Others: [lang, size, steps, time]
                    time_sec = float(row[3])
            except (ValueError, IndexError):
                continue

            if size not in data[lang]:
                data[lang][size] = []
            data[lang][size].append(time_sec)

    # Calculate averages
    sizes = sorted(list(data["Rust"].keys()))
    rust_times = [sum(data["Rust"][s])/len(data["Rust"][s]) for s in sizes]
    python_times = [sum(data["Python"][s])/len(data["Python"][s]) for s in sizes]
    go_times = [sum(data["Go"][s])/len(data["Go"][s]) for s in sizes]
    cpp_times = [sum(data["C++"][s])/len(data["C++"][s]) for s in sizes]

    plt.figure(figsize=(10, 6))
    plt.plot(sizes, rust_times, marker='o', label='Rust (Rayon)')
    plt.plot(sizes, python_times, marker='s', label='Python (Numpy)')
    plt.plot(sizes, go_times, marker='^', label='Go (Goroutines)')
    plt.plot(sizes, cpp_times, marker='x', label='C++ (std::thread)')
    
    plt.xlabel('Grid Size (NxN)')
    plt.ylabel('Execution Time (seconds) 100 steps')
    plt.title('Performance Benchmark: Rust vs Go vs C++ vs Python')
    plt.legend()
    plt.grid(True)
    plt.savefig('img/performance_comparison.png')
    print("Plot saved to img/performance_comparison.png")

if __name__ == "__main__":
    main()
