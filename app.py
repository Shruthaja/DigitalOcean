import math
import threading
import psutil
import time
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Global instances of the loaders
cpu_loader = None
memory_loader_running = False
memory_data = []  # Global reference to allocated memory

class CPULoader:
    def __init__(self, target_percent=60, check_interval=1.0):
        """
        Initialize a CPU loader that targets a specific load percentage

        Args:
            target_percent: Target CPU utilization (0-100%)
            check_interval: How often to adjust the load (seconds)
        """
        self.target_percent = min(max(target_percent, 0), 100)
        self.check_interval = check_interval
        self.running = False
        self.processes = []
        self.monitor_thread = None
        self.intensity = 5000  # Starting intensity value - will be adjusted dynamically

    def _cpu_worker(self):
        """Worker process that performs calculations in bursts"""
        thread = threading.current_thread()
        while getattr(thread, "running", True):
            # Perform genuinely CPU-intensive operations using pure Python
            for _ in range(self.intensity):
                # Matrix multiplication simulation (CPU intensive)
                size = 20  # Small matrix size to simulate
                matrix_a = [[math.sin(i * j) for j in range(size)] for i in range(size)]
                matrix_c = [[0 for _ in range(size)] for _ in range(size)]

                # Manual matrix multiplication is very CPU intensive
                for i in range(size):
                    for j in range(size):
                        for k in range(size):
                            matrix_c[i][j] += matrix_a[i][k] * math.cos(k * j)

                # Additional math operations that cannot be easily optimized
                result = 0
                for i in range(100):
                    result += math.sin(i) * math.cos(i * 0.5) / (math.sqrt(i + 1) + 0.001)

    def _monitor_and_adjust(self):
        """Monitors CPU usage and adjusts worker processes and intensity"""
        while self.running:
            # Get current CPU usage
            current_percent = psutil.cpu_percent(interval=self.check_interval)
            # Log current status
            print(
                f"Current CPU: {current_percent:.1f}% | Target: {self.target_percent}% | Workers: {len(self.processes)} | Intensity: {self.intensity}")
            # Dynamically adjust intensity based on how far we are from target
            if current_percent < self.target_percent - 10:
                # Significantly increase intensity if we're way below target
                self.intensity = int(self.intensity * 1.5)
                print(f"⬆️ Increased intensity to {self.intensity}")
            elif current_percent < self.target_percent - 5:
                # Moderate increase
                self.intensity = int(self.intensity * 1.2)
                print(f"↗️ Moderately increased intensity to {self.intensity}")
            elif current_percent > self.target_percent + 10:
                # Significantly decrease intensity if we're way above target
                self.intensity = max(100, int(self.intensity * 0.5))
                print(f"⬇️ Decreased intensity to {self.intensity}")
            elif current_percent > self.target_percent + 5:
                # Moderate decrease
                self.intensity = max(100, int(self.intensity * 0.8))
                print(f"↘️ Moderately decreased intensity to {self.intensity}")

            # Adjust number of processes only if intensity adjustment isn't enough
            if current_percent < self.target_percent - 15 and len(self.processes) < psutil.cpu_count():
                # Add a worker if significantly below target
                new_process = threading.Thread(target=self._cpu_worker)
                new_process.running = True
                new_process.daemon = True
                new_process.start()
                self.processes.append(new_process)
                print(f"➕ Added worker ({len(self.processes)} total)")

            elif current_percent > self.target_percent + 15 and len(self.processes) > 1:
                # Remove a worker if significantly above target
                if self.processes:
                    process = self.processes.pop()
                    process.running = False
                    print(f"➖ Removed worker ({len(self.processes)} total)")

    def start(self, duration=None):
        """
        Start generating the specified CPU load

        Args:
            duration: How long to run in seconds (None = run until stop() is called)
        """
        if self.running:
            print("Already running")
            return

        self.running = True
        print(f"Starting CPU load test targeting {self.target_percent}% utilization...")

        # Start with a sensible number of workers (about half the available cores)
        initial_workers = max(1, psutil.cpu_count() // 2)
        for _ in range(initial_workers):
            new_process = threading.Thread(target=self._cpu_worker)
            new_process.running = True
            new_process.daemon = True
            new_process.start()
            self.processes.append(new_process)

        print(f"Started with {initial_workers} workers")

        # Start the monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_and_adjust)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        if duration is not None:
            time.sleep(duration)
            self.stop()

    def stop(self):
        """Stop the CPU load test"""
        if not self.running:
            return

        self.running = False

        # Stop all worker processes
        for process in self.processes:
            process.running = False

        self.processes = []
        print("CPU load test stopped")


def simulate_memory_load():
    """Simulate memory load that can be stopped externally"""
    global memory_loader_running, memory_data

    # Set flag
    memory_loader_running = True

    # Clear any previous data
    memory_data = []

    # Get current memory stats
    mem = psutil.virtual_memory()
    total_memory = mem.total
    available_memory = mem.available

    # Target 60% of AVAILABLE memory, not total
    target_memory_usage = available_memory * 0.6
    allocated_memory = 0

    print(f"Starting memory load test targeting 60% of available memory ({available_memory / (1024 ** 3):.2f} GB)")

    try:
        # Use larger chunks for faster allocation
        chunk_size = 10 ** 7  # 10 MB per allocation

        while allocated_memory < target_memory_usage and memory_loader_running:
            # Allocate larger chunks for faster memory consumption
            chunk = 'a' * chunk_size
            memory_data.append(chunk)
            allocated_memory += len(chunk)

            # Print progress after each larger chunk
            current_usage = psutil.virtual_memory().percent
            print(f"Allocated {allocated_memory / (1024 ** 2):.2f} MB, Total system usage: {current_usage}%")

            # Check if we should stop
            if not memory_loader_running:
                break

            # Safety check - stop if overall memory usage exceeds 60%
            if psutil.virtual_memory().percent > 60:
                print("Safety limit reached (80% total memory), stopping")
                break

            # No sleep between allocations to speed things up

        print(f"Memory allocation complete: {allocated_memory / (1024 ** 2):.2f} MB")

        # Keep the memory load until stopped
        while memory_loader_running:
            current_usage = psutil.virtual_memory().percent
            print(f"Holding memory load, current system usage: {current_usage}%")
            time.sleep(5)  # Report status every 5 seconds

    except MemoryError:
        print("Memory limit reached, but was caught early!")
    finally:
        # Make sure to clear memory if this function exits for any reason
        if not memory_loader_running:
            stop_memory_load_internal()


def stop_memory_load_internal():
    """Internal function to clean up memory load"""
    global memory_loader_running, memory_data

    memory_loader_running = False

    # Calculate memory to be freed
    memory_to_free = sum(len(chunk) for chunk in memory_data) / (1024 ** 2)

    # Clear the list to free memory
    memory_data.clear()

    # Force garbage collection
    import gc
    gc.collect()

    print(f"Memory load test stopped, freed approximately {memory_to_free:.2f} MB")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start-memory-load', methods=['GET'])
def start_memory_load():
    global memory_loader_running

    # Stop any existing memory load
    if memory_loader_running:
        stop_memory_load_internal()

    # Run the memory load test in a separate thread
    threading.Thread(target=simulate_memory_load, daemon=True).start()
    return jsonify(message="Memory load test started targeting 60% of total memory. Check the logs for details.")


@app.route('/stop-memory-load', methods=['GET'])
def stop_memory_load():
    global memory_loader_running

    if memory_loader_running:
        stop_memory_load_internal()
        return jsonify(message="Memory load test stopped.")
    else:
        return jsonify(message="No memory load test currently running.")


@app.route('/start-cpu-load', methods=['GET'])
def start_cpu_load():
    global cpu_loader

    # Stop any existing CPU loader
    if cpu_loader and cpu_loader.running:
        cpu_loader.stop()

    # Create and start a new CPU loader
    cpu_loader = CPULoader(target_percent=60)  # Target 60% CPU load

    # Start in a separate thread to avoid blocking the web server
    threading.Thread(target=cpu_loader.start, daemon=True).start()

    return jsonify(message="CPU load test started targeting 60% utilization. Check the logs for details.")


@app.route('/stop-cpu-load', methods=['GET'])
def stop_cpu_load():
    global cpu_loader
    if cpu_loader and cpu_loader.running:
        cpu_loader.stop()
        return jsonify(message="CPU load test stopped.")
    else:
        return jsonify(message="No CPU load test currently running.")

@app.route('/status', methods=['GET'])
def status():
    # Get CPU usage with a very short interval to get current value
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    memory_percent = memory.percent

    return jsonify({
        'cpu_percent': cpu_percent,
        'memory_percent': memory_percent,
        'cpu_test_running': cpu_loader.running if cpu_loader else False,
        'memory_test_running': memory_loader_running,
        'timestamp': time.time()  # Add timestamp to prevent caching
    })


# To ensure Flask doesn't cache responses
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)