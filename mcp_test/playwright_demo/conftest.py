import pytest
from playwright.sync_api import sync_playwright


def pytest_addoption(parser):
    parser.addoption(
        "--chrome",
        action="store_true",
        help="使用已安装的 Chrome（通过 Playwright channel=chrome 启动）",
    )
    parser.addoption(
        "--chrome-path",
        action="store",
        default=None,
        help="指定 Chrome 可执行文件路径（优先级高于 --chrome）",
    )
    parser.addoption(
        "--headless",
        action="store_true",
        help="以无头模式运行浏览器",
    )


@pytest.fixture(scope="session")
def launch_options(pytestconfig):
    use_chrome = pytestconfig.getoption("--chrome")
    chrome_path = pytestconfig.getoption("--chrome-path")
    headless = pytestconfig.getoption("--headless")

    options = {"headless": bool(headless)}
    if chrome_path:
        options["executable_path"] = chrome_path
    elif use_chrome:
        options["channel"] = "chrome"
    return options


@pytest.fixture()
def page_ctx(launch_options):
    with sync_playwright() as p:
        browser = p.chromium.launch(**launch_options)
        try:
            context = browser.new_context()
            page = context.new_page()
            yield page
        finally:
            browser.close()


