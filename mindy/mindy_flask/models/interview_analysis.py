import os
from datetime import datetime
import gradio as gr
import pandas as pd
from dotenv import load_dotenv
from fpdf import FPDF
from datetime import datetime
import google.generativeai as genai
import re
import warnings
warnings.filterwarnings("ignore", message="cmap value too big/small:*")

# 載入環境變數並設定 API 金鑰
dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

def get_chinese_font_file() -> str:
    fonts_path = r"C:\\Windows\\Fonts"
    candidates = ["kaiu.ttf"]
    for font in candidates:
        font_path = os.path.join(fonts_path, font)
        if os.path.exists(font_path):
            print("找到系統中文字型：", font_path)
            return os.path.abspath(font_path)
    print("未在系統中找到候選中文字型檔案。")
    return None

def create_table(pdf: FPDF, df: pd.DataFrame):
    available_width = pdf.w - 2 * pdf.l_margin
    cell_height = 8
    font_size = 9  # 調整字體大小，避免過大文字
    pdf.set_font("ChineseFont", size=font_size)

    # 設置每列的寬度，並確保字體大小與排版兼容
    col_widths = []
    for col in df.columns:
        if "留言" in col or "關鍵詞" in col:
            col_widths.append(available_width * 0.45)  # 留言或關鍵詞欄位較寬
        else:
            col_widths.append(available_width * 0.55 / (len(df.columns) - 1))  # 其他欄位平均分配

    scale = available_width / sum(col_widths)
    col_widths = [w * scale for w in col_widths]

    # 表頭：使用背景色
    pdf.set_fill_color(200, 200, 200)
    for i, col in enumerate(df.columns):
        pdf.cell(col_widths[i], cell_height, str(col), border=1, align="C", fill=True)
    pdf.ln(cell_height)

    fill = False
    for index, row in df.iterrows():
        if pdf.get_y() + cell_height > pdf.h - pdf.b_margin:
            pdf.add_page()
            pdf.set_fill_color(200, 200, 200)
            for i, col in enumerate(df.columns):
                pdf.cell(col_widths[i], cell_height, str(col), border=1, align="C", fill=True)
            pdf.ln(cell_height)

        pdf.set_fill_color(245, 245, 255) if fill else pdf.set_fill_color(255, 255, 255)
        fill = not fill

        # 逐行處理，每行的文字會自動換行
        for i, item in enumerate(row):
            text = str(item).replace("**", "")  # 去掉不必要的格式
            pdf.multi_cell(col_widths[i], cell_height, text, border=1, align="L", fill=True)
        
        pdf.ln(cell_height)

def parse_markdown_table(markdown_text: str) -> pd.DataFrame:
    lines = markdown_text.strip().splitlines()
    lines = [line.strip() for line in lines if line.strip()]
    table_lines = [line for line in lines if line.startswith("|")]
    if not table_lines:
        return None
    header_line = table_lines[0]
    headers = [h.strip() for h in header_line.strip("|").split("|")]
    data = []
    for line in table_lines[2:]:
        row = [cell.strip() for cell in line.strip("|").split("|")]
        if len(row) == len(headers):
            data.append(row)
    df = pd.DataFrame(data, columns=headers)
    return df

def generate_pdf(text: str = None, df: pd.DataFrame = None) -> str:
    print("開始生成 PDF")
    pdf = FPDF(format="A4")
    pdf.add_page()

    chinese_font_path = get_chinese_font_file()
    if not chinese_font_path:
        return "錯誤：無法取得中文字型檔"

    pdf.add_font("ChineseFont", "", chinese_font_path, uni=True)
    pdf.set_font("ChineseFont", "", 12)

    if df is not None:
        create_table(pdf, df)
    elif text is not None:
        if "|" in text:
            table_part = "\n".join([line for line in text.splitlines() if line.strip().startswith("|")])
            parsed_df = parse_markdown_table(table_part)
            if parsed_df is not None:
                create_table(pdf, parsed_df)
            else:
                pdf.multi_cell(0, 10, text)
        else:
            pdf.multi_cell(0, 10, text)
    else:
        pdf.cell(0, 10, "沒有可呈現的內容")

    output_dir = "pdf_report"
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    pdf.output(filename)
    print("PDF 已儲存：", filename)
    return filename

def gradio_handler(csv_file, user_prompt):
    print("進入 gradio_handler")
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
