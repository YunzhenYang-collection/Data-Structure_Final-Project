import gradio as gr
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
import os

# 載入環境變數並設定 API 金鑰
dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

# 設定預設的分析提示（default_prompt）
default_prompt = """請針對以下面試對話進行分析：

1. 情緒分析：對每一條面試對話判斷情緒傾向（正向、中立、負向），並標註每條對話的情緒情境。例如，面試官的提問可能是中立的，而面試者的回答可能表現出積極的情緒。
   
2. 回答質量評估：根據對話內容，評估面試者的回答質量。可以包括：
   - 完整性：回答是否涵蓋了問題的所有要點。
   - 清晰度：回答是否清晰易懂。
   - 專業性：回答是否具有專業性，並顯示出對面試領域的了解。
   
3. 關鍵字提取：識別並提取對話中的關鍵字或專業術語。例如，面試者可能提到某些技能、工具或專案經驗，這些都是面試中的重要信息。

4. 面試官與面試者的互動模式：分析面試官與面試者之間的互動模式，是否存在明確的問題與回答、面試官是否鼓勵了詳細回答，或者是否存在困難的問題。

5. 回答改進建議**：根據面試者的回答，給出可能的改進建議。這可以包括如何更好地展示自己的專業技能、如何在回答中增強說服力等。

請依照上述格式進行分析，並提供詳細的報告。
"""

def gradio_handler(csv_file, user_prompt):
    print("進入 gradio_handler")
    
    if not user_prompt:
        user_prompt = default_prompt
    
    if csv_file is not None:
        print("讀取 CSV 檔案")
        df = pd.read_csv(csv_file.name)
        total_rows = df.shape[0]
        block_size = 30
        cumulative_response = ""
        
        for i in range(0, total_rows, block_size):
            block = df.iloc[i:i+block_size]
            block_csv = block.to_csv(index=False)
            prompt = (f"以下是CSV資料第 {i+1} 到 {min(i+block_size, total_rows)} 筆：\n"
                      f"{block_csv}\n\n請根據以下規則進行分析並產出報表：\n{user_prompt}")
            print("完整 prompt for block:")
            print(prompt)
            response = model.generate_content(prompt)
            block_response = response.text.strip()
            cumulative_response += f"區塊 {i//block_size+1}:\n{block_response}\n\n"

        pdf_path = generate_pdf(text=cumulative_response)
        return cumulative_response, pdf_path
    else:
        context = "未上傳 CSV 檔案。"
        full_prompt = f"{context}\n\n{user_prompt}"
        print("完整 prompt：")
        print(full_prompt)
        response = model.generate_content(full_prompt)
        response_text = response.text.strip()
        print("AI 回應：")
        print(response_text)
        pdf_path = generate_pdf(text=response_text)
        return response_text, pdf_path

def generate_pdf(text: str):
    print("開始生成 PDF")
    pdf = FPDF(format="A4")
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, text)

    # 儲存 PDF 文件
    pdf_output_path = f"pdf_report/analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    os.makedirs("pdf_report", exist_ok=True)
    pdf.output(pdf_output_path)
    
    return pdf_output_path

# Gradio 介面設置
with gr.Blocks() as demo:
    gr.Markdown("# 面試對話分析")
    with gr.Row():
        csv_input = gr.File(label="上傳 CSV 檔案")
        user_input = gr.Textbox(label="請輸入分析指令", lines=10, value=default_prompt)
    output_text = gr.Textbox(label="回應內容", interactive=False)
    output_pdf = gr.File(label="下載 PDF 報表")
    submit_button = gr.Button("生成報表")
    submit_button.click(fn=gradio_handler, inputs=[csv_input, user_input], outputs=[output_text, output_pdf])

demo.launch()
