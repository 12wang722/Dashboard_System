from playwright.sync_api import expect

from ui_tests.auth.login_helper import login_with_password
from ui_tests.helpers import save_named_screenshot


def test_login_succeeds_and_dashboard_loads(page, login_url, credentials):
    login_with_password(page, login_url, credentials)

    expect(page).to_have_url(lambda url: any(item in url for item in ["dashboard", "home", "index", "workbench"]))
    expect(page.get_by_role("main")).to_be_visible()

    save_named_screenshot(page, "login-success")


def test_post_login_key_module_is_visible(page, base_url, login_url, credentials):
    login_with_password(page, login_url, credentials)
    page.goto(f"{base_url}/dashboard", wait_until="domcontentloaded")

    expect(page.get_by_role("main")).to_be_visible()

    save_named_screenshot(page, "post-login-dashboard")