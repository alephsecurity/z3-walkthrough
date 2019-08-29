import asyncio
from pyppeteer import launch


async def get_cookie(url: str) -> int:
    browser = await launch({'headless': True,
                            'args': ['--no-sandbox', '--disable-setuid-sandbox'],
                            'ignoreHTTPSErrors': True});
    page = await browser.newPage()

    await page.goto(url)
    elementList = await page.querySelectorAll('form')
    button = await elementList[0].querySelectorAll('input')
    await button[0].click()

    await page.waitForNavigation();

    cookies = await page.cookies()

    for cookie in cookies:
        if cookie['name'] == 'rememberMe00086':
            return int(cookie['value'])


if __name__ == '__main__':
    url = 'https://localhost:8443/benchmark/weakrand-00/BenchmarkTest00086?BenchmarkTest00086=SafeText'

    cookie_nums = []
    for i in range(1):
        cookie_nums.append(await get_cookie(url=url))
    print(cookie_nums)