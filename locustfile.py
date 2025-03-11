from locust import HttpUser, task, between

class LoadTest(HttpUser):
    wait_time = between(1, 2)  # Time between simulated user requests

    @task
    def generate_load(self):
        self.client.get("/generate-load")  # Hit the endpoint in your Flask app
