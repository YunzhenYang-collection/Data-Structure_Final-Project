import random
import os
from dotenv import load_dotenv
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
# from autogen_ext.agents.web_surfer import MultimodalWebSurfer
import asyncio
from playwright.sync_api import sync_playwright
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
        page.goto(url, timeout=60000, wait_until='load')  # 增加超時時間並等待頁面加載完成
        page.wait_for_timeout(6000)  # 等待頁面加載

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
def summarize_news(news_items):
    summarized_news = []

    for news in news_items:
        try:
            # 解析 HTML 內容
            soup = BeautifulSoup(news['content'], 'html.parser')
            
            # 提取文章標題
            title = soup.find('h2')  # 假設標題位於 <h2> 標籤中
            title = title.text.strip() if title else "無標題"

            # 提取發佈時間
            time = soup.find('time')  # 假設時間位於 <time> 標籤中
            time = time.text.strip() if time else "未知時間"

            # 提取文章內容
            paragraphs = soup.find_all('p')  # 假設內容位於 <p> 標籤中
            content = " ".join([p.text.strip() for p in paragraphs])

            # 使用 Gemini 生成摘要
            summary = summarize_article(content)

            summarized_news.append({
                "title": title,
                "summary": summary,
                "time": time,
                "link": news["url"]
            })
        except Exception as e:
            print(f"生成摘要時發生錯誤：{e}")
            summarized_news.append({
                "title": news["title"],
                "summary": "無法生成摘要",
                "time": "未知時間",
                "link": news.get("url", "無連結")
            })

    return summarized_news

def summarize_article(content):
    """利用 gemini 生成摘要"""
    try:
        # 使用 AutoGen 的 create 方法生成聊天回應，不帶 model 參數
        response = summarizer.create(
            messages=[
                {"role": "system", "content": "你是一個新聞摘要助手，請將以下內容簡短地概括為一句摘要："},
                {"role": "user", "content": content}
            ]
        )
        summary = response["choices"][0]["message"]["content"]
        return summary.strip() if summary else "無摘要"
    except Exception as e:
        print(f"生成摘要時發生錯誤：{e}")
        return "無摘要"