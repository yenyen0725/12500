# 12500 建築物室內設計 學科練習網站

## 專案概覽

靜態網頁題庫測驗，部署於 GitHub Pages：https://yenyen0725.github.io/12500/

- `questions.json` → 題目來源（1149 題）
- `build_quiz.py` → 產生 `quiz.html`（完整單頁應用）
- `extract_images.py` → 從 PDF 擷取圖示題圖片到 `images/`
- `quiz.html` → 最終部署的測驗頁面

## 常用指令

```bash
# 重建網頁
python build_quiz.py

# 重新擷取所有圖示題圖片
python extract_images.py

# 推送到 GitHub Pages
git add -A && git commit -m "..." && git push
```

## PDF 對照表（`extract_images.py`）

```python
PDF_MAP = {
    'D': '12500_design.pdf',
    'S': '12500_safety.pdf',
    'E': '90007_ethics.pdf',
    'V': '90008_env.pdf',
    'N': '90009_energy.pdf',
}
```

## questions.json 結構

```json
{
  "id": "D_42",          // 科目前綴_題號（注意：同號題可能跨章節重複）
  "num": 42,             // PDF 中的題號
  "subject": "12500 建築物室內設計",
  "section": "繪製圖說",
  "question": "題目文字",
  "options": ["選項A","選項B","選項C","選項D"],  // has_image 題可為空字串
  "answer": [1],         // 1-indexed，多選如 [1,3,4]
  "is_multiple": false,
  "has_image": true,     // 選項含圖（圖片即選項，options 可為空）
  "has_q_image": true    // 題幹含圖（題目中有「如下圖」）
}
```

## 圖示題規則

### 兩種類型

| 欄位 | 意義 | 擷取方式 | DPI |
|------|------|----------|-----|
| `has_q_image` | 題幹含圖（「如下圖所示」） | `mode='figure'`：只截 PDF 內嵌圖片 | 250 |
| `has_image` | 選項含圖（圖即選項） | `mode='area'`：截整題範圍並塗白答案 | 150 |

### 答案遮蔽規則（`_redact_answer`）

PDF 格式：`42. (1) 題目文字...`，答案 `(N)` 印在題號後。

- **多選答案**：PDF 合併顯示，如 answer=[1,4] → PDF 印 `(14)`，需搜尋合併字串
- **搜尋順序**：先嘗試合併格式 `(14)`，找不到才逐一嘗試 `(1)` `(4)`

```python
combined = ''.join(str(a) for a in sorted(q_answer))
# 先搜尋 (14)，再搜尋 (1)(4)
```

### 跨章節同號題衝突

同一 PDF 的不同章節可能都有「第 42 題」，`find_question_page()` 會找到錯誤的頁。

**解法**：傳入 `q_answer`，只接受「題號 + 答案都匹配」的頁：

```python
page_idx = find_question_page(pdf_path, q_num, q_answer=q.get('answer'))
if page_idx is None:
    page_idx = find_question_page(pdf_path, q_num)  # fallback
```

## build_quiz.py 功能要點

### 圖示題顯示
- `has_image` 或 `has_q_image` → 顯示 `images/{id}.jpg`
- `has_q_image`：圖片寬度 `auto`（只顯示圖）
- `has_image`：圖片寬度 `100%`（全寬顯示選項圖）
- `has_image` 題**不**自動揭示答案，讓使用者自行選擇

### 選項顯示
```js
const txt = opt || (circles[i] + ' （見上圖）');  // 空選項顯示圓圈符號
```

### 作答流程
- `confirmAnswer()`：確認答案、更新錯題庫、觸發雲端同步
- `skipQuestion()`：跳過、加入錯題庫、觸發雲端同步
- `prevQuestion()`：返回上一題（review mode 顯示已作答結果）
- 手機左右滑動：左滑=下一題，右滑=上一題

### AI 解析
- 使用 Groq API（llama-3.1-8b-instant），台灣可用、免費
- 答對答錯都能查詢
- `askAI()` 每次都先清除快取，強制重新查詢
- 有快取時顯示「重新查詢」按鈕

### 本機進度同步（匯出/匯入）
- `exportProgress()` / `importProgress()`：JSON 檔案手動備份

## Google Drive 雲端同步

### 架構
```
quiz.html (localStorage) → Apps Script Web App → Google Drive/12500/練習進度/12500progress.json
```

### 同步的資料
- `wrongBank`：錯題 ID 陣列
- `totalStats`：`{total, correct}`
- `questionNotes`：`{qId: "筆記文字"}`

### 關鍵實作

GAS URL **寫死在程式碼**（`DEFAULT_GAS_URL`），任何設備打開都自動連線：

```js
const DEFAULT_GAS_URL = 'https://script.google.com/macros/s/AKfycbzuKGeFZ7EPDNFUb5RhBVs78-RdgUMQLKqPpAtHH-4S8y3ba-UbnMWDH1mkfphyEMDWEw/exec';
let gasUrl = localStorage.getItem('gasUrl') || DEFAULT_GAS_URL;
```

自動觸發：攔截 `localStorage.setItem`，對 `wrongBank`/`totalStats`/`questionNotes` 的變更自動 2 秒後同步：

```js
const SYNC_KEYS = new Set(['wrongBank','totalStats','questionNotes']);
const _orig = localStorage.setItem.bind(localStorage);
localStorage.setItem = function(key, val){
  _orig(key, val);
  if(SYNC_KEYS.has(key)){ clearTimeout(cloudSyncTimer); cloudSyncTimer = setTimeout(syncToCloud, 2000); }
};
```

Apps Script 部署設定：
- 執行身份：**我**（帳號擁有者）
- 存取權限：**所有人**
- 資料夾：`我的雲端硬碟/12500/練習進度/`

## localStorage 資料結構

| Key | 類型 | 說明 |
|-----|------|------|
| `wrongBank` | `string[]` | 錯題 ID 陣列 |
| `totalStats` | `{total,correct}` | 累計作答統計 |
| `questionNotes` | `{[id]:string}` | 各題筆記 |
| `aiExplanations` | `{[id]:string}` | AI 解析快取（不同步至雲端） |
| `groqApiKey` | `string` | Groq API Key |
| `gasUrl` | `string` | 自訂 Apps Script 網址（覆蓋預設） |

## 部署注意事項

- `quiz.html` 必須重新 build 才會更新（`python build_quiz.py`）
- 圖片存在 `images/` 資料夾，已 commit 進 repo
- GitHub Pages 從 `main` branch 根目錄自動部署
- 修改 `build_quiz.py` 後記得執行 build 再 commit `quiz.html`
