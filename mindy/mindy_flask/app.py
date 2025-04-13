from flask import Flask, render_template, request, send_file, jsonify
# from mindy_backend.models.daily import get_news_by_category, summarize_news
from models.daliy import get_news_by_category, summarize_news
from models.interview import save_transcript_to_csv, interview_practice_logic
from models.interview_analysis import gradio_handler


# 設定模板目錄為 'mindy_js/templates'
app = Flask(__name__, template_folder='../mindy_js/templates')

@app.route('/')
def index():
    return render_template('index.html')  # 渲染 index.html 頁面

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


@app.route('/generate_transcript', methods=['POST'])
def generate_transcript():
    user_input = request.form['user_input']  # 用戶的面試情境
    ai_feedback = "這是 AI 的回應"  # 這裡根據用戶輸入生成 AI 的反饋
    # 儲存面試內容為 CSV
    csv_path = save_transcript_to_csv(user_input, ai_feedback)
    # 返回 CSV 文件以供下載
    return send_file(csv_path, as_attachment=True)

@app.route('/analyze_interview', methods=['GET'])
def analyze_interview():
    return render_template('analyze_interview.html')  # 渲染分析頁面

@app.route('/gradio_analysis', methods=['POST', 'GET'])
def gradio_analysis():
    if request.method == 'POST':
        csv_file = request.files['csv_file']  # 從表單中取得 CSV 文件
        user_prompt = request.form['user_prompt']  # 從表單中取得分析指令
        
        # 使用 gradio_handler 來處理上傳的 CSV 文件並生成結果
        result_text, pdf_path = gradio_handler(csv_file, user_prompt)

        # 返回分析結果和 PDF 路徑，讓用戶下載
        return render_template('analysis_result.html', result=result_text, pdf_path=pdf_path)
    
    # 頁面加載時顯示分析頁面，並讓用戶上傳 CSV 文件
    return render_template('analyze_interview.html')

@app.route('/interview_practice', methods=['GET', 'POST'])
def interview_practice():
    # 呼叫 interview_practice_logic 函數來處理 POST 或 GET 請求
    return interview_practice_logic(request)

if __name__ == '__main__':
    app.run(debug=True)
