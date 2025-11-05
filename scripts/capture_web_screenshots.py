#!/usr/bin/env python3
import asyncio
import os
from pathlib import Path

from playwright.async_api import async_playwright, Page, TimeoutError as PlaywrightTimeoutError

IMAGES_DIR = Path("docs/images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:8501")
API_URL = os.getenv("API_URL", "http://localhost:8000")

VIEWPORT = {"width": 1920, "height": 1080}

def target_path(name: str) -> str:
    return str(IMAGES_DIR / name)

async def safe_click(page: Page, text: str, timeout: int = 3000) -> bool:
    for f in (
        lambda: page.get_by_role("link", name=text, exact=True).first,
        lambda: page.get_by_role("button", name=text, exact=True).first,
        lambda: page.get_by_text(text, exact=True).first,
    ):
        try:
            el = f()
            await el.click(timeout=timeout)
            return True
        except Exception:
            continue
    return False

async def wait_ready(page: Page, extra_ms: int = 800):
    await page.wait_for_load_state("domcontentloaded")
    await page.wait_for_timeout(extra_ms)

async def screenshot_full(page: Page, filename: str):
    await page.screenshot(path=target_path(filename), full_page=True)

async def capture_dashboard(page: Page):
    print("📸 Capturing dashboard screenshots...")
    try:
        await page.goto(DASHBOARD_URL, wait_until="domcontentloaded", timeout=10000)
        await wait_ready(page)
        await screenshot_full(page, "01-dashboard-home.png")
        print("✅ Captured: 01-dashboard-home.png")
    except Exception as e:
        print(f"⚠️  Dashboard not available: {e}")
        return

    # Analytics
    for label in ["Analytics", "Course Metrics", "📊 Analytics"]:
        if await safe_click(page, label):
            await wait_ready(page)
            await screenshot_full(page, "02-analytics-page.png")
            print("✅ Captured: 02-analytics-page.png")
            break

    # AI Insights
    for label in ["AI Insights", "AI Analysis", "🤖 AI Insights"]:
        if await safe_click(page, label):
            await wait_ready(page)
            await screenshot_full(page, "03-ai-insights.png")
            print("✅ Captured: 03-ai-insights.png")
            break

    # Automation
    for label in ["Automation", "⚙️ Automation"]:
        if await safe_click(page, label):
            await wait_ready(page)
            await screenshot_full(page, "04-automation-page.png")
            print("✅ Captured: 04-automation-page.png")
            break

async def capture_api_docs(page: Page):
    print("\n📸 Capturing API documentation screenshots...")
    # Swagger
    try:
        await page.goto(f"{API_URL}/docs", wait_until="domcontentloaded", timeout=10000)
        await wait_ready(page)
        await screenshot_full(page, "05-api-docs-swagger.png")
        print("✅ Captured: 05-api-docs-swagger.png")
        await screenshot_full(page, "11-api-endpoints.png")
        print("✅ Captured: 11-api-endpoints.png")
    except Exception as e:
        print(f"⚠️  API not available: {e}")
        return

    # Execute example GET (12)
    try:
        get_blocks = page.locator(".opblock.opblock-get")
        count = await get_blocks.count()
        target = None
        for i in range(count):
            block = get_blocks.nth(i)
            text = (await block.text_content()) or ""
            if "/api/courses" in text or "/courses" in text:
                target = block
                break
        if target:
            await target.click()
            await wait_ready(page)
            try_btn = target.get_by_role("button", name="Try it out").first
            await try_btn.click()
            await wait_ready(page)
            exec_btn = target.get_by_role("button", name="Execute").first
            await exec_btn.click()
            await page.wait_for_timeout(1500)
            body = target.locator(".opblock-body").first
            await body.screenshot(path=target_path("12-api-response.png"))
            print("✅ Captured: 12-api-response.png")
        else:
            await screenshot_full(page, "12-api-response.png")
            print("✅ Captured: 12-api-response.png (fallback)")
    except Exception as e:
        print(f"⚠️  Could not capture API response: {e}")
        await screenshot_full(page, "12-api-response.png")
        print("✅ Captured: 12-api-response.png (fallback)")

    # ReDoc
    try:
        await page.goto(f"{API_URL}/redoc", wait_until="domcontentloaded", timeout=10000)
        await wait_ready(page)
        await screenshot_full(page, "06-api-docs-redoc.png")
        print("✅ Captured: 06-api-docs-redoc.png")
    except Exception as e:
        print(f"⚠️  ReDoc not available: {e}")

async def main():
    print("🚀 Starting screenshot capture...\n")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(viewport=VIEWPORT, device_scale_factor=1.0)
        page = await context.new_page()

        await capture_dashboard(page)
        await capture_api_docs(page)

        await context.close()
        await browser.close()
    
    print("\n✨ Screenshot capture complete!")
    print(f"📁 Images saved to: {IMAGES_DIR.absolute()}")

if __name__ == "__main__":
    asyncio.run(main())
