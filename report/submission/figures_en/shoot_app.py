# Screenshot the built web app (web/dist) in English mode with headless Edge via Playwright.
import pathlib, sys
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(__file__).parent
URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5188/"

with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge", headless=True)
    pg = b.new_page(viewport={"width": 1600, "height": 900}, device_scale_factor=1.5)
    pg.goto(URL, wait_until="networkidle")
    pg.wait_for_timeout(2500)
    pg.screenshot(path=str(OUT / "app_00_debug.png"))
    print("BTN0:", [t.strip() for t in pg.locator("button").all_inner_texts()][:40])
    en = pg.locator("button").filter(has_text="en")
    en = pg.locator("xpath=//button[translate(normalize-space(.),'EN','en')='en']")
    en.first.click(timeout=5000)
    pg.wait_for_timeout(2500)
    pg.screenshot(path=str(OUT / "app_01_home.png"))
    # list tab-like buttons for further shots
    btns = [t.strip() for t in pg.locator("button").all_inner_texts() if t.strip()]
    print("BUTTONS:", btns[:80])
    b.close()
