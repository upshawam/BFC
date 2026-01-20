import asyncio
from playwright.async_api import async_playwright

a_sync = async_playwright

async def run(did, label):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://ultrasignup.com/results_event.aspx?did={did}", wait_until='domcontentloaded', timeout=90000)
        await page.wait_for_selector('table#list', timeout=30000)
        await page.wait_for_timeout(5000)
        row_ids = await page.evaluate("jQuery('#list').jqGrid('getDataIDs')")
        codes = {}
        sample = {}
        for rid in row_ids:
            row = await page.evaluate(f"jQuery('#list').jqGrid('getRowData', '{rid}')")
            sc = str(row.get('status'))
            codes[sc] = codes.get(sc, 0) + 1
            sample.setdefault(sc, row)
        print(f"{label} did={did} status codes: {codes}")
        for sc, row in sample.items():
            print(f" sample for code {sc}: {row}")
        await browser.close()

async def main():
    await run(108870, '2024 50K')
    await run(116578, '2024 Marathon')

asyncio.run(main())
