from playwright.sync_api import expect

from ui_tests.helpers import save_named_screenshot


def test_home_page_loads(page, base_url):
    page.goto(base_url, wait_until="domcontentloaded")

    expect(page).to_have_url(base_url + "/")
    expect(page.locator("h1")).to_be_visible()

    save_named_screenshot(page, "home-loaded")


def test_invalid_form_input_shows_validation_feedback(page, base_url):
    page.goto(base_url, wait_until="domcontentloaded")
    page.get_by_role("button", name="登录").click()

    expect(page.locator("#error-message")).to_contain_text("请输入账号")

    save_named_screenshot(page, "form-validation")