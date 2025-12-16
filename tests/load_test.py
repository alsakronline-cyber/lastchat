from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task(1)
    def health_check(self):
        self.client.get("/api/v1/health")

    @task(3)
    def ask_recommendation(self):
        self.client.post("/api/v1/recommend", json={"query": "SICK distance sensor"})
