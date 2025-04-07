from playwright.sync_api import sync_playwright

TOPIC_URLS = {
    "tech": "https://tw.news.yahoo.com/tech-news/",
    "business": "https://tw.news.yahoo.com/finance/",
    "world": "https://tw.news.yahoo.com/world/"
}

TOPIC_LABELS = {
    "tech": "科學與科技",
    "business": "商業",
    "world": "國際"
}

def fetch_news_by_topic(topic_key):
    url = TOPIC_URLS.get(topic_key)
    if not url:
        return []

    headlines = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_timeout(2000)

        try:
            elements = page.locator("h3 > a")
            for el in elements.all()[:5]:
                text = el.text_content()
                href = el.get_attribute("href")
                if text and href:
                    full_url = f"https://tw.news.yahoo.com{href}" if href.startswith("/") else href
                    headlines.append({"title": text.strip(), "url": full_url})
        except Exception as e:
            print("⚠️ 抓取失敗:", e)

        browser.close()

    print(f"[DEBUG] 抓到 {len(headlines)} 則標題")
    return headlines