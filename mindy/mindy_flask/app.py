from flask import Flask, render_template, request, send_file, jsonify
import threading
from models.daliy import fetch_news_by_topic, get_news_by_category, summarize_news
# from models.interview import save_transcript_to_csv
from models.interview_analysis import gradio_handler,  generate_pdf  
# import gradio as gr
from models.interview_chat import get_interview_questions, simulate_interview, analyze_answer, save_transcript_to_csv
from flask_mysqldb import MySQL
import os
from dotenv import load_dotenv
import asyncio
from models.interview_mcp import process_interview_answer, run_multiagent_analysis
import google.generativeai as genai
from models.mcp import ProtocolAgent  

# In[0]:Initialization:
load_dotenv()

# app = Flask(__name__, template_folder='templates', static_folder='mindy_flask/static')
app = Flask(__name__, )

# .env path
env_file_path = os.path.join(os.getcwd(), '.env')

if os.path.exists(env_file_path):
    print(f".env path: {env_file_path}")
else:
    print(".env file not found.")
    
# DB config

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

db_host = os.getenv("DB_HOST")
print(f"DB_HOST：{db_host}")


@app.route('/')
def index():
    return render_template('index.html')  # 渲染 index.html 頁面

# In[1]:Daily Digest:
@app.route('/get_daily_digest', methods=['GET'])
def get_daily_digest():
    category = request.args.get('category', 'tech')  # 默認為 'tech'，如果未選擇分類則顯示科技類
    # 抓取新聞
    news_items = get_news_by_category(category)

    # 只返回新聞標題和連結
    news_list = [{"title": news["title"], "link": news["url"]} for news in news_items]

    return jsonify(news_list)  # 返回新聞標題和連結

@app.route('/get_news_summary', methods=['GET'])
async def get_news_summary():
    title = request.args.get('title')  # 從查詢字符串獲取 title
    
    # 根據 title 查找相關新聞
    news_items = fetch_news_by_title(title)  # 假設你有根據 title 查找新聞的功能

    # 確保有抓取到新聞
    if not news_items:
        return jsonify({"error": "No news found"}), 404  # 如果沒有新聞則返回 404

    # 呼叫 summary 函數來生成摘要
    summary_data = await summarize_news(news_items)  # 使用 await 等待異步結果

    # 檢查 summary_data 是否有內容
    if not summary_data:
        return jsonify({"error": "No summary found"}), 404  # 如果沒有摘要返回 404

    # 返回摘要
    return jsonify({"summary": summary_data[0]["summary"]})


# In[2]:Interview: 
@app.route('/interview', methods=['GET', 'POST'])
def interview():
    selected_questions = []  # 初始設置為空列表
    responses = []  # 用來儲存面試過程中的回應
    job_title = ''  # 設定默認為空字串
    interview_type = ''  # 設定默認為空字串

    if request.method == 'POST':
        job_title = request.form['job_title'].lower().replace(" ", "_")
        interview_type = request.form['interview_type'].lower()

        print("job_title:", job_title)
        print("interview_type:", interview_type)

        # 根據職位與面試類型選擇問題
        selected_questions = get_interview_questions(job_title, interview_type)

        # 若返回的是空值或無效的問題列表，設為空列表
        if selected_questions is None:
            selected_questions = []

        # 這裡會從前端表單提交中收集用戶的回答
        def user_answer_callback(question):
            # 從表單中收集用戶的回答
            return request.form.get(f"answer_{question}", "")  # 假設前端會提交 "answer_question" 的字段


        # 模擬面試
        responses = simulate_interview(selected_questions, user_answer_callback)

        # 如果需要對回答進行分析，則調用 analyze_answer 函數進行分析
        for response in responses:
            response['analysis'] = analyze_answer(response['question'], response['response'])

    # 渲染模板並傳遞問題、回應和選擇的職位與面試類型
    return render_template('interview.html', questions=selected_questions, responses=responses, job_title=job_title, interview_type=interview_type)


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
#print(GEMINI_API_KEY)

# ✅ 建立 Gemini 客戶端與模型
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# ✅ 封裝 autogen client
class GeminiChatCompletionClient:
    def __init__(self, model="gemini-1.5-flash-8b"):
        self.model = model
        self.model_info = {"vision": False}

    async def create(self, messages, **kwargs):
        parts = []
        for m in messages:
            if hasattr(m, 'content'):
                parts.append(str(m.content))
            elif isinstance(m, dict) and 'content' in m:
                parts.append(str(m['content']))
        content = "\n".join(parts)
        response = client.models.generate_content(
            model=self.model,
            contents=content
        )
        return type("Response", (), {
            "text": response.text,
            "content": response.text,
            "usage": {
                "prompt_tokens": {"value": 0},
                "completion_tokens": {"value": 0}
            }
        })

model_client = GeminiChatCompletionClient()

