# multiagent.py (新版，MCP 架構)
import asyncio
import json
from flask_socketio import SocketIO
import pandas as pd

from mcp import ModelClient, ProtocolAgent

# ✅ 多 Agent 分析流程（新版 MCP）
async def process_user_diary(socketio: SocketIO, user_id, user_entries: pd.DataFrame):
    model_client = ModelClient()

    analysis_agent = ProtocolAgent(
        name="analysis_expert",
        role="分析專家",
        model_client=model_client
    )
    coaching_agent = ProtocolAgent(
        name="ai_coach",
        role="AI 教練",
        model_client=model_client
    )

    display_names = {
        "analysis_expert": "分析專家",
        "ai_coach": "AI 教練"
    }

    records = user_entries.to_dict(orient='records')
    if len(records) > 5:
        prompt_records = json.dumps(records[:5], ensure_ascii=False, indent=2, default=str) + "\n... (以下省略)"
    else:
        prompt_records = json.dumps(records, ensure_ascii=False, indent=2, default=str)

    prompt = (
        f"目前正在處理用戶 {user_id} 的面試對話，共 {len(user_entries)} 則。\n"
        f"對話內容（僅顯示前 5 筆）：\n{prompt_records}\n\n"
        "請仔細分析上述對話，找出用戶的應對回答，並根據你的分析給出如何回答得更好，內容必須包含：\n"
        "1. 回答有何不妥，面試官為何不滿意\n"
        "2. 實際可行的回答建議\n"
        "3. AI 教練如何提供個性化互動建議\n\n"
        "請注意：請僅生成全新內容，不要重複上述提示。請在回覆最後直接輸出最終建議，格式必須以『最終建議：』開頭。"
    )

    agents = [analysis_agent, coaching_agent]
    final_recommendation = None

    try:
        for _ in range(6):  # 最多 6 輪互動
            for agent in agents:
                response = await agent.act(prompt)
                display_name = display_names.get(agent.name, agent.name)

                if len(response) > 1500:
                    formatted_text = response[:1500] + "... (內容過長)"
                else:
                    formatted_text = response

                socketio.emit('update', {
                    'message': f"🤖 [{display_name}]：{formatted_text}",
                    'source': agent.name,
                    'tag': 'analysis'
                })

                if "最終建議：" in response:
                    final_recommendation = response.split("最終建議：")[-1].strip()
                    socketio.emit('suggestions', {'suggestions': final_recommendation})
                    return  # 提前結束
    except asyncio.exceptions.CancelledError:
        pass

async def run_multiagent_analysis(socketio: SocketIO, user_id, user_entries: pd.DataFrame):
    socketio.emit('update', {
        'message': '🤖 系統：正在啟動分析專家與 AI 教練的協作...',
        'tag': 'analysis'
    })
    await process_user_diary(socketio, user_id, user_entries)