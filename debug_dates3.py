from playwright.sync_api import sync_playwright

url = "https://ultrasignup.com/results_event.aspx?did=119817"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(url, wait_until='domcontentloaded', timeout=60000)
    
    text = page.text_content('body')
    
    # Get context around September 20, 2025
    import re
    matches = list(re.finditer(r'(September|October|November)\s+(\d{1,2}),?\s+(\d{4})', text))
    
    print(f"Found {len(matches)} date(s)")
    for match in matches:
        start = max(0, match.start() - 200)
        end = min(len(text), match.end() + 200)
        context = text[start:end]
        print(f"\nContext around: {match.group()}")
        print(context)
        print("-" * 80)
    
    browser.close()
