import asyncio
import logging
from playwright.async_api import Browser, Page, expect
from playwright.async_api._generated import Playwright
from playwright.async_api._context_manager import PlaywrightContextManager
from os import path


CURRENT_DIR = path.dirname(path.realpath(__file__))
MAX_THREADS = 10


class Screenshot:
    def __init__(self) -> None:
        self._playwright_context_manager: PlaywrightContextManager
        self._playwright_handler: Playwright
        self._browser_handler: Browser
        self._exit_called = False

    async def __aenter__(self):
        self._playwright_context_manager = PlaywrightContextManager()
        self._playwright_handler = await self._playwright_context_manager.__aenter__()
        self._browser_handler = await self._playwright_handler.chromium.launch()
        return self

    async def __aexit__(self, *args):
        if not self._exit_called:
            await self._browser_handler.close()
            await self._playwright_context_manager.__aexit__()
            self._exit_called = True

    async def _smooth_scroll(self, page: Page):
        scroll_height = await page.evaluate('document.body.scrollHeight')
        pos = 0
        while pos < scroll_height:
            pos += 100
            if pos > scroll_height:
                pos = scroll_height
            await page.evaluate(f'window.scrollTo(0, {pos})')
            await asyncio.sleep(0.2)
        await page.evaluate(f'window.scrollTo(0, 0)')

    async def get_screenshot(self, url, file_path, full_page=True):
        logger.info(f'Started processing {url}.')
        page = await self._browser_handler.new_page()
        try:
            await page.goto(url)
            await self._smooth_scroll(page)
            images = await page.get_by_role('img').all()
            for image in images:
                await image.scroll_into_view_if_needed()
                await expect(image).not_to_have_js_property('naturalWidth', 0)
                width = await image.evaluate('''img => window.getComputedStyle(img).getPropertyValue('width')''')
                if width == "0px":
                    continue
                await expect(image).to_have_js_property('complete', True)
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(5)
            await page.evaluate('window.scrollTo(0, 0)')
            await page.screenshot(path=file_path, full_page=True)
            logger.info(f'Completed taking screenshot of {url}')
        except Exception:
            logger.exception(f'Failed taking screenshot of {url}.')
        finally:
            await page.close()


async def main():
    from urllib.parse import urlparse
    import json

    with open('squarespace/squarespace-templates.json', 'r') as f:
        websites = json.loads(f.read())



    url_list = [website['url'] for website in websites][:10]
    url_list = ["https://clay-demo.squarespace.com"]
    tasks = []
    async with Screenshot() as s:
        for url in url_list:
            file_path = f'{CURRENT_DIR}/screenshots/{urlparse(url).hostname}{"-".join(urlparse(url).path)}.png'
            tasks.append(s.get_screenshot(f'{url}/?nochrome=true', file_path, full_page=True))
        await asyncio.gather(*tasks)



if __name__ == '__main__':
    import time
    logger = logging.getLogger('Screenshot')
    logger.setLevel(logging.INFO)
    log_file = f'{CURRENT_DIR}/logs/screenshot-{time.time()}.log'
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(log_file)
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.ERROR)
    c_handler.setFormatter(logging.Formatter('[%(levelname)s] - %(message)s'))
    f_handler.setFormatter(logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s'))
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)
    asyncio.run(main())
