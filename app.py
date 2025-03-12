import math
import threading
import psutil
import time
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Global instance of the CPU loader
cpu_loader = None


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
    total_memory = psutil.virtual_memory().total  # Total system memory
    target_memory_usage = total_memory * 0.6  # 60% of total memory

    allocated_memory = 0
    large_data = []

    try:
        while allocated_memory < target_memory_usage:
            # Allocate 1 MB chunks
            chunk = 'a' * 10 ** 6  # 1 MB per string
            large_data.append(chunk)
            allocated_memory += len(chunk)

            # Slow down the memory load to keep it under load for longer
            if allocated_memory % 10 ** 6 == 0:  # Every MB, print progress
                print(f"Allocated {allocated_memory / (1024 ** 2):.2f} MB")
            # time.sleep(0.5)  # Sleep for 0.5 seconds to slow down the allocation

        print(f"Memory limit reached: {allocated_memory / (1024 ** 2):.2f} MB (60% of total)")
        # Keep the memory load for some additional time after reaching the target
        time.sleep(120)  # Keep the load for 120 seconds after reaching the target

    except MemoryError:
        print("Memory limit reached, but was caught early!")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start-memory-load', methods=['GET'])
def start_memory_load():
    # Run the memory load test in a separate thread
    threading.Thread(target=simulate_memory_load, daemon=True).start()
    return jsonify(message="Memory load test started. Check the logs for details.")


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
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    memory_percent = memory.percent

    return jsonify({
        'cpu_percent': cpu_percent,
        'memory_percent': memory_percent,
        'cpu_test_running': cpu_loader.running if cpu_loader else False
    })


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)