"""
Load testing script (Locust). Run with: locust -f tests/load/locustfile.py

Scenario weighting reflects expected real usage: most traffic is read-heavy
browsing (disease info, schemes, videos) with chat as the most resource-
intensive path (embedding + vector search + LLM call) — weighted lower to
avoid the load test itself becoming an unrealistic LLM-cost generator, but
still present since it's the path most likely to be a bottleneck.
"""
from locust import HttpUser, task, between


class JanSwasthyaUser(HttpUser):
    wait_time = between(2, 8)  # simulates realistic human think-time between actions
    token = None

    def on_start(self):
        # Register a throwaway user per simulated client
        import random
        phone = f"9{random.randint(100000000, 999999999)}"
        res = self.client.post("/api/v1/auth/register", json={
            "full_name": "Load Test User",
            "phone_number": phone,
            "password": "loadtestpass123",
        })
        if res.status_code == 201:
            self.token = res.json()["access_token"]

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    @task(5)
    def browse_diseases(self):
        self.client.get("/api/v1/diseases/")

    @task(3)
    def browse_schemes(self):
        self.client.get("/api/v1/schemes/")

    @task(3)
    def browse_videos(self):
        self.client.get("/api/v1/videos/")

    @task(2)
    def view_disease_detail(self):
        self.client.get("/api/v1/diseases/dengue")

    @task(1)
    def send_chat_message(self):
        self.client.post(
            "/api/v1/chat/message",
            json={"message": "What are the symptoms of dengue?", "language": "en"},
            headers=self.headers,
        )
