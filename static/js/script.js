        function startMemoryLoadTest() {
            document.getElementById('message').innerText = "Starting memory load test...";

            fetch('/start-memory-load')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('message').innerText = data.message;
                    updateStatus();
                })
                .catch(error => {
                    document.getElementById('message').innerText = "Error starting memory load test!";
                });
        }

        function stopMemoryLoadTest() {
            document.getElementById('message').innerText = "Stopping memory load test...";

            fetch('/stop-memory-load')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('message').innerText = data.message;
                    updateStatus();
                })
                .catch(error => {
                    document.getElementById('message').innerText = "Error stopping memory load test!";
                });
        }

        function startCpuLoadTest() {
            document.getElementById('message').innerText = "Starting CPU load test...";

            fetch('/start-cpu-load')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('message').innerText = data.message;
                    updateStatus();
                })
                .catch(error => {
                    document.getElementById('message').innerText = "Error starting CPU load test!";
                });
        }

        function stopCpuLoadTest() {
            document.getElementById('message').innerText = "Stopping CPU load test...";

            fetch('/stop-cpu-load')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('message').innerText = data.message;
                    updateStatus();
                })
                .catch(error => {
                    document.getElementById('message').innerText = "Error stopping CPU load test!";
                });
        }

        function stopAllTests() {
            document.getElementById('message').innerText = "EMERGENCY STOP: Stopping all load tests...";

            // Stop both tests in parallel
            Promise.all([
                fetch('/stop-cpu-load').then(response => response.json()),
                fetch('/stop-memory-load').then(response => response.json())
            ])
            .then(results => {
                document.getElementById('message').innerText = "All load tests have been stopped.";
                updateStatus();
            })
            .catch(error => {
                document.getElementById('message').innerText = "Error stopping tests! Server may be overloaded.";
            });
        }

        function updateStatus() {
            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    // Update CPU display
                    const cpuPercent = data.cpu_percent.toFixed(1);
                    document.getElementById('cpu-value').innerText = cpuPercent + '%';
                    document.getElementById('cpu-bar').style.width = cpuPercent + '%';

                    // Change color if approaching danger zone
                    if (cpuPercent > 80) {
                        document.getElementById('cpu-bar').style.backgroundColor = '#dc3545';
                    } else {
                        document.getElementById('cpu-bar').style.backgroundColor = '#0062cc';
                    }

                    // Update Memory display
                    const memoryPercent = data.memory_percent.toFixed(1);
                    document.getElementById('memory-value').innerText = memoryPercent + '%';
                    document.getElementById('memory-bar').style.width = memoryPercent + '%';

                    // Change color if approaching danger zone
                    if (memoryPercent > 80) {
                        document.getElementById('memory-bar').style.backgroundColor = '#dc3545';
                    } else {
                        document.getElementById('memory-bar').style.backgroundColor = '#28a745';
                    }

                    // Update test status
                    document.getElementById('cpu-test-status').innerText = data.cpu_test_running ? 'Running' : 'Stopped';
                    document.getElementById('cpu-test-status').style.color = data.cpu_test_running ? '#28a745' : '#dc3545';

                    document.getElementById('memory-test-status').innerText = data.memory_test_running ? 'Running' : 'Stopped';
                    document.getElementById('memory-test-status').style.color = data.memory_test_running ? '#28a745' : '#dc3545';

                    // Warning if memory is getting high
                    if (memoryPercent > 85 && (data.cpu_test_running || data.memory_test_running)) {
                        document.getElementById('message').innerHTML =
                            "<span class='attention'>WARNING: Memory usage is very high! Consider stopping tests to prevent pod crash.</span>";
                    }
                })
                .catch(error => {
                    console.error("Error fetching status:", error);
                    document.getElementById('message').innerText = "Error fetching status. Server may be overloaded.";
                });
        }

        // Update status every 2 seconds
        setInterval(updateStatus, 2000);

        // Initial status update
        updateStatus();
