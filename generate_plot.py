import matplotlib.pyplot as plt
import csv
import os

OUTPUT_FILE = "benchmark_results.csv"

def plot_results():
    if not os.path.exists(OUTPUT_FILE):
        print("CSV file not found!")
        return

    data = {"Rust": {}, "Python": {}, "Go": {}, "C++": {}}
    
    with open(OUTPUT_FILE, "r") as f:
        # Use simple reader to handle variable columns
        reader = csv.reader(f)
        header = next(reader) # skip header
        
        for row in reader:
            if not row or len(row) < 3: continue
            
            lang = row[0]
            size = int(row[1])
            
            # C++ format: Language, Size, Time
            if len(row) == 3:
                time_sec = float(row[2])
            # Others: Language, Size, Steps, Time
            else:
                time_sec = float(row[3])
            
            if size not in data[lang]:
                data[lang][size] = []
            data[lang][size].append(time_sec)

    # Calculate averages
    sizes = sorted(list(data["Rust"].keys()))
    rust_times = [sum(data["Rust"][s])/len(data["Rust"][s]) for s in sizes]
    python_times = [sum(data["Python"][s])/len(data["Python"][s]) for s in sizes]
    go_times = [sum(data["Go"][s])/len(data["Go"][s]) for s in sizes]
    cpp_times = [sum(data["C++"][s])/len(data["C++"][s]) for s in sizes]

    # Create img directory if not exists
    os.makedirs("img", exist_ok=True)

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
    plot_results()
