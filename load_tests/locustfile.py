import random
import time

from locust import HttpUser, between, task


class ConcurrencyTestUser(HttpUser):
    # No wait time between requests
    wait_time = between(0, 0)

    def on_start(self):
        """
        Executed once per simulated user before the swarm begins.
        Registers, logs in, and finds which seat to target.
        """
        # 1. Create a unique user
        user_str = f"locust_{random.randint(100000, 999999)}_{int(time.time())}"
        self.client.post(
            "/api/users/register/",
            json={
                "email": f"{user_str}@test.com",
                "username": user_str,
                "password": "Password123!",
            },
        )

        # 2. Login and get the JWT Token
        res = self.client.post(
            "/api/users/login/", json={"email": f"{user_str}@test.com", "password": "Password123!"}
        )
        self.token = res.json().get("access")
        self.headers = {"Authorization": f"Bearer {self.token}"}

        # 3. Get the first session and the first available seat
        sessions = self.client.get("/api/cinema/sessions/").json().get("results", [])
        if sessions:
            self.session_id = sessions[0]["id"]
            seats = self.client.get(f"/api/cinema/sessions/{self.session_id}/seat_map/").json()
            if seats:
                # Always pick the very first seat (e.g., A1) to force concurrency!
                self.seat_id = seats[0]["seat_id"]
        else:
            self.session_id = None
            self.seat_id = None

    @task
    def attempt_reservation(self):
        """
        The main task: Attempt to reserve the EXACT SAME seat simultaneously.
        """
        if not self.session_id or not self.seat_id:
            return

        payload = {"session_id": self.session_id, "seat_id": self.seat_id}

        # We use catch_response=True to customize what Locust considers a "Failure"
        with self.client.post(
            "/api/ticketing/reserve/", json=payload, headers=self.headers, catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 400 and "reserved" in response.text:
                # The lock worked! We mark it as a failure in Locust to see it on the graph,
                # but with a clear message that Redis successfully blocked the race condition.
                response.failure("Lock Worked (Seat already reserved)")
            else:
                response.failure(f"Unexpected error: {response.status_code}")

        # The user stops trying after hitting the endpoint once (hit and run)
        self.environment.runner.quit()
