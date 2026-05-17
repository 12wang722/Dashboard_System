from pathlib import Path


def save_named_screenshot(page, name: str) -> str:
    output_dir = Path("screenshots")
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{name}.png"
    page.screenshot(path=str(path), full_page=True)
    return str(path)