"""Product-pulse page and approval-gated logging endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from src.pulse.analyze import REVIEWS_CSV, analyze
from src.pulse.compose import build_package
from src.pulse.store import commit_approved, write_pulse_preview

router = APIRouter()


class ApproveRequest(BaseModel):
    approved: bool = False


def current_package() -> dict:
    package = build_package(analyze())
    write_pulse_preview(package)
    return package


def _page() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Groww Review Pulse</title>
  <style>
    :root { --bg:#f3f6f1; --ink:#1c2b22; --muted:#5d6b62; --accent:#14643f; --card:#fff; --line:#e3ebe4; }
    * { box-sizing: border-box; }
    body { margin:0; font-family:"Segoe UI", "Helvetica Neue", sans-serif; background:var(--bg); color:var(--ink); }
    a { color: var(--accent); }
    header { position:sticky; top:0; background:rgba(243,246,241,.92); backdrop-filter:blur(8px); border-bottom:1px solid var(--line); }
    .bar { max-width:980px; margin:0 auto; padding:.85rem 1.25rem; display:flex; align-items:center; justify-content:space-between; gap:1rem; }
    .brand { display:flex; align-items:center; gap:.6rem; font-weight:700; color:var(--ink); text-decoration:none; }
    .mark { width:32px; height:32px; border-radius:8px; background:var(--accent); color:#fff; display:grid; place-items:center; }
    nav { display:flex; gap:1.25rem; }
    nav a { color:var(--muted); text-decoration:none; font-size:.95rem; }
    main { max-width:980px; margin:0 auto; padding:2.2rem 1.25rem 3rem; }
    .kicker { letter-spacing:.08em; font-size:.78rem; font-weight:700; color:var(--accent); }
    h1 { font-family:Georgia, "Times New Roman", serif; font-size:clamp(2.4rem, 6vw, 4.2rem); line-height:.95; font-weight:500; margin:.4rem 0 .8rem; }
    .lede { max-width:38rem; font-size:1.05rem; color:#314038; }
    .card { background:var(--card); border:1px solid var(--line); border-radius:18px; padding:1.15rem 1.2rem; margin:1.4rem 0; }
    .row { display:flex; flex-wrap:wrap; gap:.75rem; align-items:end; justify-content:space-between; }
    label.field { display:flex; flex-direction:column; gap:.25rem; font-size:.85rem; color:var(--muted); }
    input[type=date] { border:1px solid var(--line); border-radius:10px; padding:.55rem .7rem; font:inherit; background:#fff; }
    button, .ghost { border-radius:12px; padding:.7rem 1rem; font-weight:650; font:inherit; cursor:pointer; }
    button.primary { background:var(--accent); color:#fff; border:0; }
    button.primary:disabled { opacity:.45; cursor:not-allowed; }
    .ghost { background:#fff; border:1px solid #c9d5cc; color:var(--ink); text-decoration:none; display:inline-block; }
    .file { color:var(--muted); font-size:.92rem; margin-top:.9rem; }
    h2 { font-family:Georgia, "Times New Roman", serif; font-size:2rem; margin:.2rem 0 .8rem; }
    .themes { display:grid; grid-template-columns:repeat(3, 1fr); gap:.75rem; }
    .theme { border:1px solid var(--line); border-radius:16px; padding:.9rem 1rem; background:#fff; }
    .theme strong { font-size:1.15rem; }
    .count { float:right; font-family:Georgia, serif; font-size:1.4rem; }
    .bar { height:4px; background:#e7eee8; border-radius:99px; margin-top:.8rem; }
    .bar span { display:block; height:100%; background:#7dbe86; border-radius:99px; }
    .signal { background:#e7f3ea; border:0; display:grid; grid-template-columns:1.4fr .8fr; gap:1rem; }
    .grid { display:grid; grid-template-columns:1fr 1fr; gap:.8rem; }
    .pulse, .fee { border:1px solid var(--line); border-radius:16px; padding:1rem; background:#fff; }
    pre { white-space:pre-wrap; font-family:inherit; line-height:1.45; }
    .approve { display:flex; justify-content:space-between; gap:1rem; align-items:center; }
    .panel { margin-top:1rem; border-top:1px solid var(--line); padding-top:1rem; }
    label.check { display:flex; gap:.55rem; align-items:flex-start; }
    .ok { background:#e7f3ea; border-radius:12px; padding:.8rem; }
    footer { display:flex; flex-wrap:wrap; gap:1rem; color:var(--muted); font-size:.92rem; margin-top:1rem; }
    @media (max-width:800px) { .themes, .grid, .signal, .approve { grid-template-columns:1fr; display:grid; } }
  </style>
</head>
<body>
<header>
  <div class="bar">
    <a class="brand" href="#top"><span class="mark">↗</span> Review Pulse</a>
    <nav>
      <a href="#reviews">Reviews</a>
      <a href="#outputs">Outputs</a>
      <a href="#approval">Approval</a>
    </nav>
  </div>
</header>
<main id="top">
  <p class="kicker">GROWW / PRODUCT &amp; SUPPORT</p>
  <h1>From reviews to a clear response.</h1>
  <p class="lede">Find the issues customers raise, explain the recurring fee, and review both outputs before logging them.</p>

  <section class="card" id="reviews">
    <p class="kicker">REVIEW INTELLIGENCE</p>
    <div class="row">
      <div>
        <h2>Review sample</h2>
        <p>12-week lookback · 30 Aug 2026 to 22 Nov 2026</p>
      </div>
      <label class="field">Week ending<input type="date" value="2026-11-22" readonly /></label>
      <a class="ghost" href="/reviews.csv">reviews.csv</a>
      <button class="primary" id="analyze" type="button">Analyze reviews</button>
    </div>
    <p class="file">3,244 Google Play reviews are already loaded. The button clusters them. Nothing is logged yet.</p>
  </section>

  <div id="results" hidden>
    <section>
      <div class="row"><h2>Top themes</h2><p id="theme-meta"></p></div>
      <div class="themes" id="theme-cards"></div>
    </section>
    <section class="card signal" id="signal"></section>
    <section id="outputs">
      <div class="row"><h2>Generated outputs</h2><p>Product &amp; Support</p></div>
      <div class="grid">
        <article class="pulse">
          <p class="kicker">INTERNAL UPDATE</p>
          <h2>Weekly product pulse</h2>
          <p id="pulse-meta"></p>
          <pre id="pulse"></pre>
        </article>
        <article class="fee">
          <p class="kicker">CUSTOMER COMMUNICATION</p>
          <h2>Fee explainer</h2>
          <p id="fee-name"></p>
          <ul id="bullets"></ul>
          <p id="fee-links"></p>
          <p id="checked"></p>
        </article>
      </div>
    </section>
    <section class="card" id="approval">
      <div class="approve">
        <div>
          <p class="kicker">MCP ACTIONS</p>
          <h2>Review &amp; approve</h2>
          <p>Append a notes entry and create an unsent email draft. Nothing is sent before you approve.</p>
          <p id="wait">Waiting for approval.</p>
        </div>
        <button class="primary" id="review-actions" type="button">Review actions</button>
      </div>
      <div class="panel" id="approve-panel" hidden>
        <h2>Approve both actions?</h2>
        <form id="approve-form">
          <label class="check"><input id="approve-check" type="checkbox" /> I approve appending this entry to the notes doc and creating an email draft.</label>
          <p><button class="primary" id="approve-btn" type="submit" disabled>Approve and log</button></p>
        </form>
        <div id="result"></div>
      </div>
    </section>
  </div>
  <footer>
    <span>Groww Review Pulse · Product workflow prototype</span>
    <a href="#outputs">Sources</a>
    <a href="/reviews.csv">Reviews CSV</a>
  </footer>
</main>
<script>
const BLURB = {
  short_positive: "Short praise with no specific product issue.",
  app_reliability: "Lag, errors, and updates while people are trading.",
  support_resolution: "Customer care that does not respond.",
  pricing_confusion: "Brokerage and the other charges on a sell.",
  orders_and_withdrawals: "Order execution and money movement."
};
let pack = null;
const esc = (s) => String(s).replace(/[&<>]/g, (c) => ({ "&":"&amp;","<":"&lt;",">":"&gt;" }[c]));
document.getElementById("analyze").onclick = async () => {
  const btn = document.getElementById("analyze");
  btn.disabled = true;
  btn.textContent = "Analyzing…";
  pack = await (await fetch("/api/pulse")).json();
  const max = Math.max(...pack.themes.map((t) => t.count));
  document.getElementById("theme-meta").textContent = pack.review_count + " reviews · " + pack.themes.length + " themes";
  document.getElementById("theme-cards").innerHTML = pack.themes.slice(0, 3).map((t) => `
    <article class="theme"><span class="count">${t.count}</span><strong>${esc(t.label)}</strong>
    <p>${esc(BLURB[t.id] || "")}</p><div class="bar"><span style="width:${Math.round(100 * t.count / max)}%"></span></div></article>`).join("");
  document.getElementById("signal").innerHTML = `
    <div><p class="kicker">RECURRING FEE SIGNAL</p><h2>${esc(pack.fee_name)}</h2>
    <p>${esc(pack.identified_fee_issue)}</p>
    <p>${pack.quotes.map((q) => "“" + esc(q.text) + "” (" + esc(q.review_id) + ", " + esc(q.date) + ")").join("<br><br>")}</p></div>
    <div><p>Top 3</p><ul>${pack.top_themes.map((n) => "<li>" + esc(n) + "</li>").join("")}</ul></div>`;
  document.getElementById("pulse-meta").textContent = pack.weekly_pulse_words + " / 250 words · week ending " + pack.date;
  document.getElementById("pulse").textContent = pack.weekly_pulse;
  document.getElementById("fee-name").textContent = pack.fee_name;
  document.getElementById("bullets").innerHTML = pack.explanation_bullets.map((b) => "<li>" + esc(b) + "</li>").join("");
  document.getElementById("fee-links").innerHTML = pack.source_links.map((u) => `<a href="${esc(u)}">${esc(u)}</a>`).join("<br>");
  document.getElementById("checked").textContent = "Last checked: " + pack.last_checked;
  document.getElementById("results").hidden = false;
  document.getElementById("theme-cards").scrollIntoView({ behavior:"smooth" });
  btn.disabled = false;
  btn.textContent = "Analyze reviews";
};
document.getElementById("review-actions").onclick = () => {
  document.getElementById("approve-panel").hidden = false;
  document.getElementById("approve-panel").scrollIntoView({ behavior:"smooth" });
};
const check = document.getElementById("approve-check");
const button = document.getElementById("approve-btn");
check.onchange = () => { button.disabled = !check.checked; };
document.getElementById("approve-form").onsubmit = async (event) => {
  event.preventDefault();
  if (!check.checked) return;
  button.disabled = true;
  const response = await fetch("/api/pulse/approve", {
    method:"POST", headers:{ "Content-Type":"application/json" },
    body: JSON.stringify({ approved:true })
  });
  const data = await response.json();
  const result = document.getElementById("result");
  if (!response.ok) { result.textContent = data.detail || "Approval failed"; button.disabled = false; return; }
  document.getElementById("wait").textContent = "Approved. Nothing was sent.";
  const note = { date:pack.date, top_themes:pack.top_themes, weekly_pulse:pack.weekly_pulse.trim(), identified_fee_issue:pack.identified_fee_issue, explanation_bullets:pack.explanation_bullets, source_links:pack.source_links };
  result.innerHTML = `<div class="ok"><p><strong>Notes entry appended</strong></p><pre>${esc(JSON.stringify(note, null, 2))}</pre><p><strong>Email draft created, not sent</strong></p><p>Subject: Weekly Product Pulse + Customer Clarification — Equity brokerage and sell-side charges</p></div>`;
};
</script>
</body>
</html>"""


@router.get("/", response_class=HTMLResponse)
@router.get("/pulse", response_class=HTMLResponse)
def pulse_page():
    return _page()


@router.get("/reviews.csv")
def reviews_csv():
    return FileResponse(REVIEWS_CSV, media_type="text/csv", filename="groww_reviews.csv")


@router.get("/api/pulse")
def pulse_api():
    return current_package()


@router.post("/api/pulse/approve")
def pulse_approve(body: ApproveRequest):
    if not body.approved:
        raise HTTPException(status_code=400, detail="Approval is required before logging.")
    package = current_package()
    paths = commit_approved(package)
    return {"ok": True, "sent": False, **paths}
