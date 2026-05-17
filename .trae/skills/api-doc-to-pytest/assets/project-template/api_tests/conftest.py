import os
import pytest


def pytest_addoption(parser):
    parser.addoption("--base-url", action="store", default=os.getenv("API_BASE_URL", "http://127.0.0.1:8000"))
    parser.addoption("--token", action="store", default=os.getenv("API_TOKEN", ""))


@pytest.fixture(scope="session")
def base_url(request):
    return request.config.getoption("--base-url").rstrip("/")


@pytest.fixture(scope="session")
def auth_token(request):
    return request.config.getoption("--token")


@pytest.fixture(scope="session")
def default_headers(auth_token):
    headers = {"Content-Type": "application/json"}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"
    return headers
