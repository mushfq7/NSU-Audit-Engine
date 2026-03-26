from locust import HttpUser, task, between

class NSUAuditStudent(HttpUser):
    wait_time = between(1, 5)

    @task(3)
    def load_homepage(self):
        """Simulates a student loading the main Streamlit portal."""
        # This hits the main app page
        self.client.get("/")

    @task(1)
    def check_system_health(self):
        """Simulates an internal system health ping."""
        # Streamlit's modern internal health endpoint
        self.client.get("/_stcore/health")