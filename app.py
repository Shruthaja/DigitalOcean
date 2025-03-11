import subprocess
import threading
import time
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Function to simulate load by keeping the CPU busy
@app.route('/generate-load')
def generate_load():
    # Simple CPU-bound task to simulate load (infinite loop)
    while True:
        # Perform a simple operation that will consume CPU (this will keep the CPU busy)
        _ = [x**2 for x in range(100000)]
        time.sleep(0.1)  # Small sleep to avoid crashing the app, you can adjust as needed

# Function to start Locust load testing as a subprocess
def start_locust():
    subprocess.run(['locust', '-f', 'locustfile.py', '--headless', '--users', '10', '--spawn-rate', '2', '--host', 'http://localhost:5000'])

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to trigger the load generation
@app.route('/trigger-load')
def trigger_load():
    # Start the Locust load test in a separate thread
    load_thread = threading.Thread(target=start_locust)
    load_thread.start()
    return jsonify({"message": "Load generation started!"})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)