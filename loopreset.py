import asyncio
import random
from playwright.async_api import async_playwright, TimeoutError

CHROMIUM_PATH = "/usr/bin/chromium"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

async def human_delay(min_ms=800, max_ms=2000):
    await asyncio.sleep(random.uniform(min_ms / 1000, max_ms / 1000))

async def reset_flow(page, context, username):
    await page.goto("https://www.instagram.com/accounts/password/reset/")
    await page.wait_for_load_state("networkidle")
    await human_delay()

    await page.fill("input[name='cppEmailOrUsername']", username)
    await human_delay()

    await page.get_by_role("button", name="Send login link").click()
    await human_delay(2000, 3000)

    # Click OK if dialog appears
    try:
        await page.get_by_role("button", name="OK").click(timeout=4000)
        await human_delay()
    except TimeoutError:
        pass

    # ---- OPEN NEW TAB ----
    new_page = await context.new_page()
    await new_page.goto("about:blank")
    await human_delay()

    # ---- CLOSE OLD TAB ----
    await page.close()

    # ---- SWITCH CONTROL ----
    await new_page.bring_to_front()
    return new_page


async def main():
    username = input("Enter Instagram username/email: ").strip()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            executable_path=CHROMIUM_PATH,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )

        context = await browser.new_context(
            viewport=None,
            user_agent=USER_AGENT,
            locale="en-US"
        )

        # Hide webdriver flag
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )

        page = await context.new_page()

        print("\n Running continuously. Press CTRL + C to stop.\n")

        try:
            while True:
                page = await reset_flow(page, context, username)
                await human_delay(3000, 6000)

        except KeyboardInterrupt:
            print("\n⛔ Stopped by user (Ctrl + C)")

        finally:
            await browser.close()

asyncio.run(main())
