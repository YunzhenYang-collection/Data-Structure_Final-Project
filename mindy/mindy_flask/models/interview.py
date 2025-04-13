from autogen_core import AutoGen
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.messages import TextMessage
from flask import render_template

# 初始化 AutoGen 和代理
agent = AutoGen()
assistant_agent = AssistantAgent(name="Interview Coach")
user_proxy = UserProxyAgent(name="User")

def interview_practice_logic(request):
    # 如果是 POST 請求，處理用戶輸入的面試情境並生成反饋
    if request.method == 'POST':
        user_input = request.form['user_input']
        
        # 使用 AutoGen 代理處理面試情境並生成 AI 回應
        user_message = TextMessage(content=user_input)  # 將用戶的輸入轉換為 TextMessage
        assistant_response = assistant_agent.reply(user_message)  # 模擬 AI 回應
        
        # 返回渲染頁面並顯示 AI 回應
        return render_template('interview.html', feedback=assistant_response.text, user_input=user_input)

    # 如果是 GET 請求，僅顯示初始頁面，詢問面試情境
    return render_template('interview.html')
