# import pathlib
import textwrap

import google.generativeai as genai
import random

from IPython.display import display
from IPython.display import Markdown

import os
from dotenv import load_dotenv
from datetime import datetime
import csv

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# 載入環境變數並設定 API 金鑰
dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)

# 設定 Gemini API 金鑰
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("請在 .env 檔案中設定 GEMINI_API_KEY")

genai.configure(api_key=gemini_api_key)  # 使用 Gemini API 金鑰

# 選擇您想要使用的模型
model = genai.GenerativeModel('gemini-2.0-flash')  # 使用 Gemini 2.0 模型
# model = genai.GenerativeModel('gemini-1.5-pro')  # 使用 Gemini 1.5 模型

# 面試問題庫 
question_bank_zh = {
    "general": [
        "請簡單介紹一下你自己。",
        "你為什麼對我們這個職位感興趣？",
        "你最大的優勢與缺點是什麼？",
        "你期望的薪資是多少？",
        "你還有什麼問題想問我嗎？"
    ],
    "behavioral": [
        "請簡單介紹一下你自己。",
        "請描述一次你領導團隊克服挑戰的經歷。",
        "請分享一次你犯了錯誤並從中學習的經歷。",
        "請描述一次你與同事意見不合，你是如何解決的？",
        "請分享一次你如何在壓力下完成工作的經歷。",
        "請描述一次你設定並達成一個具有挑戰性目標的經歷。"
    ],
    "technical_software_engineer": [
        "請簡單介紹一下你自己。",
        "請解釋一下什麼是物件導向程式設計的原則？",
        "你熟悉哪些資料結構和演算法？請舉例說明它們的應用。",
        "請解釋一下 RESTful API 的概念。",
        "你使用過哪些版本控制系統？請描述你的工作流程。",
        "請描述一個你參與過的複雜軟體專案，你在其中扮演了什麼角色？"
    ],
    "technical_data_scientist": [
        "請解釋一下什麼是偏差-變異權衡（Bias-Variance Tradeoff）？",
        "你熟悉哪些機器學習演算法？請說明它們的優缺點。",
        "請描述一個你使用過的資料分析或機器學習專案，你是如何處理資料和建立模型的？",
        "你熟悉哪些資料庫和 SQL？",
        "請解釋一下什麼是過擬合（Overfitting）和欠擬合（Underfitting），以及如何避免它們？"
    ]
}

question_bank_en = { 
    "general": [
        "Please briefly introduce yourself.",
        "Why are you interested in this position?",
        "What are your greatest strengths and greatest weaknesses?",
        "What are your salary expectations?",
        "Do you have any questions for me?"
    ],
    "behavioral": [
        "Describe a time you led a team to overcome a challenge.",
        "Share an experience where you made a mistake and learned from it.",
        "Describe a time you disagreed with a colleague. How did you resolve it?",
        "Share an experience where you had to work under pressure.",
        "Describe a time you set and achieved a challenging goal."
    ],
    "technical_software_engineer": [
        "Please explain the principles of object-oriented programming.",
        "What data structures and algorithms are you familiar with? Please give examples of their applications.",
        "Please explain the concept of RESTful APIs.",
        "What version control systems have you used? Describe your workflow.",
        "Describe a complex software project you were involved in. What role did you play?"
    ],
    "technical_data_scientist": [
        "Please explain the Bias-Variance Tradeoff.",
        "What machine learning algorithms are you familiar with? Explain their advantages and disadvantages.",
        "Describe a data analysis or machine learning project you worked on. How did you handle the data and build the model?",
        "What databases and SQL are you familiar with?",
        "Please explain overfitting and underfitting, and how to avoid them."
    ]
}

# print("歡迎使用模擬面試機器人！")

# 獲取使用者輸入的情境
# job_title = input("請輸入您要模擬面試的職位（例如：軟體工程師、資料科學家、行銷專員）：").lower().replace(" ", "_")
# interview_type = input("請輸入面試類型（例如：一般面試、行為面試、技術面試）：").lower()

# 根據職位和面試類型選擇問題
def get_interview_questions(job_title, interview_type):
    selected_questions = []
    num_general_questions = 3

    if "技術" in interview_type:
        if job_title == "軟體工程師":
            selected_questions.extend(question_bank_zh.get("technical_software_engineer", []))
        else:
            selected_questions.extend(random.sample(question_bank_zh.get("general", []), num_general_questions))
    elif "行為" in interview_type:
        selected_questions.extend(question_bank_zh.get("behavioral", []))
        selected_questions.extend(random.sample(question_bank_zh.get("general", []), num_general_questions))
    else:
        selected_questions.extend(question_bank_zh.get("general", []))

    return selected_questions

# 模擬面試函數
def simulate_interview(selected_questions, user_answer_callback):
    chat = model.start_chat(history=[])
    question_index = 0
    responses = []
    while question_index < len(selected_questions):
        interviewer_question = selected_questions[question_index]
        user_answer = user_answer_callback(interviewer_question)
        
        if user_answer.lower() == '結束':
            break
        
        response = chat.send_message(f"{user_answer}\n\n請以中文回答。")
        print(f"Question: {interviewer_question}")
        print(f"Response: {response.text}")  # 打印模型回應
        responses.append({"question": interviewer_question, "response": response.text})
        question_index += 1
    return responses

# 進行手動問題與回答分析
def analyze_answer(custom_question, custom_answer):
    analysis_prompt = f"""請分析以下面試問題的回答，並提供中文的改進建議。
    問題：{custom_question}
    回答：{custom_answer}

    請從以下幾個方面進行分析：
    - 回答是否清晰且易於理解？
    - 回答是否完整地回答了問題？
    - 回答是否與問題相關？
    - 回答中是否有使用具體的例子或證據來支持觀點？（如果適用）
    - 回答的語氣和表達是否專業？

    請提供簡潔明瞭的中文分析和建議。
    """
    try:
        analysis_response = model.generate_content(analysis_prompt)
        return analysis_response.text
    except Exception as e:
        return f"分析時發生錯誤：{e}"
    
# 儲存面試逐字稿為 CSV 文件
def save_transcript_to_csv(user_input, ai_feedback):
    # 定義儲存 CSV 的資料夾路徑
    folder_path = "reference"
    
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