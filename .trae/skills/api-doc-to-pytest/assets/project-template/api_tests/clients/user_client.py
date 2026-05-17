from api_tests.clients.base_client import BaseClient


class UserClient(BaseClient):
    def create_user(self, payload):
        return self.request("POST", "/api/users", json=payload)

    def get_user(self, user_id):
        return self.request("GET", f"/api/users/{user_id}")

    def delete_user(self, user_id):
        return self.request("DELETE", f"/api/users/{user_id}")