@app.route('/interview_mcp', methods=['GET', 'POST'])
def interview_mcp():
    selected_questions = []  # 初始設置為空列表
    responses = []  # 用來儲存面試過程中的回應
    job_title = ''  # 設定默認為空字串
    interview_type = ''  # 設定默認為空字串

    if request.method == 'POST':
        job_title = request.form['job_title'].lower().replace(" ", "_")  # 獲取職位
        interview_type = request.form['interview_type'].lower()  # 獲取面試類型

        # 根據職位與面試類型選擇問題
        selected_questions = get_interview_questions(job_title, interview_type)

        # 若返回的是空值或無效的問題列表，設為空列表
        if selected_questions is None:
            selected_questions = []

        # 定義用戶回答的回調函數
        def user_answer_callback(question):
            # 從表單中收集用戶的回答
            return request.form.get(f"answer_{question}", "")  # 假設前端會提交 "answer_question" 的字段

        # 模擬面試
        responses = simulate_interview(selected_questions, user_answer_callback)

        # 分析用戶的回答
        for idx, response in enumerate(responses):
            # 假設每個回答的分析結果會存放到 analysis 中
            analysis_results = process_interview_answer(response['response'])  # 使用面試教練進行分析

            # 進一步將分析結果與建議添加到回應
            response['analysis'] = analysis_results['analysis']
            response['advice'] = analysis_results['advice']

    # 渲染模板並傳遞問題、回應和選擇的職位與面試類型
    return render_template('interview_mcp.html', questions=selected_questions, responses=responses, job_title=job_title, interview_type=interview_type)


@app.route('/generate_transcript', methods=['POST'])
def generate_transcript():
    user_input = request.form['user_input']  # 用戶的面試情境
    ai_feedback = "這是 AI 的回應"  # 假設這是AI的回應，實際應該根據用戶的回答來生成
    # 儲存面試內容為 CSV
    csv_path = save_transcript_to_csv(user_input, ai_feedback)
    
    # 返回 CSV 文件以供下載
    # return send_file(csv_path, as_attachment=True)
    return send_file(csv_path, as_attachment=True, download_name=os.path.basename(csv_path))

'''
@app.route('/analyze_interview', methods=['GET'])
def analyze_interview():
    return render_template('analyze_interview.html')  # 渲染分析頁面
'''
'''
@app.route('/gradio_analysis', methods=['GET', 'POST'])
def gradio_analysis():
    # 這個路由會觸發 Gradio 界面的顯示
    with gr.Blocks() as demo:
        gr.Markdown("# 面試對話分析")
        with gr.Row():
            csv_input = gr.File(label="上傳 面試對話 CSV 檔案")
            user_input = gr.Textbox(label="請輸入分析指令", lines=10)
        output_text = gr.Textbox(label="回應內容", interactive=False)
        output_pdf = gr.File(label="下載 PDF 報表")
        submit_button = gr.Button("生成報表")
        submit_button.click(fn=gradio_handler, inputs=[csv_input, user_input], outputs=[output_text, output_pdf])
    
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)  # 確保這個端口是可控的
    return "Gradio 介面正在啟動..."  # 你可以根據需要自定義這個回應

'''

@app.route('/gradio_analysis', methods=['GET', 'POST'])
def gradio_analysis():
    if request.method == 'POST':
        # 這裡處理 CSV 上傳和分析指令
        csv_file = request.files['csv_file']
        user_prompt = request.form['user_prompt']
        
        # 使用 gradio_handler 來處理上傳的 CSV 文件並生成結果
        result_text, pdf_path = gradio_handler(csv_file, user_prompt)

        # 返回分析結果和 PDF 路徑，讓用戶下載
        return render_template('analysis_result.html', result=result_text, pdf_path=pdf_path)
    
    # 頁面加載時顯示分析頁面，並讓用戶上傳 CSV 文件
    return render_template('gradio_analysis.html')  # 返回 Gradio 分析頁面

# In[2]:Saving Jar

# MySQL
app.config['MYSQL_HOST'] = DB_HOST
app.config['MYSQL_USER'] = DB_USER
app.config['MYSQL_PASSWORD'] = DB_PASSWORD
app.config['MYSQL_DB'] = DB_NAME
mysql = MySQL(app)

@app.route('/add_saving_goal', methods=['POST'])
def add_saving_goal():
    # 從表單獲取資料
    goal = request.form['goal']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    goal_amount = request.form['goal_amount']
    daily_contribution = request.form['daily_contribution']

    # 資料庫操作：新增儲蓄目標
    cursor = mysql.connection.cursor()
    try:
        cursor.execute('''
            INSERT INTO saving_jar (goal, start_date, end_date, goal_amount, daily_contribution)
            VALUES (%s, %s, %s, %s, %s)
        ''', (goal, start_date, end_date, goal_amount, daily_contribution))

        # 提交變更
        mysql.connection.commit()
        return jsonify({"message": "Saving goal added successfully!"})

    except Exception as e:
        # 發生錯誤時rollback
        mysql.connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        # 關閉游標
        cursor.close()


# In[]: main:
if __name__ == '__main__':
    app.run(debug=True, port=5000)  # 使用端口 5000 啟動 Flask 應用
