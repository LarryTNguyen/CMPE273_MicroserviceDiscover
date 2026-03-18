# registry_client.py
import requests
from threading import Thread, Event

class RegistryClient:
    def __init__(self, service_name, service_address, registry_url="http://localhost:5001"):
        self.service_name = service_name
        self.service_address = service_address
        self.registry_url = registry_url
        self.stop_event = Event()
        self.heartbeat_interval = 10

    def register(self):
        response = requests.post(
            f"{self.registry_url}/register",
            json={
                "service": self.service_name,
                "address": self.service_address
            },
            timeout=5
        )
        response.raise_for_status()
        return response.json()

    def heartbeat(self):
        response = requests.post(
            f"{self.registry_url}/heartbeat",
            json={
                "service": self.service_name,
                "address": self.service_address
            },
            timeout=5
        )
        return response

    def discover(self, service_name):
        response = requests.get(
            f"{self.registry_url}/discover/{service_name}",
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get("instances", [])
        return []

    def deregister(self):
        try:
            requests.post(
                f"{self.registry_url}/deregister",
                json={
                    "service": self.service_name,
                    "address": self.service_address
                },
                timeout=5
            )
        except Exception:
            pass

    def heartbeat_loop(self):
        while not self.stop_event.is_set():
            try:
                self.heartbeat()
            except Exception:
                pass
            self.stop_event.wait(self.heartbeat_interval)

    def start(self):
        self.register()
        t = Thread(target=self.heartbeat_loop, daemon=True)
        t.start()

    def stop(self):
        self.stop_event.set()
        self.deregister()