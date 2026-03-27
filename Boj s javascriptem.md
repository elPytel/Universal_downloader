# Boj s javascriptem

- [ ] Opravení stahování ze stránek co potřebují `js` pomocí playwright.

Jako jedna z možných cest se nabízí:

playwright
playwright install

```python
def download_page_js(url, timeout=30000) -> SimpleResponse:
    if not _HAS_PLAYWRIGHT:
        raise RuntimeError("Install playwright.")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=timeout)
        
        # Najdeme odkaz s třídou decryptLink
        # Pokud jich je víc, budeš muset iterovat nebo vybrat ten správný
        link_selector = "a.decryptLink"
        
        if page.locator(link_selector).count() > 0:
            # Počkáme na navigaci, která nastane po kliknutí
            with page.expect_navigation(timeout=timeout):
                page.click(link_selector)
            
            # Nyní je page.url ta finální adresa (nebo v page.content je cílová stránka)
            final_url = page.url
            content = page.content()
            status = 200
        else:
            content = page.content()
            status = 404 # Nebo jiný handling, pokud tam link není
            
        browser.close()
    return SimpleResponse(content, status, final_url) # Doporučuji vracet i výslednou URL
```