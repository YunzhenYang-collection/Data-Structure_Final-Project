from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.messages import TextMessage
from flask import render_template
import csv
import os
from datetime import datetime

# 初始化 OpenAI 模型客戶端
model_client = OpenAIChatCompletionClient(model="gpt-4")  # 或者選擇你需要的模型

# 初始化 AssistantAgent 和 UserProxyAgent，並傳遞 model_client
assistant_agent = AssistantAgent(name="Interview Coach", model_client=model_client)
user_proxy = UserProxyAgent(name="User")

# 儲存面試逐字稿為 CSV 文件
def save_transcript_to_csv(user_input, ai_feedback):
    # 定義 CSV 檔案路徑
    csv_output_path = f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # 寫入 CSV 文件
    with open(csv_output_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["User Response", "AI Feedback"])  # CSV 標題
        writer.writerow([user_input, ai_feedback])  # 寫入每一次的對話

    return csv_output_path

def interview_practice_logic(request):
    # 如果是 POST 請求，處理用戶輸入的面試情境並生成反饋
    if request.method == 'POST':
        user_input = request.form['user_input']
        
        # 使用 AssistantAgent 處理用戶輸入的面試情境並生成 AI 回應
        user_message = TextMessage(content=user_input)  # 將用戶的輸入轉換為 TextMessage
        assistant_response = assistant_agent.reply(user_message)  # 模擬 AI 回應
        
        # 儲存面試逐字稿為 CSV
        csv_path = save_transcript_to_csv(user_input, assistant_response.text)
        
        # 返回渲染頁面並顯示 AI 回應，並提供 CSV 下載鏈接
        return render_template('interview.html', feedback=assistant_response.text, user_input=user_input, csv_path=csv_path)

    # 如果是 GET 請求，僅顯示初始頁面，詢問面試情境
    return render_template('interview.html')
