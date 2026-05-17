import json
import os
from pathlib import Path

import pytest


def pytest_addoption(parser):
    parser.addoption("--base-url", action="store", default=os.getenv("PLAYWRIGHT_BASE_URL", "http://127.0.0.1:3000"))
    parser.addoption("--login-url", action="store", default=os.getenv("PLAYWRIGHT_LOGIN_URL", ""))
    parser.addoption("--username", action="store", default=os.getenv("PLAYWRIGHT_USERNAME", ""))
    parser.addoption("--password", action="store", default=os.getenv("PLAYWRIGHT_PASSWORD", ""))
    parser.addoption("--storage-state", action="store", default=os.getenv("PLAYWRIGHT_STORAGE_STATE", ""))
    parser.addoption("--cookies-file", action="store", default=os.getenv("PLAYWRIGHT_COOKIES_FILE", ""))


@pytest.fixture(scope="session")
def base_url(pytestconfig):
    return pytestconfig.getoption("base_url").rstrip("/")


@pytest.fixture(scope="session")
def login_url(pytestconfig, base_url):
    value = pytestconfig.getoption("login_url")
    return value.rstrip("/") if value else f"{base_url}/login"


@pytest.fixture(scope="session")
def credentials(pytestconfig):
    return {
        "username": pytestconfig.getoption("username"),
        "password": pytestconfig.getoption("password"),
    }


@pytest.fixture(scope="session")
def auth_state(pytestconfig):
    storage_state = pytestconfig.getoption("storage_state")
    cookies_file = pytestconfig.getoption("cookies_file")

    if storage_state:
        return {"mode": "storage_state", "value": str(Path(storage_state).expanduser())}
    if cookies_file:
        return {"mode": "cookies_file", "value": str(Path(cookies_file).expanduser())}
    return {"mode": "none", "value": ""}


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, auth_state):
    if auth_state["mode"] != "storage_state":
        return browser_context_args
    return {
        **browser_context_args,
        "storage_state": auth_state["value"],
    }


@pytest.fixture(autouse=True)
def apply_auth_state(context, auth_state):
    if auth_state["mode"] != "cookies_file":
        return

    cookies_path = Path(auth_state["value"])
    if not cookies_path.is_file():
        raise AssertionError(f"Cookie file not found: {cookies_path}")

    with cookies_path.open("r", encoding="utf-8") as fp:
        cookies = json.load(fp)

    if not isinstance(cookies, list) or not cookies:
        raise AssertionError("Cookie file must be a non-empty JSON array.")

    context.add_cookies(cookies)
