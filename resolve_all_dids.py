"""Resolve 50K/Marathon DIDs for each year by reading toggle links."""
from playwright.sync_api import sync_playwright

# Known 50K DIDs as seeds (from the toggle block we already trust)
SEED_50K = {
    2025: 119817,
    2024: 108870,
    2023: 97857,
    2022: 88170,
    2021: 79789,
    2020: 71482,
    2019: 60848,
    2018: 50528,
    2017: 41232,
    2016: 34630,
    2015: 32215,
}


def resolve_links(seed_did):
    url = f"https://ultrasignup.com/results_event.aspx?did={seed_did}"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        links = page.evaluate(
            """
            () => {
                const container = document.querySelector('div.unit-1.text-right');
                if (!container) return [];
                return Array.from(container.querySelectorAll('a')).map(a => ({
                    text: (a.textContent || '').trim(),
                    href: a.getAttribute('href') || ''
                }));
            }
            """
        )
        browser.close()
    mapping = {}
    for link in links:
        href = link.get('href','')
        text = link.get('text','').lower()
        if 'did=' in href:
            try:
                did_val = int(href.split('did=')[1].split('#')[0])
            except ValueError:
                continue
            if '50k' in text:
                mapping['50K'] = did_val
            elif 'marathon' in text:
                mapping['Marathon'] = did_val
    return mapping


def main():
    results = {}
    for year, seed in sorted(SEED_50K.items()):
        mapping = resolve_links(seed)
        results[year] = mapping
        print(f"{year}: {mapping}")
    print("\nFinal mapping:")
    for year in sorted(results):
        m = results[year]
        print(f"{year}: 50K={m.get('50K')} Marathon={m.get('Marathon')}")


if __name__ == "__main__":
    main()
