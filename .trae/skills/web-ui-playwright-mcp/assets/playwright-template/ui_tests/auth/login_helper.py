from playwright.sync_api import expect


def login_with_password(page, login_url: str, credentials: dict):
    username = credentials.get("username", "")
    password = credentials.get("password", "")

    if not username or not password:
        raise AssertionError("Missing PLAYWRIGHT_USERNAME or PLAYWRIGHT_PASSWORD")

    page.goto(login_url, wait_until="domcontentloaded")
    page.get_by_label("账号").fill(username)
    page.get_by_label("密码").fill(password)
    page.get_by_role("button", name="登录").click()

    expect(page).not_to_have_url(lambda url: "/login" in url)
    expect(page.get_by_role("main")).to_be_visible()