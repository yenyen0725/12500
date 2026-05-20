import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('questions.json', encoding='utf-8') as f:
    questions = json.load(f)

qs_json = json.dumps(questions, ensure_ascii=False)

HTML = r"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>12500 建築物室內設計 乙級學科題庫測驗</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --primary:#2563eb;--primary-dark:#1d4ed8;--primary-light:#dbeafe;
  --success:#16a34a;--success-light:#dcfce7;
  --danger:#dc2626;--danger-light:#fee2e2;
  --warn:#d97706;--warn-light:#fef3c7;
  --neutral:#6b7280;--neutral-light:#f3f4f6;
  --border:#e5e7eb;--bg:#f9fafb;--card:#fff;
  --text:#111827;--text-sub:#6b7280;
  --radius:12px;--shadow:0 2px 8px rgba(0,0,0,.08);
}
body{font-family:-apple-system,BlinkMacSystemFont,"Microsoft JhengHei",sans-serif;
  background:var(--bg);color:var(--text);min-height:100vh;line-height:1.6;font-size:16px}
.screen{display:none;min-height:100vh;flex-direction:column;align-items:center;padding:16px}
.screen.active{display:flex}

/* ===== HOME ===== */
#home{background:linear-gradient(135deg,#1e3a8a 0%,#2563eb 100%)}
.home-inner{width:100%;max-width:560px;padding:8px}
.logo-area{text-align:center;padding:28px 0 20px;color:#fff}
.logo-area h1{font-size:1.45rem;font-weight:700;line-height:1.3;margin-bottom:6px}
.logo-area .subtitle{font-size:.88rem;opacity:.8}
.badge{display:inline-block;background:rgba(255,255,255,.2);color:#fff;
  padding:4px 12px;border-radius:20px;font-size:.8rem;margin-top:8px}
.card{background:var(--card);border-radius:var(--radius);padding:18px;
  box-shadow:var(--shadow);margin-bottom:14px}
.card h3{font-size:.82rem;font-weight:600;color:var(--text-sub);
  text-transform:uppercase;letter-spacing:.05em;margin-bottom:12px}
.filter-group{display:flex;flex-wrap:wrap;gap:8px}
.filter-btn{border:2px solid var(--border);background:#fff;color:var(--text);
  padding:6px 13px;border-radius:8px;cursor:pointer;font-size:.86rem;
  font-family:inherit;transition:all .15s}
.filter-btn:hover{border-color:var(--primary);color:var(--primary)}
.filter-btn.active{border-color:var(--primary);background:var(--primary-light);
  color:var(--primary);font-weight:600}
.section-checkboxes{display:flex;flex-direction:column;gap:7px}
.section-cb{display:flex;align-items:center;gap:10px;cursor:pointer;
  padding:7px 10px;border-radius:8px;border:1px solid var(--border);transition:background .1s}
.section-cb:hover{background:var(--neutral-light)}
.section-cb input[type=checkbox]{width:17px;height:17px;cursor:pointer;accent-color:var(--primary)}
.section-cb .cnt{margin-left:auto;font-size:.78rem;color:var(--text-sub);
  background:var(--neutral-light);padding:2px 8px;border-radius:10px}
.num-btns,.order-group{display:flex;flex-wrap:wrap;gap:8px}
.num-btn,.order-btn{border:2px solid var(--border);background:#fff;color:var(--text);
  padding:7px 15px;border-radius:8px;cursor:pointer;font-size:.88rem;
  font-family:inherit;transition:all .15s}
.num-btn:hover,.order-btn:hover{border-color:var(--primary);color:var(--primary)}
.num-btn.active,.order-btn.active{border-color:var(--primary);background:var(--primary-light);
  color:var(--primary);font-weight:700}
.order-btn{flex:1;text-align:center}
.mode-cards{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.mode-card{border:2px solid var(--border);background:#fff;border-radius:10px;
  padding:14px;cursor:pointer;text-align:center;transition:all .15s}
.mode-card:hover{border-color:var(--primary)}
.mode-card.active{border-color:var(--primary);background:var(--primary-light)}
.mode-card .icon{font-size:1.5rem;margin-bottom:5px}
.mode-card .label{font-size:.88rem;font-weight:600}
.mode-card .desc{font-size:.75rem;color:var(--text-sub);margin-top:2px}
.start-btn{width:100%;padding:15px;background:var(--primary);color:#fff;
  border:none;border-radius:10px;font-size:1.05rem;font-weight:700;
  cursor:pointer;transition:background .15s;margin-top:4px;font-family:inherit}
.start-btn:hover{background:var(--primary-dark)}
.stats-bar{display:flex;gap:10px;margin-bottom:14px}
.stat-item{flex:1;background:rgba(255,255,255,.15);border-radius:8px;
  padding:10px;text-align:center;color:#fff}
.stat-item .val{font-size:1.3rem;font-weight:700}
.stat-item .lbl{font-size:.73rem;opacity:.8}
.reset-link{text-align:center;margin-top:2px;padding-bottom:6px}
.reset-link a{color:rgba(255,255,255,.45);font-size:.76rem;cursor:pointer;text-decoration:underline}

/* ===== QUIZ ===== */
#quiz{background:var(--bg)}
.quiz-topbar{width:100%;max-width:700px;display:flex;align-items:center;
  gap:10px;padding:12px 0 6px}
.progress-bar{flex:1;height:6px;background:var(--border);border-radius:3px;overflow:hidden}
.progress-fill{height:100%;background:var(--primary);border-radius:3px;transition:width .3s}
.progress-text{font-size:.82rem;color:var(--text-sub);white-space:nowrap}
.exit-btn{padding:6px 12px;border:1.5px solid var(--border);background:#fff;
  color:var(--text-sub);border-radius:8px;cursor:pointer;font-size:.8rem;
  font-family:inherit;white-space:nowrap;transition:all .15s;flex-shrink:0}
.exit-btn:hover{border-color:var(--danger);color:var(--danger);background:var(--danger-light)}
.quiz-tags{width:100%;max-width:700px;display:flex;gap:6px;flex-wrap:wrap;margin-bottom:4px}
.tag{padding:3px 10px;border-radius:20px;font-size:.73rem;font-weight:600}
.tag-subject{background:#e0e7ff;color:#3730a3}
.tag-section{background:var(--neutral-light);color:var(--neutral)}
.tag-multi{background:var(--warn-light);color:var(--warn)}
.quiz-card{width:100%;max-width:700px;background:var(--card);
  border-radius:var(--radius);padding:22px;box-shadow:var(--shadow);margin-bottom:12px}
.q-num{font-size:.8rem;color:var(--text-sub);margin-bottom:6px}
.q-text{font-size:1.04rem;line-height:1.75;margin-bottom:18px}
.options-list{display:flex;flex-direction:column;gap:9px}
.option-item{border:2px solid var(--border);border-radius:10px;
  cursor:pointer;transition:all .15s;user-select:none}
.option-item:hover:not(.disabled){border-color:var(--primary);background:var(--primary-light)}
.option-item.selected{border-color:var(--primary);background:var(--primary-light)}
.option-item.correct{border-color:var(--success)!important;background:var(--success-light)!important}
.option-item.wrong{border-color:var(--danger)!important;background:var(--danger-light)!important}
.option-item.show-correct{border-color:var(--success);background:var(--success-light)}
.option-item.disabled{cursor:default}
.option-inner{display:flex;align-items:flex-start;gap:12px;padding:11px 14px}
.opt-label{width:28px;height:28px;border-radius:6px;background:var(--border);
  display:flex;align-items:center;justify-content:center;font-weight:700;
  font-size:.86rem;flex-shrink:0;transition:all .15s}
.option-item.selected .opt-label{background:var(--primary);color:#fff}
.option-item.correct .opt-label{background:var(--success);color:#fff}
.option-item.wrong .opt-label{background:var(--danger);color:#fff}
.option-item.show-correct .opt-label{background:var(--success);color:#fff}
.opt-text{font-size:.94rem;line-height:1.5;padding-top:3px}
.image-notice{background:#fff3cd;border:1px solid #ffc107;border-radius:8px;
  padding:9px 13px;font-size:.83rem;color:#856404;margin-bottom:10px}

/* 解析區塊 */
.analysis-box{border-radius:10px;padding:16px;margin-top:14px;display:none;
  border:1px solid transparent}
.analysis-box.show{display:block}
.analysis-box.correct{background:#f0fdf4;border-color:#86efac}
.analysis-box.wrong{background:#fef2f2;border-color:#fca5a5}
.analysis-box.info{background:#fffbeb;border-color:#fde68a}
.analysis-verdict{display:flex;align-items:center;gap:8px;
  font-size:1rem;font-weight:700;margin-bottom:10px}
.analysis-verdict .icon{font-size:1.2rem}
.analysis-answer{background:rgba(255,255,255,.7);border-radius:8px;
  padding:10px 14px;margin-bottom:0}
.analysis-answer .label{font-size:.75rem;font-weight:600;color:var(--text-sub);
  text-transform:uppercase;letter-spacing:.04em;margin-bottom:6px}
.analysis-answer .ans-rows{display:flex;flex-direction:column;gap:5px}
.ans-row{display:flex;align-items:flex-start;gap:8px;font-size:.9rem}
.ans-circle{width:22px;height:22px;border-radius:5px;background:var(--success);
  color:#fff;display:flex;align-items:center;justify-content:center;
  font-size:.72rem;font-weight:700;flex-shrink:0;margin-top:1px}
.ans-text{line-height:1.5}
.your-ans{margin-top:8px;padding-top:8px;border-top:1px solid rgba(0,0,0,.06)}
.your-ans .label{font-size:.75rem;font-weight:600;color:var(--text-sub);
  text-transform:uppercase;letter-spacing:.04em;margin-bottom:4px}
.your-ans .ya-text{font-size:.88rem;color:var(--danger)}

.quiz-footer{width:100%;max-width:700px;display:flex;gap:10px;padding-bottom:24px}
.btn{padding:12px 18px;border:none;border-radius:8px;font-size:.93rem;
  font-weight:600;cursor:pointer;font-family:inherit;transition:all .15s;flex:1}
.btn-primary{background:var(--primary);color:#fff}
.btn-primary:hover{background:var(--primary-dark)}
.btn-primary:disabled{background:var(--border);color:var(--text-sub);cursor:not-allowed}
.btn-skip{background:var(--neutral-light);color:var(--text-sub);flex:.6}
.btn-skip:hover{background:var(--border)}

/* ===== RESULTS ===== */
#results{background:var(--bg)}
.results-inner{width:100%;max-width:560px;padding:8px}
.score-hero{background:linear-gradient(135deg,#1e3a8a,#2563eb);
  border-radius:16px;padding:26px;text-align:center;color:#fff;margin-bottom:14px}
.score-circle{width:100px;height:100px;border-radius:50%;
  background:rgba(255,255,255,.15);display:flex;flex-direction:column;
  align-items:center;justify-content:center;margin:0 auto 12px;
  border:3px solid rgba(255,255,255,.4)}
.score-pct{font-size:1.9rem;font-weight:800;line-height:1}
.score-label{font-size:.73rem;opacity:.7}
.score-hero h2{font-size:1.15rem;font-weight:700;margin-bottom:3px}
.score-verdict{font-size:.95rem;opacity:.85}
.score-verdict.pass{color:#bbf7d0}
.score-verdict.fail{color:#fecaca}
.stats-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:14px}
.stat-card{background:var(--card);border-radius:10px;padding:13px;
  text-align:center;box-shadow:var(--shadow)}
.stat-card .val{font-size:1.45rem;font-weight:700}
.stat-card .lbl{font-size:.73rem;color:var(--text-sub);margin-top:2px}
.stat-card.green .val{color:var(--success)}
.stat-card.red .val{color:var(--danger)}
.stat-card.blue .val{color:var(--primary)}
.review-section{background:var(--card);border-radius:var(--radius);
  padding:16px;box-shadow:var(--shadow);margin-bottom:14px}
.review-section h3{font-size:.95rem;font-weight:700;margin-bottom:12px}
.review-item{border-left:3px solid var(--danger);padding:10px 12px;
  margin-bottom:9px;background:var(--danger-light);border-radius:0 8px 8px 0}
.review-item.skipped{border-color:var(--warn);background:var(--warn-light)}
.review-q{font-size:.86rem;line-height:1.5;margin-bottom:5px}
.review-ans{font-size:.8rem;color:var(--text-sub)}
.review-ans span{font-weight:600;color:var(--text)}
.result-btns{display:flex;flex-direction:column;gap:10px;margin-bottom:24px}
.result-btn{width:100%;padding:13px;border:none;border-radius:10px;
  font-size:.98rem;font-weight:700;cursor:pointer;font-family:inherit;transition:all .15s}
.result-btn.primary{background:var(--primary);color:#fff}
.result-btn.primary:hover{background:var(--primary-dark)}
.result-btn.secondary{background:var(--card);color:var(--text);border:2px solid var(--border)}
.result-btn.secondary:hover{border-color:var(--primary);color:var(--primary)}

/* 退出確認 modal */
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.5);
  display:none;align-items:center;justify-content:center;z-index:999;padding:16px}
.modal-overlay.show{display:flex}
.modal-box{background:#fff;border-radius:14px;padding:24px;max-width:340px;
  width:100%;box-shadow:0 8px 32px rgba(0,0,0,.2)}
.modal-box h3{font-size:1.05rem;font-weight:700;margin-bottom:8px}
.modal-box p{font-size:.9rem;color:var(--text-sub);margin-bottom:20px;line-height:1.5}
.modal-btns{display:flex;gap:10px}
.modal-btn{flex:1;padding:11px;border:none;border-radius:8px;
  font-size:.93rem;font-weight:600;cursor:pointer;font-family:inherit}
.modal-btn.cancel{background:var(--neutral-light);color:var(--text)}
.modal-btn.confirm{background:var(--danger);color:#fff}

/* ===== NOTES ===== */
.notes-section{margin-top:14px;border-top:1px solid var(--border);padding-top:12px}
.notes-header{display:flex;align-items:center;gap:6px;margin-bottom:8px}
.notes-header .notes-icon{font-size:.95rem}
.notes-header .notes-lbl{font-size:.8rem;font-weight:700;color:var(--text-sub);letter-spacing:.03em}
.notes-saved{font-size:.73rem;color:var(--success);margin-left:auto;
  opacity:0;transition:opacity .4s}
.notes-saved.show{opacity:1}
.notes-has{font-size:.73rem;color:var(--primary);margin-left:auto;font-weight:600}
.notes-textarea{width:100%;min-height:78px;border:1.5px solid var(--border);border-radius:8px;
  padding:10px 12px;font-size:.875rem;font-family:inherit;color:var(--text);
  resize:vertical;line-height:1.55;transition:border-color .15s;background:#fafafa}
.notes-textarea:focus{outline:none;border-color:var(--primary);background:#fff}
.notes-textarea::placeholder{color:#9ca3af;font-size:.83rem}

/* ===== RESUME BANNER ===== */
.resume-bar{background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.3);
  border-radius:10px;padding:12px 16px;margin-bottom:14px;
  display:flex;align-items:center;justify-content:space-between;gap:10px;color:#fff}
.resume-info{display:flex;align-items:center;gap:10px;font-size:.88rem;min-width:0}
.resume-info .icon{font-size:1.2rem;flex-shrink:0}
.resume-text .title{font-weight:700}
.resume-text .sub{font-size:.76rem;opacity:.75}
.resume-btns{display:flex;gap:8px;flex-shrink:0}
.resume-btn{padding:7px 13px;border-radius:7px;cursor:pointer;font-size:.82rem;
  font-weight:600;font-family:inherit;border:none;transition:all .15s}
.resume-btn.go{background:#fff;color:var(--primary)}
.resume-btn.go:hover{background:var(--primary-light)}
.resume-btn.discard{background:transparent;color:rgba(255,255,255,.7);
  border:1px solid rgba(255,255,255,.35)}
.resume-btn.discard:hover{background:rgba(255,255,255,.15)}
/* ===== SYNC BUTTONS ===== */
.sync-bar{display:flex;gap:8px;margin-bottom:14px}
.sync-btn{flex:1;padding:9px 6px;border-radius:8px;cursor:pointer;font-size:.82rem;
  font-weight:600;font-family:inherit;border:1.5px solid rgba(255,255,255,.3);
  background:rgba(255,255,255,.1);color:#fff;transition:all .15s;text-align:center}
.sync-btn:hover{background:rgba(255,255,255,.2);border-color:rgba(255,255,255,.55)}

@media(max-width:480px){
  .mode-cards{grid-template-columns:1fr}
  .quiz-card{padding:15px}
  .q-text{font-size:.98rem}
}
</style>
</head>
<body>

<!-- EXIT MODAL -->
<div class="modal-overlay" id="exitModal">
  <div class="modal-box">
    <h3>確定要結束測驗？</h3>
    <p>作答進度已自動儲存，下次開啟後可點「繼續作答」繼續。</p>
    <div class="modal-btns">
      <button class="modal-btn cancel" onclick="closeExitModal()">繼續作答</button>
      <button class="modal-btn confirm" onclick="confirmExit()">結束離開</button>
    </div>
  </div>
</div>

<!-- HOME -->
<div id="home" class="screen active">
<div class="home-inner">

  <!-- RESUME BANNER -->
  <div class="resume-bar" id="resumeBar" style="display:none">
    <div class="resume-info">
      <span class="icon">📖</span>
      <div class="resume-text">
        <div class="title">上次測驗尚未完成</div>
        <div class="sub" id="resumeDesc">可從上次進度繼續</div>
      </div>
    </div>
    <div class="resume-btns">
      <button class="resume-btn go" onclick="resumeSession()">繼續作答</button>
      <button class="resume-btn discard" onclick="discardSession()">丟棄</button>
    </div>
  </div>

  <!-- SYNC BUTTONS -->
  <div class="sync-bar">
    <button class="sync-btn" onclick="exportProgress()">📤 匯出進度</button>
    <button class="sync-btn" onclick="importProgress()">📥 匯入進度</button>
  </div>

  <div class="logo-area">
    <h1>🏛 建築物室內設計<br>乙級學科題庫測驗</h1>
    <div class="subtitle">技術士技能檢定 12500（含共同科目 90006–90009）</div>
    <div class="badge">共 1149 道題目</div>
  </div>

  <div class="stats-bar" id="homeStats" style="display:none">
    <div class="stat-item"><div class="val" id="statTotal">0</div><div class="lbl">累計作答</div></div>
    <div class="stat-item"><div class="val" id="statCorrect">0</div><div class="lbl">累計答對</div></div>
    <div class="stat-item"><div class="val" id="statRate">0%</div><div class="lbl">正確率</div></div>
  </div>
  <div class="reset-link" id="resetLink" style="display:none">
    <a onclick="resetStats()">重置學習紀錄</a>
  </div>

  <div class="card">
    <h3>科目選擇</h3>
    <div class="filter-group" id="subjectFilter">
      <button class="filter-btn active" data-val="all">全部科目</button>
      <button class="filter-btn" data-val="design">建築物室內設計</button>
      <button class="filter-btn" data-val="common">共同科目</button>
    </div>
  </div>

  <div class="card">
    <h3>工作項目</h3>
    <div class="section-checkboxes" id="sectionCheckboxes"></div>
  </div>

  <div class="card">
    <h3>題目數量</h3>
    <div class="num-btns">
      <button class="num-btn active" data-val="20">20 題</button>
      <button class="num-btn" data-val="50">50 題</button>
      <button class="num-btn" data-val="100">100 題</button>
      <button class="num-btn" data-val="all">全部</button>
      <button class="num-btn" data-val="wrong">錯題複習</button>
    </div>
  </div>

  <div class="card">
    <h3>測驗模式</h3>
    <div class="mode-cards">
      <div class="mode-card active" data-val="practice">
        <div class="icon">💡</div>
        <div class="label">練習模式</div>
        <div class="desc">作答後立即顯示解析</div>
      </div>
      <div class="mode-card" data-val="exam">
        <div class="icon">📝</div>
        <div class="label">測驗模式</div>
        <div class="desc">全部完成後顯示成績</div>
      </div>
    </div>
  </div>

  <div class="card">
    <h3>出題順序</h3>
    <div class="order-group">
      <button class="order-btn active" data-val="random">🔀 隨機出題</button>
      <button class="order-btn" data-val="seq">📋 依序出題</button>
    </div>
  </div>

  <button class="start-btn" onclick="startQuiz()">▶ 開始測驗</button>
</div>
</div>

<!-- QUIZ -->
<div id="quiz" class="screen">
  <div class="quiz-topbar">
    <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
    <div class="progress-text" id="progressText"></div>
    <button class="exit-btn" onclick="showExitModal()">✕ 結束</button>
  </div>
  <div class="quiz-tags" id="quizTags"></div>

  <div class="quiz-card">
    <div class="q-num" id="qNum"></div>
    <div class="q-text" id="qText"></div>
    <div class="image-notice" id="imageNotice" style="display:none">
      ⚠️ 此題含圖示符號，請對照原始 PDF 作答。正確答案已標示如下。
    </div>
    <div class="options-list" id="optionsList"></div>
    <div class="analysis-box" id="analysisBox">
      <div class="analysis-verdict" id="analysisVerdict"></div>
      <div class="analysis-answer" id="analysisAnswer"></div>
    </div>
    <div class="notes-section">
      <div class="notes-header">
        <span class="notes-icon">📝</span>
        <span class="notes-lbl">我的筆記</span>
        <span class="notes-saved" id="notesSaved">已儲存</span>
        <span class="notes-has" id="notesHas" style="display:none">有筆記</span>
      </div>
      <textarea class="notes-textarea" id="notesArea"
        placeholder="記下重點或備忘，下次做到這題時會自動顯示…"></textarea>
    </div>
  </div>

  <div class="quiz-footer">
    <button class="btn btn-skip" id="skipBtn" onclick="skipQuestion()">跳過</button>
    <button class="btn btn-primary" id="confirmBtn" onclick="confirmAnswer()" disabled>確認答案</button>
    <button class="btn btn-primary" id="nextBtn" onclick="nextQuestion()" style="display:none">下一題 →</button>
  </div>
</div>

<!-- RESULTS -->
<div id="results" class="screen">
<div class="results-inner">
  <div class="score-hero">
    <div class="score-circle">
      <div class="score-pct" id="scorePct">0%</div>
      <div class="score-label">得分</div>
    </div>
    <h2 id="scoreTitle"></h2>
    <div class="score-verdict" id="scoreVerdict"></div>
  </div>
  <div class="stats-grid">
    <div class="stat-card green"><div class="val" id="rCorrect">0</div><div class="lbl">✅ 答對</div></div>
    <div class="stat-card red"><div class="val" id="rWrong">0</div><div class="lbl">❌ 答錯</div></div>
    <div class="stat-card blue"><div class="val" id="rSkipped">0</div><div class="lbl">⏭ 跳過</div></div>
  </div>
  <div class="review-section" id="reviewSection" style="display:none">
    <h3>❌ 答錯 / 跳過的題目</h3>
    <div id="reviewList"></div>
  </div>
  <div class="result-btns">
    <button class="result-btn primary" id="retryWrongBtn" onclick="retryWrong()" style="display:none">🔁 重做錯題</button>
    <button class="result-btn secondary" onclick="goHome()">⚙ 重新設定</button>
  </div>
</div>
</div>

<script>
const ALL_QUESTIONS = __QUESTIONS_JSON__;

const SUBJECT_GROUPS = {
  design: {label:'建築物室內設計', prefix:'12500'},
  common: {label:'共同科目', prefixes:['90006','90007','90008','90009']}
};

const SECTION_COUNTS = {};
ALL_QUESTIONS.forEach(q => { SECTION_COUNTS[q.section] = (SECTION_COUNTS[q.section]||0)+1; });

// All unique sections in order
const ALL_SECTIONS_ORDERED = [
  '圖說判讀','相關法規','繪製圖說','工程估算','工程實務',
  '職業安全衛生','工作倫理與職業道德','環境保護','節能減碳'
];

let quizQuestions=[], currentIdx=0, results=[], answered=false, selectedAnswers=[];
let mode='practice', selSubject='all', selSections=new Set();
let selCount=20, selOrder='random', selMode='practice';
let wrongBank = JSON.parse(localStorage.getItem('wrongBank')||'[]');
let totalStats = JSON.parse(localStorage.getItem('totalStats')||'{"total":0,"correct":0}');
let questionNotes = JSON.parse(localStorage.getItem('questionNotes')||'{}');

function loadNoteForQuestion(qId){
  const ta=document.getElementById('notesArea');
  const note=questionNotes[qId]||'';
  ta.value=note;
  document.getElementById('notesHas').style.display=note?'':'none';
  document.getElementById('notesSaved').classList.remove('show');
}

function saveNoteForQuestion(qId){
  const ta=document.getElementById('notesArea');
  const val=ta.value;
  if(val.trim()){ questionNotes[qId]=val; }
  else { delete questionNotes[qId]; }
  localStorage.setItem('questionNotes',JSON.stringify(questionNotes));
  const saved=document.getElementById('notesSaved');
  const has=document.getElementById('notesHas');
  has.style.display=val.trim()?'':'none';
  saved.classList.add('show');
  clearTimeout(window._notesFadeTimer);
  window._notesFadeTimer=setTimeout(()=>saved.classList.remove('show'),1600);
}

function initHome(){
  updateSectionList();
  updateStats();
  checkSavedSession();

  // Notes textarea — debounced auto-save
  document.getElementById('notesArea').addEventListener('input',()=>{
    clearTimeout(window._notesDebounce);
    window._notesDebounce=setTimeout(()=>{
      const q=quizQuestions[currentIdx];
      if(q) saveNoteForQuestion(q.id);
    }, 600);
  });

  document.getElementById('subjectFilter').addEventListener('click',e=>{
    const btn=e.target.closest('.filter-btn');
    if(!btn)return;
    selSubject=btn.dataset.val;
    document.querySelectorAll('#subjectFilter .filter-btn').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    selSections.clear();
    updateSectionList();
  });

  document.querySelectorAll('.num-btn').forEach(btn=>{
    btn.addEventListener('click',()=>{
      document.querySelectorAll('.num-btn').forEach(b=>b.classList.remove('active'));
      btn.classList.add('active');
      const v=btn.dataset.val;
      selCount = v==='all'?9999 : v==='wrong'?'wrong' : parseInt(v);
    });
  });

  document.querySelectorAll('.mode-card').forEach(card=>{
    card.addEventListener('click',()=>{
      document.querySelectorAll('.mode-card').forEach(c=>c.classList.remove('active'));
      card.classList.add('active');
      selMode=card.dataset.val;
    });
  });

  document.querySelectorAll('.order-btn').forEach(btn=>{
    btn.addEventListener('click',()=>{
      document.querySelectorAll('.order-btn').forEach(b=>b.classList.remove('active'));
      btn.classList.add('active');
      selOrder=btn.dataset.val;
    });
  });
}

function getSections(){
  if(selSubject==='design') return ALL_SECTIONS_ORDERED.slice(0,5);
  if(selSubject==='common') return ALL_SECTIONS_ORDERED.slice(5);
  return ALL_SECTIONS_ORDERED;
}

function updateSectionList(){
  const container=document.getElementById('sectionCheckboxes');
  container.innerHTML='';
  const sections=getSections();
  if(selSections.size===0) sections.forEach(s=>selSections.add(s));

  sections.forEach(sec=>{
    const checked=selSections.has(sec);
    const cnt=SECTION_COUNTS[sec]||0;
    const lbl=document.createElement('label');
    lbl.className='section-cb';
    lbl.innerHTML=`<input type="checkbox" ${checked?'checked':''} data-sec="${sec}">
      <span>${sec}</span><span class="cnt">${cnt} 題</span>`;
    lbl.querySelector('input').addEventListener('change',e=>{
      if(e.target.checked) selSections.add(sec); else selSections.delete(sec);
    });
    container.appendChild(lbl);
  });
}

function updateStats(){
  if(totalStats.total>0){
    document.getElementById('homeStats').style.display='flex';
    document.getElementById('resetLink').style.display='';
    document.getElementById('statTotal').textContent=totalStats.total;
    document.getElementById('statCorrect').textContent=totalStats.correct;
    document.getElementById('statRate').textContent=Math.round(totalStats.correct/totalStats.total*100)+'%';
  }
}

function resetStats(){
  if(!confirm('確定要重置所有學習紀錄（含錯題庫與未完成測驗）嗎？'))return;
  totalStats={total:0,correct:0}; wrongBank=[];
  localStorage.setItem('totalStats',JSON.stringify(totalStats));
  localStorage.setItem('wrongBank',JSON.stringify(wrongBank));
  clearSession();
  document.getElementById('homeStats').style.display='none';
  document.getElementById('resetLink').style.display='none';
  checkSavedSession();
}

function startQuiz(){
  let pool=ALL_QUESTIONS;
  if(selSubject==='design') pool=pool.filter(q=>q.subject.startsWith('12500'));
  else if(selSubject==='common') pool=pool.filter(q=>!q.subject.startsWith('12500'));
  if(selSections.size>0) pool=pool.filter(q=>selSections.has(q.section));

  if(selCount==='wrong'){
    const ids=new Set(wrongBank);
    pool=pool.filter(q=>ids.has(q.id));
    if(!pool.length){alert('錯題庫是空的！先完成一次測驗再來複習。');return;}
  }

  if(selOrder==='random') pool=[...pool].sort(()=>Math.random()-.5);
  if(selCount!=='wrong'&&selCount!==9999) pool=pool.slice(0,selCount);
  if(!pool.length){alert('沒有符合條件的題目，請調整設定。');return;}

  quizQuestions=pool; currentIdx=0; results=[]; mode=selMode; clearSession();
  showScreen('quiz');
  renderQuestion();
}

function renderQuestion(){
  const q=quizQuestions[currentIdx];
  const total=quizQuestions.length;
  document.getElementById('progressFill').style.width=(currentIdx/total*100)+'%';
  document.getElementById('progressText').textContent=(currentIdx+1)+' / '+total;
  document.getElementById('qNum').textContent='第 '+(currentIdx+1)+' 題（共 '+total+' 題）';
  document.getElementById('qText').textContent=q.question;

  const subjectShort = q.subject.startsWith('12500')?'建築物室內設計'
    : q.subject.startsWith('90007')?'工作倫理與職業道德'
    : q.subject.startsWith('90008')?'環境保護'
    : q.subject.startsWith('90009')?'節能減碳'
    : '職業安全衛生';
  let tags=`<span class="tag tag-subject">${subjectShort}</span>
    <span class="tag tag-section">${q.section}</span>`;
  if(q.is_multiple) tags+=`<span class="tag tag-multi">複選題 請選所有正確答案</span>`;
  document.getElementById('quizTags').innerHTML=tags;
  document.getElementById('imageNotice').style.display=q.has_image?'':'none';

  const optList=document.getElementById('optionsList');
  optList.innerHTML='';
  const alphas=['A','B','C','D'];
  const circles=['①','②','③','④'];
  q.options.forEach((opt,i)=>{
    const item=document.createElement('div');
    item.className='option-item'+(q.has_image?' disabled':'');
    item.dataset.idx=i;
    const txt=q.has_image?circles[i]+' 選項（含圖示）':(opt||'（空白）');
    item.innerHTML=`<div class="option-inner">
      <div class="opt-label">${alphas[i]}</div>
      <div class="opt-text">${txt}</div></div>`;
    if(!q.has_image) item.addEventListener('click',()=>toggleOption(i,q));
    optList.appendChild(item);
  });

  selectedAnswers=[]; answered=false;
  document.getElementById('analysisBox').className='analysis-box';
  document.getElementById('confirmBtn').disabled=true;
  loadNoteForQuestion(q.id);
  document.getElementById('confirmBtn').style.display='';
  document.getElementById('nextBtn').style.display='none';
  document.getElementById('skipBtn').style.display='';

  if(q.has_image){
    answered=true;
    document.getElementById('confirmBtn').style.display='none';
    document.getElementById('skipBtn').style.display='none';
    document.getElementById('nextBtn').style.display='';
    q.options.forEach((_,i)=>{ if(q.answer.includes(i+1)) optList.children[i].classList.add('show-correct'); });
    showAnalysis(q, null, 'image');
    results.push({q,selected:[],correct:true,skipped:false,image:true});
  }
}

function toggleOption(idx,q){
  if(answered)return;
  if(q.is_multiple){
    const p=selectedAnswers.indexOf(idx+1);
    if(p===-1) selectedAnswers.push(idx+1); else selectedAnswers.splice(p,1);
  } else {
    selectedAnswers=[idx+1];
  }
  document.querySelectorAll('.option-item').forEach((item,i)=>{
    item.classList.toggle('selected',selectedAnswers.includes(i+1));
  });
  document.getElementById('confirmBtn').disabled=selectedAnswers.length===0;
}

function confirmAnswer(){
  const q=quizQuestions[currentIdx];
  const correct=q.answer.slice().sort().join(',')===
    [...selectedAnswers].sort((a,b)=>a-b).join(',');
  answered=true;

  results.push({q,selected:[...selectedAnswers],correct,skipped:false});
  if(!correct){ if(!wrongBank.includes(q.id)) wrongBank.push(q.id); }
  else { const p=wrongBank.indexOf(q.id); if(p!==-1) wrongBank.splice(p,1); }
  localStorage.setItem('wrongBank',JSON.stringify(wrongBank));
  totalStats.total++; if(correct) totalStats.correct++;
  localStorage.setItem('totalStats',JSON.stringify(totalStats));

  revealOptions(q,correct);
  if(mode==='practice') showAnalysis(q,correct,'answer');

  document.getElementById('confirmBtn').style.display='none';
  document.getElementById('skipBtn').style.display='none';
  document.getElementById('nextBtn').style.display='';
}

function showAnalysis(q, correct, type){
  const circles=['①','②','③','④'];
  const alphas=['A','B','C','D'];
  const box=document.getElementById('analysisBox');
  const verdict=document.getElementById('analysisVerdict');
  const ansDiv=document.getElementById('analysisAnswer');

  if(type==='image'){
    box.className='analysis-box show info';
    verdict.innerHTML=`<span class="icon">📌</span><span>圖示題目</span>`;
  } else if(correct){
    box.className='analysis-box show correct';
    verdict.innerHTML=`<span class="icon">✅</span><span>答對了！</span>`;
  } else {
    box.className='analysis-box show wrong';
    verdict.innerHTML=`<span class="icon">❌</span><span>答錯了</span>`;
  }

  // Build correct answer rows
  let rows='';
  q.answer.forEach(a=>{
    const optTxt=q.has_image?'（圖示選項）':(q.options[a-1]||'');
    rows+=`<div class="ans-row">
      <div class="ans-circle">${alphas[a-1]}</div>
      <div class="ans-text">${circles[a-1]} ${optTxt}</div></div>`;
  });

  let yourAns='';
  if(type==='answer' && !correct && selectedAnswers.length>0){
    const yTxt=selectedAnswers.map(a=>circles[a-1]+(q.options[a-1]?(' '+q.options[a-1]):'')).join('、');
    yourAns=`<div class="your-ans">
      <div class="label">你的答案</div>
      <div class="ya-text">${yTxt}</div></div>`;
  }

  ansDiv.innerHTML=`
    <div class="label">正確答案</div>
    <div class="ans-rows">${rows}</div>
    ${yourAns}`;
}

function revealOptions(q, correct){
  document.querySelectorAll('.option-item').forEach((item,i)=>{
    item.classList.add('disabled');
    const isCorrect=q.answer.includes(i+1);
    const isSelected=selectedAnswers.includes(i+1);
    if(isCorrect&&isSelected) item.classList.add('correct');
    else if(isCorrect) item.classList.add('show-correct');
    else if(isSelected) item.classList.add('wrong');
  });
}

function skipQuestion(){
  const q=quizQuestions[currentIdx];
  answered=true;
  results.push({q,selected:[],correct:false,skipped:true});
  totalStats.total++;
  localStorage.setItem('totalStats',JSON.stringify(totalStats));
  if(!wrongBank.includes(q.id)) wrongBank.push(q.id);
  localStorage.setItem('wrongBank',JSON.stringify(wrongBank));

  document.getElementById('confirmBtn').style.display='none';
  document.getElementById('skipBtn').style.display='none';
  document.getElementById('nextBtn').style.display='';

  // Always show analysis on skip
  const q2=q;
  const circles=['①','②','③','④'];
  const alphas=['A','B','C','D'];
  const box=document.getElementById('analysisBox');
  box.className='analysis-box show wrong';
  document.getElementById('analysisVerdict').innerHTML=`<span class="icon">⏭</span><span>已跳過</span>`;
  let rows='';
  q2.answer.forEach(a=>{
    const optTxt=q2.has_image?'（圖示選項）':(q2.options[a-1]||'');
    rows+=`<div class="ans-row">
      <div class="ans-circle">${alphas[a-1]}</div>
      <div class="ans-text">${circles[a-1]} ${optTxt}</div></div>`;
  });
  document.getElementById('analysisAnswer').innerHTML=`
    <div class="label">正確答案</div>
    <div class="ans-rows">${rows}</div>`;

  revealOptions(q2, false);
}

function nextQuestion(){
  currentIdx++;
  if(currentIdx>=quizQuestions.length){ clearSession(); showResults(); }
  else { saveSession(); renderQuestion(); }
}

function showResults(){
  const correct=results.filter(r=>r.correct&&!r.skipped&&!r.image).length;
  const wrong=results.filter(r=>!r.correct&&!r.skipped).length;
  const skipped=results.filter(r=>r.skipped).length;
  const counted=results.filter(r=>!r.image).length;
  const pct=counted>0?Math.round(correct/counted*100):100;
  const passed=pct>=60;

  document.getElementById('scorePct').textContent=pct+'%';
  document.getElementById('scoreTitle').textContent='答對 '+correct+' / '+counted+' 題';
  const v=document.getElementById('scoreVerdict');
  v.className='score-verdict '+(passed?'pass':'fail');
  v.textContent=passed?'🎉 恭喜通過！（及格標準 60 分）':'⚡ 繼續加油！（及格標準 60 分）';
  document.getElementById('rCorrect').textContent=correct;
  document.getElementById('rWrong').textContent=wrong;
  document.getElementById('rSkipped').textContent=skipped;

  const badResults=results.filter(r=>(!r.correct||r.skipped)&&!r.image);
  if(badResults.length>0){
    document.getElementById('reviewSection').style.display='';
    document.getElementById('retryWrongBtn').style.display='';
    const circles=['①','②','③','④'];
    const reviewList=document.getElementById('reviewList');
    reviewList.innerHTML='';
    badResults.forEach(r=>{
      const div=document.createElement('div');
      div.className='review-item'+(r.skipped?' skipped':'');
      const ansText=r.q.answer.map(a=>circles[a-1]+(r.q.has_image?'':(' '+r.q.options[a-1]))).join('、');
      const selText=r.selected.length>0?r.selected.map(a=>circles[a-1]+(r.q.options[a-1]?' '+r.q.options[a-1]:'')).join('、'):'（跳過）';
      const qShort=r.q.question.length>80?r.q.question.substring(0,78)+'…':r.q.question;
      div.innerHTML=`<div class="review-q">${qShort}</div>
        <div class="review-ans">你的答案：<span>${selText}</span>　正確：<span>${ansText}</span></div>`;
      reviewList.appendChild(div);
    });
  } else {
    document.getElementById('reviewSection').style.display='none';
    document.getElementById('retryWrongBtn').style.display='none';
  }
  showScreen('results');
}

function retryWrong(){
  const wrongQs=results.filter(r=>(!r.correct||r.skipped)&&!r.image).map(r=>r.q);
  if(!wrongQs.length)return;
  quizQuestions=selOrder==='random'?[...wrongQs].sort(()=>Math.random()-.5):wrongQs;
  currentIdx=0; results=[];
  showScreen('quiz');
  renderQuestion();
}

function goHome(){ updateStats(); showScreen('home'); checkSavedSession(); }
function showScreen(id){
  document.querySelectorAll('.screen').forEach(s=>s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  window.scrollTo(0,0);
}

// Exit modal
function showExitModal(){ document.getElementById('exitModal').classList.add('show'); }
function closeExitModal(){ document.getElementById('exitModal').classList.remove('show'); }
function confirmExit(){
  closeExitModal();
  goHome();
}

// ===== SESSION SAVE / RESTORE =====
function saveSession(){
  if(!quizQuestions.length) return;
  const session={
    qIds: quizQuestions.map(q=>q.id),
    currentIdx, mode,
    results: results.map(r=>({
      qId:r.q.id, selected:r.selected, correct:r.correct,
      skipped:!!r.skipped, image:!!r.image
    }))
  };
  localStorage.setItem('savedSession',JSON.stringify(session));
}

function clearSession(){
  localStorage.removeItem('savedSession');
}

function checkSavedSession(){
  const raw=localStorage.getItem('savedSession');
  if(!raw){ document.getElementById('resumeBar').style.display='none'; return; }
  try{
    const s=JSON.parse(raw);
    const done=s.results.length;
    const total=s.qIds.length;
    const modeLabel=s.mode==='practice'?'練習模式':'測驗模式';
    document.getElementById('resumeDesc').textContent=
      modeLabel+'・已作答 '+done+' / '+total+' 題';
    document.getElementById('resumeBar').style.display='flex';
  }catch(e){ clearSession(); document.getElementById('resumeBar').style.display='none'; }
}

function resumeSession(){
  const raw=localStorage.getItem('savedSession');
  if(!raw) return;
  try{
    const s=JSON.parse(raw);
    const qMap={};
    ALL_QUESTIONS.forEach(q=>qMap[q.id]=q);
    quizQuestions=s.qIds.map(id=>qMap[id]).filter(Boolean);
    if(!quizQuestions.length){ clearSession(); checkSavedSession(); return; }
    currentIdx=Math.min(s.currentIdx, quizQuestions.length-1);
    mode=s.mode||'practice';
    results=(s.results||[]).map(r=>({
      q:qMap[r.qId], selected:r.selected||[],
      correct:r.correct, skipped:r.skipped, image:r.image
    })).filter(r=>r.q);
    showScreen('quiz');
    renderQuestion();
  }catch(e){ alert('進度恢復失敗，將重新開始。'); clearSession(); checkSavedSession(); }
}

function discardSession(){
  if(!confirm('確定要丟棄上次未完成的測驗進度嗎？')) return;
  clearSession();
  checkSavedSession();
}

// ===== EXPORT / IMPORT =====
function exportProgress(){
  const data={
    version:1,
    exportDate:new Date().toLocaleDateString('zh-TW'),
    wrongBank, totalStats, questionNotes,
    savedSession:JSON.parse(localStorage.getItem('savedSession')||'null')
  };
  const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});
  const url=URL.createObjectURL(blob);
  const a=document.createElement('a');
  a.href=url;
  const d=new Date();
  const ds=d.getFullYear()+String(d.getMonth()+1).padStart(2,'0')+String(d.getDate()).padStart(2,'0');
  a.download='12500練習進度_'+ds+'.json';
  a.click();
  URL.revokeObjectURL(url);
}

function importProgress(){
  const input=document.createElement('input');
  input.type='file'; input.accept='.json';
  input.onchange=e=>{
    const file=e.target.files[0];
    if(!file) return;
    const reader=new FileReader();
    reader.onload=ev=>{
      try{
        const data=JSON.parse(ev.target.result);
        if(!data.version||!Array.isArray(data.wrongBank)||!data.totalStats)
          throw new Error('格式錯誤');
        wrongBank=data.wrongBank;
        totalStats=data.totalStats;
        localStorage.setItem('wrongBank',JSON.stringify(wrongBank));
        localStorage.setItem('totalStats',JSON.stringify(totalStats));
        if(data.questionNotes && typeof data.questionNotes==='object'){
          questionNotes=data.questionNotes;
          localStorage.setItem('questionNotes',JSON.stringify(questionNotes));
        }
        if(data.savedSession)
          localStorage.setItem('savedSession',JSON.stringify(data.savedSession));
        else
          localStorage.removeItem('savedSession');
        updateStats();
        checkSavedSession();
        const hasSession=!!data.savedSession;
        const noteCount=Object.keys(data.questionNotes||{}).length;
        alert('✅ 匯入成功！\n累計作答：'+totalStats.total+' 題\n錯題庫：'+wrongBank.length+' 題'
          +(noteCount?'\n筆記：'+noteCount+' 題':'')
          +(hasSession?'\n\n📖 上次未完成的測驗已恢復，請點「繼續作答」。':''));
      }catch(err){
        alert('❌ 讀取失敗，請確認選擇的是正確的進度備份檔案。');
      }
    };
    reader.readAsText(file,'utf-8');
  };
  input.click();
}

initHome();
</script>
</body>
</html>"""

html = HTML.replace('__QUESTIONS_JSON__', qs_json)

with open('quiz.html', 'w', encoding='utf-8') as f:
    f.write(html)

size = os.path.getsize('quiz.html')
print(f"Generated quiz.html: {size:,} bytes ({size/1024/1024:.1f} MB)")
