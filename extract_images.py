import sys, io, json, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import fitz  # PyMuPDF
import pdfplumber

PDF_MAP = {
    'D': '12500_design.pdf',
    'S': '12500_safety.pdf',
    'E': '90007_ethics.pdf',
    'V': '90008_env.pdf',
    'N': '90009_energy.pdf',
}

def find_question_page(pdf_path, q_num):
    """找出題號 q_num 在 PDF 的頁碼（0-indexed）"""
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ''
            text_flat = re.sub(r'\s+', ' ', text)
            # 找 "3. (1)" 或 "3.（1）" 這類模式
            if re.search(r'(?<!\d)' + str(q_num) + r'\s*[\.\．]\s*[\(（]\d', text_flat):
                return i
    return None

def extract_page_image(pdf_path, page_idx, output_path, dpi=150):
    """用 PyMuPDF 把指定頁面存成 JPEG"""
    doc = fitz.open(pdf_path)
    page = doc[page_idx]
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    # 轉成 JPEG bytes 再存（壓縮、縮小檔案）
    pix.save(output_path.replace('.jpg', '_tmp.png'))
    # 用 fitz 直接存 JPEG
    img_bytes = pix.tobytes('jpeg', jpg_quality=75)
    with open(output_path, 'wb') as f:
        f.write(img_bytes)
    # 清理暫存
    tmp = output_path.replace('.jpg', '_tmp.png')
    if os.path.exists(tmp):
        os.remove(tmp)
    doc.close()
    return os.path.getsize(output_path)

# 讀取題目
with open('questions.json', encoding='utf-8') as f:
    questions = json.load(f)

has_image_qs = [q for q in questions if q.get('has_image') or q.get('has_q_image')]
print(f'共 {len(has_image_qs)} 道圖示題（含題目含圖）')

os.makedirs('images', exist_ok=True)

ok, skip, fail = 0, 0, 0
for q in has_image_qs:
    prefix = q['id'].split('_')[0]
    q_num = q['num']
    pdf_path = PDF_MAP.get(prefix)
    output_path = f'images/{q["id"]}.jpg'

    if not pdf_path or not os.path.exists(pdf_path):
        print(f'[跳過] {q["id"]} - PDF 不存在: {pdf_path}')
        skip += 1
        continue

    if os.path.exists(output_path):
        print(f'[已有] {q["id"]}')
        skip += 1
        continue

    page_idx = find_question_page(pdf_path, q_num)
    if page_idx is None:
        print(f'[找不到頁] {q["id"]} Q{q_num} in {pdf_path}')
        fail += 1
        continue

    size = extract_page_image(pdf_path, page_idx, output_path)
    print(f'[完成] {q["id"]} → images/{q["id"]}.jpg ({size//1024}KB)')
    ok += 1

print(f'\n完成 {ok} 張，跳過 {skip} 張，失敗 {fail} 張')
