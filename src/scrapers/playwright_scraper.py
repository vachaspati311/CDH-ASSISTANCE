from playwright.async_api import async_playwright

class PlaywrightScraper:
    async def scrape(self, url, wait_for_network=True):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                if wait_for_network:
                    await page.goto(url, wait_until="networkidle")
                else:
                    await page.goto(url)
                
                # Extract content
                title = await page.title()
                content = await page.evaluate("() => document.body.innerText")
                
                return {
                    "url": url,
                    "title": title,
                    "content": content,
                    "success": True
                }
            except Exception as e:
                return {
                    "url": url,
                    "error": str(e),
                    "success": False
                }
            finally:
                await browser.close()
    
    async def scrape_multiple(self, urls):
        results = []
        for url in urls:
            result = await self.scrape(url)
            results.append(result)
        return results
