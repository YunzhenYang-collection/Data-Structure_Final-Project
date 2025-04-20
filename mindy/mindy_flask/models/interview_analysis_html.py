import os
from datetime import datetime
import gradio as gr
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
import warnings
import pdfkit  # 用於將 HTML 轉換為 PDF

# 載入環境變數並設定 API 金鑰
dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")
print(f".env 檔案的路徑是: {dotenv_path}")
# 忽略警告
warnings.filterwarnings("ignore", message="cmap value too big/small:*")

# 設定中文字型
def get_chinese_font_file() -> str:
    fonts_path = r"C:\\Windows\\Fonts"
    candidates = ["kaiu.ttf", "msyh.ttf", "simhei.ttf"]  # 增加幾個常見的中文字型
    for font in candidates:
        font_path = os.path.join(fonts_path, font)
        if os.path.exists(font_path):
            print("找到系統中文字型：", font_path)
            return os.path.abspath(font_path)
    print("未在系統中找到候選中文字型檔案。")
    return None

# 創建 HTML 表格
def create_html_table(df: pd.DataFrame) -> str:
    """將 DataFrame 轉換為 HTML 表格"""
    html_content = '<html><body><table border="1" style="border-collapse: collapse; width: 100%;">'
    
    # 表頭
    html_content += "<tr>"
    for column in df.columns:
        html_content += f"<th style='padding: 8px; text-align: center;'>{column}</th>"
    html_content += "</tr>"
    
    # 資料行
    for _, row in df.iterrows():
        html_content += "<tr>"
        for item in row:
            html_content += f"<td style='padding: 8px; text-align: center;'>{item}</td>"
        html_content += "</tr>"
    
    html_content += "</table></body></html>"
    return html_content

# 使用 pdfkit 將 HTML 轉換為 PDF
def generate_pdf_from_html(html_content: str, output_filename: str) -> None:
    """將 HTML 內容轉換為 PDF 並保存"""
    # 指定 wkhtmltopdf 執行檔案路徑
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

    # 使用指定的配置生成 PDF
    pdfkit.from_string(html_content, output_filename, configuration=config)
    print(f"PDF 已儲存於 {output_filename}")

# 處理上傳的 CSV 並生成分析報告
def gradio_handler(csv_file, user_prompt):
    if csv_file is not None:
        print("讀取 CSV 檔案")
        df = pd.read_csv(csv_file.name)

        # 為每條對話進行情緒分析並新增到 DataFrame
        df['情緒傾向'] = df['對話'].apply(analyze_sentiment)

        # 分析 CSV 文件內容
        analysis_result = analyze_data(df, user_prompt)

        # 生成 HTML 表格
        html_table = create_html_table(df)

        # 儲存 PDF 至 _report 資料夾
        output_dir = "pdf_report"
        os.makedirs(output_dir, exist_ok=True)
        output_pdf_filename = os.path.join(output_dir, f"generated_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        generate_pdf_from_html(html_table, output_pdf_filename)
        
        return analysis_result, output_pdf_filename
    else:
        return "未上傳 CSV 檔案", None

def analyze_sentiment(text: str) -> str:
    """用 AI 模型進行情緒分析"""
    # 使用模型進行情緒分析，這裡假設返回的是情緒標籤
    response = model.generate_content(f"請分析以下對話的情緒：{text}")
    sentiment = response.text.strip()  # 假設模型回應的是情緒的標籤（正向、中立、負向）
    return sentiment

def analyze_data(df: pd.DataFrame, user_prompt: str) -> str:
    """分析數據並返回分析結果"""
    # 模擬簡單的分析過程，這裡你可以根據實際需求進行自定義分析
    analysis_result = "情緒分析結果：\n"
    
    # 假設分析對話情緒，這裡會基於 CSV 的數據進行分析，並簡單的生成回應
    for index, row in df.iterrows():
        analysis_result += f"{row['時間戳']} - {row['講者']}: {row['對話']} (情緒：{row['情緒傾向']})\n"
    
    analysis_result += "\n回答質量評估：\n"
    for index, row in df.iterrows():
        analysis_result += f"{row['時間戳']} - {row['講者']} 回答的完整性、清晰度和專業性評估\n"
    
    return analysis_result

# 預設的分析指令
default_prompt = """請針對以下面試對話進行分析：

1. **情緒分析**：對每一條面試對話判斷情緒傾向（正向、中立、負向），並標註每條對話的情緒情境。例如，面試官的提問可能是中立的，而面試者的回答可能表現出積極的情緒。

2. **回答質量評估**：根據對話內容，評估面試者的回答質量。可以包括：
   - 完整性：回答是否涵蓋了問題的所有要點。
   - 清晰度：回答是否清晰易懂。
   - 專業性：回答是否具有專業性，並顯示出對面試領域的了解。

3. **關鍵字提取**：識別並提取對話中的關鍵字或專業術語。例如，面試者可能提到某些技能、工具或專案經驗，這些都是面試中的重要信息。

4. **面試官與面試者的互動模式**：分析面試官與面試者之間的互動模式，是否存在明確的問題與回答、面試官是否鼓勵了詳細回答，或者是否存在困難的問題。

5. **回答改進建議**：根據面試者的回答，給出可能的改進建議。這可以包括如何更好地展示自己的專業技能、如何在回答中增強說服力等。

請依照上述格式進行分析，並提供詳細的報告。
"""

# Gradio 介面
with gr.Blocks() as demo:
    gr.Markdown("# 面試對話分析")
    with gr.Row():
        csv_input = gr.File(label="上傳 面試對話 CSV 檔案")
        user_input = gr.Textbox(label="請輸入分析指令", lines=10, value=default_prompt)
    output_text = gr.Textbox(label="回應內容", interactive=False)
    output_pdf = gr.File(label="下載 PDF 報表")
    submit_button = gr.Button("生成報表")
    submit_button.click(fn=gradio_handler, inputs=[csv_input, user_input], outputs=[output_text, output_pdf])

demo.launch()
