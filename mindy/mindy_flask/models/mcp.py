# models/mcp.py
import os
import asyncio
import time
from dotenv import load_dotenv
from google.genai import client as genai_client

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY 未設定於環境變數")

class ModelClient:
    def __init__(self, model="gemini-2.5-pro-exp-03-25"):
        self.model = model
        self.client = genai_client.Client(api_key=GEMINI_API_KEY)

    async def generate(self, messages: list, retry=5, base_delay=5):
        content = "\n".join(messages)
        for attempt in range(retry):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=content
                )
                return response.text.strip()
            except Exception as e:
                if "RESOURCE_EXHAUSTED" in str(e):
                    delay = base_delay * (2 ** attempt)  # 指數退避
                    print(f"配額超限，等待 {delay} 秒後重試 {attempt+1}/{retry}")
                    await asyncio.sleep(delay)
                else:
                    raise
        raise RuntimeError("多次重試後仍無法完成請求")


class ContextManager:
    def __init__(self):
        self.history = []

    def add_message(self, role, content):
        self.history.append(f"[{role}] {content}")

    def get_context(self):
        return list(self.history)

class ProtocolAgent:
    def __init__(self, name, role, model_client: ModelClient):
        self.name = name
        self.role = role
        self.model_client = model_client
        self.context_manager = ContextManager()

    async def act(self, input_text):
        self.context_manager.add_message(self.role, input_text)
        context = self.context_manager.get_context()
        try:
            response = await self.model_client.generate(context)
        except Exception as e:
            print(f"[{self.name}] 呼叫失敗：{e}")
            response = f"⚠️ 請求失敗：{e}"
        self.context_manager.add_message(self.name, response)
        return response
