from flask import Flask, render_template, request, send_file, jsonify
# from mindy_backend.models.daily import get_news_by_category, summarize_news
from models.daliy import get_news_by_category, summarize_news
# from models.interview import save_transcript_to_csv
# from models.interview_analysis import gradio_handler,  generate_pdf  
# import gradio as gr
from models.interview_chat import get_interview_questions, simulate_interview, analyze_answer, save_transcript_to_csv
import os

# In[0]:設定模板目錄為 'mindy_js/templates'
# app = Flask(__name__, template_folder='templates', static_folder='mindy_flask/static')
app = Flask(__name__, )


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
def get_news_summary():
    title = request.args.get('title', '')  # 獲取前端傳來的標題
    if title:
        # 假設 summarize_news 函式已經從標題生成摘要
        summary_data = summarize_news([{"title": title, "content": "這是文章內容"}])
        return jsonify({"summary": summary_data[0]["summary"]})
    else:
        return jsonify({"summary": "未提供標題"})

# In[2]:Interview: 
@app.route('/interview', methods=['GET', 'POST'])
def interview():
    selected_questions = []  # 初始設置為空列表
    responses = []  # 用來儲存面試過程中的回應

    if request.method == 'POST':
        job_title = request.form['job_title'].lower().replace(" ", "_")
        interview_type = request.form['interview_type'].lower()

        # 根據職位與面試類型選擇問題
        selected_questions = get_interview_questions(job_title, interview_type)

        # 若返回的是空值或無效的問題列表，設為空列表
        if selected_questions is None:
            selected_questions = []

        # 定義用戶回答的回調函數
        def user_answer_callback(question):
            # 模擬用戶的回答（你可以修改為從前端收集用戶輸入）
            return "這是我的回答"  # 這裡是硬編碼的模擬回答

        # 模擬面試
        responses = simulate_interview(selected_questions, user_answer_callback)

        # 如果需要對回答進行分析，則調用 analyze_answer 函數進行分析
        for response in responses:
            response['analysis'] = analyze_answer(response['question'], response['response'])

    return render_template('interview.html', questions=selected_questions, responses=responses)
'''
def interview():
    questions = []
    if request.method == 'POST':
        job_title = request.form['job_title'].lower().replace(" ", "_")
        interview_type = request.form['interview_type'].lower()

        # 根據職位與面試類型選擇問題
        selected_questions = get_interview_questions(job_title, interview_type)

        # 返回並顯示選擇的問題，將問題列表傳遞給模板
        questions = selected_questions

    return render_template('interview.html', questions=questions)

'''

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




# In[]: main:
if __name__ == '__main__':
    app.run(debug=True, port=5000)  # 使用端口 5000 啟動 Flask 應用
