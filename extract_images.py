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
            if re.search(r'(?<!\d)' + str(q_num) + r'\s*[\.\．]\s*[\(（]\d', text_flat):
                return i
    return None

def extract_page_image(pdf_path, page_idx, output_path, dpi=150):
    """用 PyMuPDF 把指定頁面存成 JPEG（整頁，用於 has_image 選項含圖題）"""
    doc = fitz.open(pdf_path)
    page = doc[page_idx]
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    img_bytes = pix.tobytes('jpeg', jpg_quality=75)
    with open(output_path, 'wb') as f:
        f.write(img_bytes)
    doc.close()
    return os.path.getsize(output_path)

def extract_question_figure(pdf_path, page_idx, q_num, output_path, dpi=200):
    """
    用於 has_q_image（題目包含「如下圖」）：
    只擷取題目圖示部分，不含整頁文字。
    策略：找到題號的 y 範圍，再找下一題的 y，
    取兩者之間的圖片物件，裁切後輸出。
    """
    doc = fitz.open(pdf_path)
    page = doc[page_idx]
    page_h = page.rect.height
    page_w = page.rect.width

    # ── 1. 從 text blocks 找本題和下一題的 y 座標 ──
    blocks = page.get_text('blocks')
    text_blocks = [(x0, y0, x1, y1, txt) for x0, y0, x1, y1, txt, *_ in blocks
                   if len(blocks[0]) >= 7 and _[1] == 0]  # type==0 是文字

    # 重新用 tuple 解包（blocks 每個元素 7 項）
    text_blocks = []
    for b in blocks:
        x0, y0, x1, y1, txt, bno, btype = b
        if btype == 0:
            text_blocks.append((y0, y1, txt))

    q_end_y = None     # 本題文字區塊結束 y
    next_q_y = None    # 下一題開始 y

    for (y0, y1, txt) in text_blocks:
        t = re.sub(r'\s+', ' ', txt).strip()
        if q_end_y is None:
            # 找到本題號
            if re.search(r'(?<!\d)' + str(q_num) + r'\s*[\.\．]', t):
                q_end_y = y1
        else:
            # 找下一題（題號 q_num+1 或更大）
            m = re.match(r'^(\d+)\s*[\.\．]', t)
            if m and int(m.group(1)) > q_num:
                next_q_y = y0
                break

    # 沒找到本題位置 → 用頁面中段 fallback
    if q_end_y is None:
        q_end_y = page_h * 0.30
    if next_q_y is None:
        next_q_y = page_h * 0.75

    # ── 2. 找位於本題圖示區域的圖片物件 ──
    figure_rects = []
    for img_info in page.get_images(full=True):
        xref = img_info[0]
        for rect in page.get_image_rects(xref):
            # 圖片的 y 中心在本題和下一題之間
            cy = (rect.y0 + rect.y1) / 2
            if cy >= q_end_y - 5 and cy <= next_q_y + 5:
                area = rect.width * rect.height
                if area > 500:   # 過濾掉太小的裝飾圖示
                    figure_rects.append(rect)

    if figure_rects:
        # 合併所有圖示的 bounding box
        x0 = min(r.x0 for r in figure_rects)
        y0 = min(r.y0 for r in figure_rects)
        x1 = max(r.x1 for r in figure_rects)
        y1 = max(r.y1 for r in figure_rects)
        pad = 18
        clip = fitz.Rect(
            max(0,       x0 - pad),
            max(0,       y0 - pad),
            min(page_w,  x1 + pad),
            min(page_h,  y1 + pad),
        )
        print(f'  → 找到 {len(figure_rects)} 個圖片物件，裁切 y={y0:.0f}~{y1:.0f}')
    else:
        # fallback：顯示本題文字區到下一題之間的整段
        pad = 10
        clip = fitz.Rect(
            page_w * 0.03,
            max(0, q_end_y - pad),
            page_w * 0.97,
            min(page_h, next_q_y + pad),
        )
        print(f'  → 未找到圖片物件，裁切文字區 y={q_end_y:.0f}~{next_q_y:.0f}')

    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, clip=clip, colorspace=fitz.csRGB)
    img_bytes = pix.tobytes('jpeg', jpg_quality=85)
    with open(output_path, 'wb') as f:
        f.write(img_bytes)
    doc.close()
    return os.path.getsize(output_path)

# ── 主程式 ──
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

    if os.path.exists(output_path) and not q.get('has_q_image'):
        print(f'[已有] {q["id"]}')
        skip += 1
        continue

    page_idx = find_question_page(pdf_path, q_num)
    if page_idx is None:
        print(f'[找不到頁] {q["id"]} Q{q_num} in {pdf_path}')
        fail += 1
        continue

    if q.get('has_q_image'):
        print(f'[圖示題] {q["id"]} Q{q_num} p.{page_idx}')
        size = extract_question_figure(pdf_path, page_idx, q_num, output_path, dpi=250)
    else:
        size = extract_page_image(pdf_path, page_idx, output_path)

    print(f'[完成] {q["id"]} → {output_path} ({size//1024}KB)')
    ok += 1

print(f'\n完成 {ok} 張，跳過 {skip} 張，失敗 {fail} 張')
