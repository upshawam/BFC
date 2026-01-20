from playwright.sync_api import sync_playwright
import re

url = "https://ultrasignup.com/results_event.aspx?did=119817"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='domcontentloaded', timeout=60000)
    html = page.content()
    browser.close()

# Search for common date patterns and surrounding context
date_snippets = re.findall(r'.{0,50}(?:October|November|September|January|February|March|April|May|June|July|August|Dec|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*?(?:\d{1,2}|,|2\d{3}).{0,50}', html, re.IGNORECASE)

print(f"Found {len(date_snippets)} potential date contexts:")
for i, snippet in enumerate(date_snippets[:10]):
    print(f"{i+1}. {snippet[:150]}")
