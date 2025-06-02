import os
from dotenv import load_dotenv

load_dotenv()  # 讀取當前目錄下的 .env 檔案

gemini_key = os.getenv("GEMINI_API_KEY")
print("GEMINI_API_KEY:", gemini_key)


print("\ngoogle.generativeai.genai :")
import google.generativeai as genai
print(genai.__version__)  # 如果沒有此屬性，代表版本太舊
print(dir(genai))        # 看看有沒有 chat 屬性

print("\ngoogle :")
import google
print(dir(google))        # 看看有沒有 generativeai 屬性

print("\ngoogle. genai :")
from google import genai
print(dir(genai))