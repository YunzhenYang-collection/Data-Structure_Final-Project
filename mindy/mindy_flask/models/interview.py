import os
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.messages import TextMessage
import google.generativeai as genai
from flask import render_template
import csv
from datetime import datetime
import asyncio

# 載入環境變數並設定 API 金鑰
dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)

# 設定 Gemini API 金鑰
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("請在 .env 檔案中設定 GEMINI_API_KEY")

genai.configure(api_key=gemini_api_key)  # 使用 Gemini API 金鑰
model = genai.GenerativeModel("gemini-1.5-pro")  # 指定 Gemini 模型

# 初始化 AssistantAgent 和 UserProxyAgent，並傳遞 model_client
assistant_agent = AssistantAgent(name="Interview_Coach", model_client=model)
user_proxy = UserProxyAgent(name="User")

# 儲存面試逐字稿為 CSV 文件
def save_transcript_to_csv(user_input, ai_feedback):
    # 定義儲存 CSV 的資料夾路徑
    folder_path = "interview_record"
    
    # 確保資料夾存在，如果不存在則創建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # 定義 CSV 檔案路徑
    csv_output_path = os.path.join(folder_path, f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    
    # 寫入 CSV 文件
    with open(csv_output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["User Response", "AI Feedback"])  # CSV 標題
        writer.writerow([user_input, ai_feedback])  # 寫入每一次的對話

    return csv_output_path

# interview_practice_logic 函數
async def interview_practice_logic(request):
    # 如果是 POST 請求，處理用戶輸入的面試情境並生成反饋
    if request.method == 'POST':
        user_input = request.form['user_input']
        
        # 使用 TextMessage 創建用戶消息
        user_message = TextMessage(content=user_input, source="user")  # 設置 source 為 "user"
        
        # 發送用戶消息並獲取 AI 回應（使用 create 方法）
        response = await model.create([user_message])  # 使用 create 方法，假設 model 是異步的
        
        # 假設回應是列表，選取第一個回應
        assistant_response = response[0]
        
        # 打印回應內容以便檢查
        print("Assistant Response:", assistant_response.text)  # 打印 AI 回應
        
        # 儲存面試逐字稿為 CSV
        csv_path = save_transcript_to_csv(user_input, assistant_response.text)
        
        # 返回渲染頁面並顯示 AI 回應，並提供 CSV 下載鏈接
        return render_template('interview.html', feedback=assistant_response.text, user_input=user_input, csv_path=csv_path)

    # 如果是 GET 請求，僅顯示初始頁面，詢問面試情境
    return render_template('interview.html')
