import random
import os
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
# from autogen_ext.agents.web_surfer import MultimodalWebSurfer
import asyncio
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# 載入 .env 檔案中的環境變數
load_dotenv()

# 獲取 GEMINI API 金鑰
gemini_api_key = os.environ.get("GEMINI_API_KEY")
if not gemini_api_key:
    print("請檢查 .env 檔案中的 GEMINI_API_KEY。")
    exit(1)

# 初始化 OpenAIChatCompletionClient 並指定模型
summarizer = OpenAIChatCompletionClient(
    model="gemini-2.0-flash",  # 使用 gemini-2.0-flash 模型
    api_key=gemini_api_key,
)

# 設置 Yahoo News 類別對應的 URL 和標籤
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

# 使用 Playwright 抓取新聞標題
def fetch_news_by_topic(topic_key):
    url = TOPIC_URLS.get(topic_key)
    if not url:
        return []

    headlines = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # headless=True 不顯示瀏覽器界面
        page = browser.new_page()
        page.goto(url)
        page.goto(url, timeout=12000, wait_until='load')  # 增加超時時間並等待頁面加載完成
        page.wait_for_timeout(12000)  # 等待頁面加載       
               

        try:
            elements = page.locator("h3 > a")
            # 抓取最多 15 條新聞
            for el in elements.all()[:15]:
                text = el.text_content()
                href = el.get_attribute("href")
                if text and href:
                    full_url = f"https://tw.news.yahoo.com{href}" if href.startswith("/") else href
                    headlines.append({"title": text.strip(), "url": full_url})  # 添加 url
        except Exception as e:
            print("⚠️ 抓取失敗:", e)

        browser.close()

    # 隨機選擇 10 條新聞
    selected_news = random.sample(headlines, 10) if len(headlines) >= 10 else headlines

    print(f"[DEBUG] 抓到 {len(headlines)} 條新聞，選擇 {len(selected_news)} 條新聞")
    return selected_news
def get_news_by_category(category):
    return fetch_news_by_topic(category)

# 直接根據類別同步取得新聞
async def summarize_news(news_items):
    summarized_news = []

    async with async_playwright() as p:
        for news in news_items:
            url = news.get('url')
            if not url:
                print(f"跳過無 URL 的新聞: {news}")
                continue  # 如果沒有 URL，跳過該新聞

            try:
                # 使用 Playwright 加載頁面
                browser = await p.chromium.launch(headless=True)  # headless=True 不顯示瀏覽器界面
                page = await browser.new_page()

                # 進入新聞頁面
                await page.goto(url, timeout=60000, wait_until='domcontentloaded')  # 等待頁面加載

                # 等待 caas-body 元素加載完成
                await page.wait_for_selector('div.caas-body', timeout=30000)

                # 抓取 caas-body 內的所有 <p> 標籤內容
                paragraphs = await page.locator('div.caas-body p').all_text_contents()

                # 確保抓取到內容
                if paragraphs:
                    print(f"成功抓取到內容：{paragraphs}")
                else:
                    print("content 為空，未能抓取到有效內容")
                    paragraphs = ["無法抓取內容"]

                # 將抓取的段落合併成摘要
                summary = " ".join(paragraphs[:5])  # 假設取前5段作為摘要

                # 提取標題和時間
                title = news.get("title", "無標題")
                time = news.get("time", "未知時間")

                summarized_news.append({
                    "title": title,
                    "summary": summary,
                    "time": time,
                    "link": url
                })

                await browser.close()  # 關閉瀏覽器

            except Exception as e:
                print(f"生成摘要時發生錯誤：{e}")
                summarized_news.append({
                    "title": news.get("title", "無標題"),
                    "summary": "無法生成摘要",
                    "time": "未知時間",
                    "link": url
                })

    return summarized_news


async def summarize_article(content):
    """利用 gemini 生成摘要"""
    try:
        # 使用 AutoGen 的 create 方法生成聊天回應
        response = await summarizer.create(
            messages=[
                {"role": "system", "content": "你是一個新聞摘要助手，請閱讀新聞內容以後提取有用的資訊做成一段5句話以內的摘要："},
                {"role": "user", "content": content}
            ]
        )

        # 打印返回的 response 以便調試
        print(f"生成摘要的 response: {response}")

        # 確保返回格式正確並提取摘要
        if isinstance(response, dict):
            # 如果返回的是字典類型，嘗試處理它
            if "choices" in response and len(response["choices"]) > 0:
                summary = response["choices"][0].get("message", {}).get("content", "")
                if summary:
                    return summary.strip()
                else:
                    return "摘要內容為空"
            else:
                return "無法生成摘要，未找到有效的選擇"
        else:
            return "返回的格式不正確"

    except Exception as e:
        print(f"生成摘要時發生錯誤：{e}")
        return "無摘要"