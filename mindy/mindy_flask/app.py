from flask import Flask, render_template, request, send_file, jsonify, url_for, send_from_directory
import threading
from models.daliy import fetch_news_by_topic, get_news_by_category, summarize_news
from models.interview import save_transcript_to_csv
from models.interview_analysis import gradio_handler,  generate_pdf  
from werkzeug.utils import secure_filename
# from models.interview_analysis_html import analyze_interview 
# import gradio as gr
from models.interview_chat import get_interview_questions, simulate_interview, analyze_answer, save_transcript_to_csv
from flask_mysqldb import MySQL
import os
from dotenv import load_dotenv
import asyncio
# from models.interview_mcp import process_interview_answer, run_multiagent_analysis
import google.generativeai as genai
# from models.mcp import ProtocolAgent 
from models.reminders import get_all_reminders, add_reminder, delete_reminder

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

gemini_key = os.getenv("GEMINI_API_KEY")
print("GEMINI_API_KEY:", gemini_key)
    
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

# 建立模型實例
model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')

# ✅ 封裝 autogen client
class GeminiChatCompletionClient:
    def __init__(self, model_instance=None):
        # 預設用外部 model 實例，也可以自訂
        self.model = model_instance if model_instance else genai.GenerativeModel('gemini-1.5-flash-8b')
        self.model_info = {"vision": False}

    async def create(self, messages, **kwargs):
        parts = []
        for m in messages:
            # 支援 dict 或物件格式
            if hasattr(m, 'content'):
                parts.append(str(m.content))
            elif isinstance(m, dict) and 'content' in m:
                parts.append(str(m['content']))
        content = "\n".join(parts)
        # ⚠️ generate_content() 不是 async，這裡你要考慮用 ThreadPoolExecutor 包起來，否則直接呼叫會變同步
        response = self.model.generate_content(content)
        return type("Response", (), {
            "text": response.text,
            "content": response.text,
            "usage": {
                "prompt_tokens": {"value": 0},
                "completion_tokens": {"value": 0}
            }
        })



from models.interview_mcp import handle_chat # AI Agent 聊天函式 interface

# 建立 Gemini chat client
# model_client = GeminiChatCompletionClient(model)

@app.route('/interview')
def interview():
    return render_template('interview_mcp.html')

@app.route('/interview/chat', methods=['POST'])
def interview_chat():
    data = request.get_json()
    user_msg = data.get('message', '').strip()
    if not user_msg:
        return jsonify({'reply': '', 'analysis': ''})

    try:
        reply, analysis = handle_chat(user_msg)
        return jsonify({'reply': reply, 'analysis': analysis})
    except Exception as e:
        return jsonify({'reply': f"⚠️ 發生錯誤：{str(e)}", 'analysis': ''})


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
#In[2]:Interview Analysis:

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

# 配置上傳文件夾及允許的文件擴展名
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 確保上傳文件夾存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 檢查文件擴展名是否被允許
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/interview_analysis', methods=['GET', 'POST'])
def interview_analysis():
    if request.method == 'POST':
        # 處理文件上傳
        if 'csv_file' not in request.files:
            return '沒有檔案', 400
        file = request.files['csv_file']
        if file.filename == '':
            return '沒有選擇檔案', 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            user_prompt = request.form['user_prompt']
            # 執行分析
            result = analyze_interview(file_path, user_prompt)
            # 返回結果
            return render_template('analysis_result.html', result=result)

    return render_template('analysis.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# In[3]:Saving Jar

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

#In[] Reminders:

# 取得所有提醒事項
@app.route('/reminders', methods=['GET'])
def get_reminders():
    return jsonify(get_all_reminders())

# 新增提醒事項
@app.route('/reminders', methods=['POST'])
def add_reminder_api():
    data = request.json
    content = data.get('content')
    date = data.get('date')
    if not content or not date:
        return jsonify({'error': '請提供提醒內容與日期'}), 400
    new_reminder = add_reminder(content, date)
    return jsonify(new_reminder), 201

# 刪除提醒事項
@app.route('/reminders/<rid>', methods=['DELETE'])
def delete_reminder_api(rid):
    delete_reminder(rid)
    return jsonify({'success': True})


# In[]: main:
if __name__ == '__main__':

    app.run(debug=True, port=5000)  # 使用端口 5000 啟動 Flask 應用
