import asyncio
import json
import pandas as pd

from mcp import ModelClient, ProtocolAgent

# ✅ 面試專家與面試教練的分析流程
async def process_interview(user_id, user_answers: pd.DataFrame):
    model_client = ModelClient()

    # 創建面試專家和 AI 教練代理
    interview_expert = ProtocolAgent(
        name="interview_expert",
        role="面試專家",
        model_client=model_client
    )
    coaching_agent = ProtocolAgent(
        name="ai_coach",
        role="AI 教練",
        model_client=model_client
    )

    display_names = {
        "interview_expert": "面試專家",
        "ai_coach": "AI 教練"
    }

    # 假設 user_answers 是 DataFrame，其中每一列是用戶的回答
    records = user_answers.to_dict(orient='records')
    if len(records) > 5:
        prompt_records = json.dumps(records[:5], ensure_ascii=False, indent=2, default=str) + "\n... (以下省略)"
    else:
        prompt_records = json.dumps(records, ensure_ascii=False, indent=2, default=str)

    prompt = (
        f"目前正在處理用戶 {user_id} 的面試回答，共 {len(user_answers)} 則。\n"
        f"回答內容（僅顯示前 5 筆）：\n{prompt_records}\n\n"
        "請仔細分析上述回答，找出用戶的情緒與表達模式，並根據你的分析生成一段面試建議，內容必須包含：\n"
        "1. 回答中表達的情緒與思考模式\n"
        "2. 實際可行的改進建議\n"
        "3. AI 教練如何提供個性化的面試建議\n\n"
        "請注意：請僅生成全新內容，不要重複上述提示。請在回覆最後直接輸出最終建議，格式必須以『最終建議：』開頭。"
    )

    agents = [interview_expert, coaching_agent]
    final_recommendation = None

    analysis_results = []

    try:
        for _ in range(6):  # 最多 6 輪互動
            for agent in agents:
                response = await agent.act(prompt)
                display_name = display_names.get(agent.name, agent.name)

                if len(response) > 1500:
                    formatted_text = response[:1500] + "... (內容過長)"
                else:
                    formatted_text = response

                analysis_results.append({
                    'agent': display_name,
                    'response': formatted_text
                })

                if "最終建議：" in response:
                    final_recommendation = response.split("最終建議：")[-1].strip()
                    analysis_results.append({'agent': '最終建議', 'response': final_recommendation})
                    return analysis_results  # 提前結束
    except asyncio.exceptions.CancelledError:
        pass

    return analysis_results  # 返回最終的分析結果


async def run_interview_analysis(user_id, user_answers: pd.DataFrame):
    """
    啟動分析並返回最終結果
    """
    return await process_interview(user_id, user_answers)
