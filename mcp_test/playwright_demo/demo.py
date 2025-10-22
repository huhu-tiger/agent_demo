import pytest


def test_baidu_search_mcp(page_ctx):
    page = page_ctx
    page.goto("https://www.baidu.com", wait_until="domcontentloaded")

    # 使用页面提供的搜索框 id
    page.wait_for_selector('#chat-textarea')
    search_input = page.locator('#chat-textarea')
    search_input.fill("MCP")
    search_input.press("Enter")

    page.wait_for_load_state("domcontentloaded")

    # 等待 5 秒后退出
    page.wait_for_timeout(5000)

    title = page.title()
    assert "MCP" in title or "百度搜索" in title


