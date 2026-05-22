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


def _get_question_y_bounds(page, q_num):
    """
    在 fitz page 上找題號 q_num 的 y 範圍。
    返回 (q_start_y, q_end_y, next_q_y)，找不到時用估算值。
    """
    page_h = page.rect.height
    text_blocks = []
    for b in page.get_text('blocks'):
        x0, y0, x1, y1, txt, bno, btype = b
        if btype == 0:
            text_blocks.append((y0, y1, txt))

    q_start_y = q_end_y = next_q_y = None
    for y0, y1, txt in text_blocks:
        t = re.sub(r'\s+', ' ', txt).strip()
        if q_end_y is None:
            if re.search(r'(?<!\d)' + str(q_num) + r'\s*[\.\．]', t):
                q_start_y = y0
                q_end_y = y1
        else:
            m = re.match(r'^(\d+)\s*[\.\．]', t)
            if m and int(m.group(1)) > q_num:
                next_q_y = y0
                break

    if q_start_y is None:
        q_start_y, q_end_y = page_h * 0.25, page_h * 0.40
    if next_q_y is None:
        next_q_y = page_h

    return q_start_y, q_end_y, next_q_y


def extract_question_region(pdf_path, page_idx, q_num, output_path,
                             dpi=200, mode='figure'):
    """
    mode='figure' (has_q_image)：
        找題目和下一題之間的嵌入圖片，只截取那個圖示。
    mode='area'   (has_image)：
        截取從本題開始到下一題前的整段（含題幹 + 選項圖）。
    """
    doc = fitz.open(pdf_path)
    page = doc[page_idx]
    page_h = page.rect.height
    page_w = page.rect.width

    q_start_y, q_end_y, next_q_y = _get_question_y_bounds(page, q_num)

    if mode == 'area':
        # 截從題目開始到下一題前（含選項圖）
        pad = 6
        clip = fitz.Rect(
            page_w * 0.01,
            max(0,      q_start_y - pad),
            page_w * 0.99,
            min(page_h, next_q_y  - pad),
        )
        print(f'  → [area] y={q_start_y:.0f}~{next_q_y:.0f}')

    else:  # mode == 'figure'
        # 找題目和下一題之間的嵌入圖片
        figure_rects = []
        for img_info in page.get_images(full=True):
            xref = img_info[0]
            for rect in page.get_image_rects(xref):
                cy = (rect.y0 + rect.y1) / 2
                if cy >= q_end_y - 5 and cy <= next_q_y + 5:
                    if rect.width * rect.height > 500:
                        figure_rects.append(rect)

        if figure_rects:
            x0 = min(r.x0 for r in figure_rects)
            y0 = min(r.y0 for r in figure_rects)
            x1 = max(r.x1 for r in figure_rects)
            y1 = max(r.y1 for r in figure_rects)
            pad = 18
            clip = fitz.Rect(
                max(0,      x0 - pad),
                max(0,      y0 - pad),
                min(page_w, x1 + pad),
                min(page_h, y1 + pad),
            )
            print(f'  → [figure] 找到 {len(figure_rects)} 個圖片，裁切 y={y0:.0f}~{y1:.0f}')
        else:
            # fallback：只截題幹到下一題之間的空白區
            clip = fitz.Rect(
                page_w * 0.03,
                max(0,      q_end_y - 10),
                page_w * 0.97,
                min(page_h, next_q_y + 10),
            )
            print(f'  → [figure fallback] y={q_end_y:.0f}~{next_q_y:.0f}')

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
print(f'共 {len(has_image_qs)} 道圖示題')

os.makedirs('images', exist_ok=True)

ok, skip, fail = 0, 0, 0
for q in has_image_qs:
    prefix  = q['id'].split('_')[0]
    q_num   = q['num']
    pdf_path    = PDF_MAP.get(prefix)
    output_path = f'images/{q["id"]}.jpg'

    if not pdf_path or not os.path.exists(pdf_path):
        print(f'[跳過] {q["id"]} - PDF 不存在: {pdf_path}')
        skip += 1
        continue

    page_idx = find_question_page(pdf_path, q_num)
    if page_idx is None:
        print(f'[找不到頁] {q["id"]} Q{q_num} in {pdf_path}')
        fail += 1
        continue

    if q.get('has_q_image'):
        mode, dpi = 'figure', 250
    else:
        mode, dpi = 'area', 150

    print(f'[{mode}] {q["id"]} Q{q_num} p.{page_idx}')
    size = extract_question_region(pdf_path, page_idx, q_num, output_path, dpi=dpi, mode=mode)
    print(f'[完成] {q["id"]} → {output_path} ({size//1024}KB)')
    ok += 1

print(f'\n完成 {ok} 張，跳過 {skip} 張，失敗 {fail} 張')
