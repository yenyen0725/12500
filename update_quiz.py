import sys, io, json, re, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pdfplumber

def extract_text(fname):
    texts = []
    with pdfplumber.open(fname) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t: texts.append(t)
    return '\n'.join(texts)

def parse_questions(raw_text, subject_prefix, subject_name, common_section):
    text = re.sub(r'Page \d+ of \d+', ' ', raw_text)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'  +', ' ', text)

    questions = []
    section_pattern = re.compile(r'工作項目\s*(\d+)[：:]\s*([^\d]+?)(?=\s+\d+\.\s*\(|\s*工作項目|$)')
    sections = list(section_pattern.finditer(text))

    q_pattern = re.compile(r'(\d+)\.\s*\((\d+)\)\s*(.*?)(?=\s+\d+\.\s*\(\d+\)|\s*$)')
    matches = list(q_pattern.finditer(text))

    for match in matches:
        q_num = int(match.group(1))
        answer_raw = match.group(2)
        q_text_raw = match.group(3).strip()

        q_pos = match.start()
        sec_name = common_section
        for s in sections:
            if s.start() <= q_pos:
                sec_name = s.group(2).strip()

        correct = [int(a) for a in list(answer_raw)]

        option_pattern = re.compile(r'[①②③④]')
        parts = option_pattern.split(q_text_raw)
        circles = option_pattern.findall(q_text_raw)

        question_text = parts[0].strip().rstrip('。').strip()
        options = []
        for i, circle in enumerate('①②③④'):
            if circle in circles:
                idx = circles.index(circle)
                if idx < len(parts) - 1:
                    opt = parts[idx + 1].strip().rstrip('。').strip()
                    options.append(opt)
                else:
                    options.append('')
            else:
                options.append('')

        all_empty = all(len(opt.strip()) < 2 for opt in options)

        questions.append({
            'id': f'{subject_prefix}_{q_num}',
            'num': q_num,
            'subject': subject_name,
            'section': sec_name,
            'question': question_text,
            'options': options,
            'answer': correct,
            'is_multiple': len(answer_raw) > 1,
            'has_image': all_empty
        })

    return questions

# Load existing questions
with open('questions.json', encoding='utf-8') as f:
    existing = json.load(f)

# Parse new subject PDFs
new_files = [
    ('90007_ethics.pdf',  'E', '90007 工作倫理與職業道德', '工作倫理與職業道德'),
    ('90008_env.pdf',     'V', '90008 環境保護',           '環境保護'),
    ('90009_energy.pdf',  'N', '90009 節能減碳',           '節能減碳'),
]

new_questions = []
for fname, prefix, subject_name, section in new_files:
    text = extract_text(fname)
    qs = parse_questions(text, prefix, subject_name, section)
    new_questions.extend(qs)
    print(f'{subject_name}: {len(qs)} questions')

all_questions = existing + new_questions
print(f'\nTotal: {len(all_questions)} questions')

# Save updated questions.json
with open('questions.json', 'w', encoding='utf-8') as f:
    json.dump(all_questions, f, ensure_ascii=False, indent=2)
print('Saved questions.json')
