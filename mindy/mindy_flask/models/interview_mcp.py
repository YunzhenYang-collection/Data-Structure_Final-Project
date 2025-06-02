# interview_mcp.py
import os
import asyncio
from dotenv import load_dotenv
from google.genai import client as genai_client

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY 未設定")

class ModelClient:
    def __init__(self, model="gemini-2.0-flash"):
        self.model = model
        self.client = genai_client.Client(api_key=GEMINI_API_KEY)

    async def generate(self, messages: list):
        prompt = "\n".join(messages)
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text.strip()

class ProtocolAgent:
    def __init__(self, name, role, model_client: ModelClient, initial_prompt=None):
        self.name = name
        self.role = role
        self.model_client = model_client
        self.history = []
        if initial_prompt:
            # 初始化時放入預設背景+對話
            self.history.append(f"[system] {initial_prompt}")

    async def act(self, user_input: str):
        self.history.append(f"[user] {user_input}")
        context = self.history.copy()

        response = await self.model_client.generate(context)
        self.history.append(f"[{self.name}] {response}")
        return response

# 預設面試專家背景及起始對話
default_initial_prompt = (
    "你是面試專家，請扮演一位專業面試教練，"
    "會引導應徵者作自我介紹並根據回答持續提問。"
    "請開始面試，使用者第一個輸入皆為自我介紹。"
)

# 建立 ModelClient
model_client = ModelClient()

# 建立兩個 Agent，帶入初始 prompt 只給 coach
agent1 = ProtocolAgent("ai_coach", "AI 教練", model_client, initial_prompt=default_initial_prompt)
agent2 = ProtocolAgent("analysis_expert", "對話分析專家", model_client)

def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        return future.result()
    else:
        return asyncio.run(coro)

def handle_chat(user_message: str) -> tuple[str, str]:
    # ai_coach 根據用戶訊息產生面試回覆
    reply = run_async(agent1.act(user_message))

    # analysis_expert 根據 coach 回覆給出建議
    # 這裡用 coach 最新回覆作為分析內容
    analysis = run_async(agent2.act(reply))

    return reply, analysis
