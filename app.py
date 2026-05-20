import streamlit as st
import pickle
import os
import json
import datetime
from train_model import train_and_save

st.set_page_config(
    page_title="SpamShield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600&display=swap');

* { box-sizing: border-box; }
html, body, [class*="css"], .stApp { background-color:#080c10 !important; color:#c9d1d9 !important; }

.stApp::before {
    content:''; position:fixed; top:0; left:0; right:0; bottom:0;
    background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,255,180,0.012) 2px,rgba(0,255,180,0.012) 4px);
    pointer-events:none; z-index:0;
}

/* ── Header ── */
.shield-header { text-align:center; padding:1.5rem 0 1rem; border-bottom:1px solid #00ffb414; margin-bottom:1.5rem; }
.shield-title { font-family:'Share Tech Mono',monospace !important; font-size:2.6rem !important; color:#00ffb4 !important; letter-spacing:6px; text-transform:uppercase; margin:0 !important; text-shadow:0 0 20px rgba(0,255,180,0.3); }
.shield-sub { color:#8b949e; font-family:'Share Tech Mono',monospace !important; font-size:0.72rem; letter-spacing:3px; text-transform:uppercase; margin-top:0.4rem; }
.version-tag { display:inline-block; background:rgba(0,255,180,0.08); border:1px solid rgba(0,255,180,0.25); color:#00ffb4; font-family:'Share Tech Mono',monospace; font-size:0.62rem; padding:2px 10px; border-radius:2px; letter-spacing:2px; margin-top:0.4rem; }

/* ── Stats bar ── */
.stats-bar { display:flex; gap:12px; margin-bottom:1.4rem; }
.stat-pill { flex:1; background:#0d1117; border:1px solid #21262d; border-radius:4px; padding:10px 14px; text-align:center; }
.stat-num { font-family:'Share Tech Mono',monospace; font-size:1.4rem; display:block; }
.stat-num.green { color:#00ffb4; }
.stat-num.red { color:#ff5555; }
.stat-num.amber { color:#f0883e; }
.stat-num.muted { color:#8b949e; }
.stat-key { font-family:'Share Tech Mono',monospace; font-size:0.6rem; color:#484f58; letter-spacing:2px; text-transform:uppercase; display:block; margin-top:2px; }

/* ── Section label ── */
.section-label { font-family:'Share Tech Mono',monospace !important; font-size:0.68rem !important; letter-spacing:3px; text-transform:uppercase; color:#00ffb4 !important; border-left:3px solid #00ffb4; padding-left:10px; margin-bottom:1rem; }

/* ── Tabs ── */
.tab-bar { display:flex; gap:4px; margin-bottom:1rem; border-bottom:1px solid #21262d; padding-bottom:0; }
.tab-btn { font-family:'Share Tech Mono',monospace; font-size:0.7rem; letter-spacing:2px; text-transform:uppercase; padding:8px 16px; border:1px solid transparent; border-bottom:none; border-radius:3px 3px 0 0; cursor:pointer; background:transparent; color:#484f58; transition:all 0.2s; }
.tab-btn.active { color:#00ffb4; border-color:#21262d; border-bottom:1px solid #080c10; background:#0d1117; }
.tab-btn:hover:not(.active) { color:#8b949e; }
.tab-count { display:inline-block; background:#161b22; border-radius:10px; padding:1px 7px; font-size:0.6rem; margin-left:5px; color:#8b949e; }
.tab-count.red { background:rgba(255,85,85,0.15); color:#ff5555; }
.tab-count.green { background:rgba(0,255,180,0.1); color:#00ffb4; }
.tab-count.amber { background:rgba(240,136,62,0.15); color:#f0883e; }

/* ── Message cards ── */
.msg-card { background:#0d1117; border:1px solid #21262d; border-radius:4px; padding:14px 16px; margin:6px 0; transition:border-color 0.2s; position:relative; }
.msg-card:hover { border-color:#30363d; }
.msg-card.spam { border-left:3px solid #ff5555; background:rgba(255,85,85,0.03); }
.msg-card.safe { border-left:3px solid #00ffb4; }
.msg-card.promo { border-left:3px solid #f0883e; }
.msg-card.user-reported-spam { border-left:3px solid #ff5555; opacity:0.7; }
.msg-card.user-marked-safe { border-left:3px solid #00ffb4; }

.msg-header { display:flex; align-items:center; gap:8px; margin-bottom:6px; }
.msg-sender { font-family:'Share Tech Mono',monospace; font-size:0.8rem; color:#e6edf3; }
.msg-time { font-family:'Share Tech Mono',monospace; font-size:0.65rem; color:#484f58; margin-left:auto; }

.trust-badge { display:inline-flex; align-items:center; gap:4px; font-family:'Share Tech Mono',monospace; font-size:0.6rem; letter-spacing:1px; padding:2px 8px; border-radius:2px; }
.trust-badge.safe { background:rgba(0,255,180,0.1); border:1px solid rgba(0,255,180,0.3); color:#00ffb4; }
.trust-badge.spam { background:rgba(255,85,85,0.1); border:1px solid rgba(255,85,85,0.3); color:#ff5555; }
.trust-badge.promo { background:rgba(240,136,62,0.1); border:1px solid rgba(240,136,62,0.3); color:#f0883e; }
.trust-badge.unknown { background:rgba(139,148,158,0.1); border:1px solid rgba(139,148,158,0.2); color:#8b949e; }

.msg-body { font-family:'Exo 2',sans-serif; font-size:0.85rem; color:#8b949e; line-height:1.5; margin:4px 0 10px; }

.warn-banner { background:rgba(255,85,85,0.08); border:1px solid rgba(255,85,85,0.25); border-radius:3px; padding:6px 12px; margin:6px 0; font-family:'Share Tech Mono',monospace; font-size:0.68rem; color:#ff8888; letter-spacing:1px; }
.promo-banner { background:rgba(240,136,62,0.08); border:1px solid rgba(240,136,62,0.2); border-radius:3px; padding:6px 12px; margin:6px 0; font-family:'Share Tech Mono',monospace; font-size:0.68rem; color:#f0883e; letter-spacing:1px; }

.conf-mini { font-family:'Share Tech Mono',monospace; font-size:0.65rem; color:#484f58; margin-bottom:4px; }
.conf-bar-bg { background:#161b22; border-radius:2px; height:4px; width:100%; overflow:hidden; margin-bottom:8px; }
.conf-bar-spam { background:linear-gradient(90deg,#ff5555,#ff8888); height:100%; border-radius:2px; }
.conf-bar-ham { background:linear-gradient(90deg,#00ffb4,#00cc90); height:100%; border-radius:2px; }
.conf-bar-promo { background:linear-gradient(90deg,#f0883e,#f5a06e); height:100%; border-radius:2px; }

/* ── Action buttons row ── */
.action-row { display:flex; gap:6px; margin-top:8px; flex-wrap:wrap; }

/* ── Scan panel ── */
div[data-testid="stTextArea"] textarea { background:#0d1117 !important; border:1px solid #21262d !important; border-radius:4px !important; color:#e6edf3 !important; font-family:'Share Tech Mono',monospace !important; font-size:0.85rem !important; caret-color:#00ffb4; }
div[data-testid="stTextArea"] textarea:focus { border-color:#00ffb4 !important; box-shadow:0 0 0 1px rgba(0,255,180,0.2) !important; }

div[data-testid="stButton"] button { background:transparent !important; border:1px solid #21262d !important; color:#8b949e !important; font-family:'Share Tech Mono',monospace !important; font-size:0.68rem !important; border-radius:3px !important; padding:7px 10px !important; transition:all 0.15s; letter-spacing:1px; }
div[data-testid="stButton"] button:hover { border-color:#00ffb4 !important; color:#00ffb4 !important; background:rgba(0,255,180,0.05) !important; }

/* Result boxes */
.result-spam { background:rgba(255,85,85,0.06); border:1px solid rgba(255,85,85,0.4); border-left:4px solid #ff5555; border-radius:4px; padding:20px 24px; margin:1rem 0; }
.result-ham { background:rgba(0,255,180,0.04); border:1px solid rgba(0,255,180,0.3); border-left:4px solid #00ffb4; border-radius:4px; padding:20px 24px; margin:1rem 0; }
.result-promo { background:rgba(240,136,62,0.05); border:1px solid rgba(240,136,62,0.35); border-left:4px solid #f0883e; border-radius:4px; padding:20px 24px; margin:1rem 0; }
.result-label { font-family:'Share Tech Mono',monospace !important; font-size:1.3rem; letter-spacing:4px; text-transform:uppercase; margin:0 0 5px 0; }
.result-sub { font-size:0.78rem; opacity:0.6; font-family:'Share Tech Mono',monospace; letter-spacing:1px; }

/* Model cards */
.model-panel { background:#0d1117; border:1px solid #21262d; border-radius:4px; padding:14px 16px; margin:6px 0; }
.model-panel.best { border-color:rgba(0,255,180,0.35); background:rgba(0,255,180,0.03); }
.model-name { font-family:'Share Tech Mono',monospace; font-size:0.82rem; color:#e6edf3; letter-spacing:1px; margin-bottom:8px; }
.model-name.best { color:#00ffb4; }
.best-badge { display:inline-block; background:rgba(0,255,180,0.1); border:1px solid rgba(0,255,180,0.3); color:#00ffb4; font-family:'Share Tech Mono',monospace; font-size:0.58rem; padding:2px 7px; border-radius:2px; letter-spacing:2px; margin-left:7px; vertical-align:middle; }
.metric-grid { display:grid; grid-template-columns:1fr 1fr; gap:6px; }
.metric-item { background:#161b22; border-radius:3px; padding:7px 9px; }
.metric-val { font-family:'Share Tech Mono',monospace; font-size:0.95rem; color:#00ffb4; display:block; }
.metric-val.warn { color:#f0883e; }
.metric-key { font-size:0.62rem; color:#484f58; letter-spacing:1px; text-transform:uppercase; display:block; margin-top:2px; }

.step-row { display:flex; align-items:flex-start; gap:12px; margin:6px 0; padding:9px 12px; background:#0d1117; border-radius:3px; border:1px solid #161b22; }
.step-num { font-family:'Share Tech Mono',monospace; font-size:0.72rem; color:#00ffb4; min-width:22px; opacity:0.7; }
.step-text { font-size:0.82rem; color:#8b949e; line-height:1.5; font-family:'Exo 2',sans-serif; }
.step-text strong { color:#c9d1d9; }

.cyber-footer { text-align:center; font-family:'Share Tech Mono',monospace; font-size:0.62rem; color:#30363d; letter-spacing:2px; padding:1.5rem 0; border-top:1px solid #161b22; margin-top:2rem; }

.block-container { padding-top:1rem !important; max-width:1300px !important; }
footer,#MainMenu,header { display:none !important; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ──────────────────────────────────────────────────────
INBOX_FILE = "inbox.json"

SAMPLE_INBOX = [
    {"id":1,"sender":"Mom","body":"Hey honey, dinner is ready. Come home soon okay?","time":"09:14","category":"primary","spam_score":2.1,"reported":None},
    {"id":2,"sender":"Rahul","body":"Bro are you coming to the match tonight? It's at 8pm.","time":"10:32","category":"primary","spam_score":1.8,"reported":None},
    {"id":3,"sender":"HDFC Bank","body":"Your account statement for April is ready. Login to netbanking to view.","time":"11:05","category":"primary","spam_score":8.4,"reported":None},
    {"id":4,"sender":"Flipkart","body":"SALE ALERT! Up to 70% off on electronics. Shop now before stocks run out!","time":"11:22","category":"promotions","spam_score":61.2,"reported":None},
    {"id":5,"sender":"Swiggy","body":"Your favourite restaurant is offering 40% off today only. Order now!","time":"12:01","category":"promotions","spam_score":55.7,"reported":None},
    {"id":6,"sender":"Unknown","body":"WINNER!! You have been selected for a Rs.50,000 prize. Call 9999-XXXXX now to claim!","time":"12:45","category":"spam","spam_score":98.7,"reported":None},
    {"id":7,"sender":"+91-8800-XXXX","body":"FREE entry! Win FA Cup tickets. Text WIN to 87121. T&C apply. Helpline 0845 277 4014.","time":"13:10","category":"spam","spam_score":97.3,"reported":None},
    {"id":8,"sender":"Prof. Sharma","body":"Class rescheduled to 3pm tomorrow. Please inform others in the group.","time":"14:00","category":"primary","spam_score":3.2,"reported":None},
]

def load_inbox():
    if os.path.exists(INBOX_FILE):
        with open(INBOX_FILE) as f:
            return json.load(f)
    return [m.copy() for m in SAMPLE_INBOX]

def save_inbox(inbox):
    with open(INBOX_FILE,"w") as f:
        json.dump(inbox, f)

def category_color(cat):
    return {"primary":"green","promotions":"amber","spam":"red"}.get(cat,"muted")

def trust_label(msg):
    r = msg.get("reported")
    if r == "spam": return ("spam","⚠ REPORTED SPAM")
    if r == "safe": return ("safe","✓ MARKED SAFE")
    sc = msg["spam_score"]
    if sc < 20:  return ("safe","✓ TRUSTED")
    if sc < 60:  return ("promo","~ PROMOTIONAL")
    return ("spam","⚠ THREAT")

def warn_banner(msg):
    r = msg.get("reported")
    sc = msg["spam_score"]
    if r == "spam":
        return '<div class="warn-banner">⚠ YOU REPORTED THIS AS SPAM</div>'
    if r == "safe":
        return '<div class="trust-badge safe" style="margin:6px 0;display:inline-flex;">✓ YOU MARKED THIS AS SAFE</div>'
    if sc >= 60:
        return f'<div class="warn-banner">⚠ HIGH THREAT PROBABILITY · {sc:.1f}% SPAM SCORE · DO NOT CLICK LINKS</div>'
    if sc >= 20:
        return f'<div class="promo-banner">~ PROMOTIONAL CONTENT DETECTED · {sc:.1f}% SPAM SCORE</div>'
    return ""

# ── Load models ───────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_models():
    if not os.path.exists("model.pkl"):
        with st.spinner("[ INITIALISING THREAT DETECTION ENGINE... ]"):
            train_and_save()
    with open("model.pkl","rb") as f: model = pickle.load(f)
    with open("vectorizer.pkl","rb") as f: vectorizer = pickle.load(f)
    with open("results.pkl","rb") as f: data = pickle.load(f)
    return model, vectorizer, data["results"], data["best"]

if not os.path.exists("spam.csv"):
    st.error("[ ERROR ] spam.csv not found. Place dataset in project root.")
    st.stop()

model, vectorizer, results, best_name = load_models()

if "inbox" not in st.session_state:
    st.session_state.inbox = load_inbox()

# ── Header ────────────────────────────────────────────────────────
st.markdown("""
<div class="shield-header">
    <div class="shield-title">⬡ SpamShield</div>
    <div class="shield-sub">SMS Threat Detection Engine</div>
    <div class="version-tag">v2.0 &nbsp;·&nbsp; SUPERVISED LEARNING &nbsp;·&nbsp; TF-IDF</div>
</div>
""", unsafe_allow_html=True)

# ── Stats bar ─────────────────────────────────────────────────────
inbox = st.session_state.inbox
total   = len(inbox)
n_spam  = sum(1 for m in inbox if m["category"]=="spam" or m.get("reported")=="spam")
n_promo = sum(1 for m in inbox if m["category"]=="promotions" and m.get("reported") != "spam")
n_safe  = total - n_spam - n_promo
n_reported = sum(1 for m in inbox if m.get("reported") is not None)

st.markdown(f"""
<div class="stats-bar">
    <div class="stat-pill"><span class="stat-num green">{n_safe}</span><span class="stat-key">Safe</span></div>
    <div class="stat-pill"><span class="stat-num amber">{n_promo}</span><span class="stat-key">Promotions</span></div>
    <div class="stat-pill"><span class="stat-num red">{n_spam}</span><span class="stat-key">Blocked</span></div>
    <div class="stat-pill"><span class="stat-num muted">{n_reported}</span><span class="stat-key">Reported</span></div>
    <div class="stat-pill"><span class="stat-num muted">{total}</span><span class="stat-key">Total</span></div>
</div>
""", unsafe_allow_html=True)

# ── Main Layout ───────────────────────────────────────────────────
left, right = st.columns([1.1, 1], gap="large")

# ════════════════════════════════════════════════════════
# LEFT — Inbox
# ════════════════════════════════════════════════════════
with left:
    st.markdown('<div class="section-label">// Inbox</div>', unsafe_allow_html=True)

    # Tab selector
    tabs = ["Primary", "Promotions", "Spam / Blocked"]
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Primary"

    t1, t2, t3 = st.columns(3)
    for col, tab in zip([t1,t2,t3], tabs):
        with col:
            if st.button(tab, key=f"tab_{tab}"):
                st.session_state.active_tab = tab
                st.rerun()

    active = st.session_state.active_tab
    cat_map = {"Primary":"primary","Promotions":"promotions","Spam / Blocked":"spam"}
    cat_key = cat_map[active]

    # Filter messages
    if cat_key == "spam":
        filtered = [m for m in inbox if m["category"]=="spam" or m.get("reported")=="spam"]
    elif cat_key == "promotions":
        filtered = [m for m in inbox if m["category"]=="promotions" and m.get("reported")!="spam"]
    else:
        filtered = [m for m in inbox if m["category"]=="primary" and m.get("reported")!="spam"]

    # Tab indicator
    tab_color = {"primary":"green","promotions":"amber","spam":"red"}[cat_key]
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;padding:8px 12px;background:#0d1117;border-radius:3px;border:1px solid #21262d;">
        <span style="font-family:'Share Tech Mono',monospace;font-size:0.68rem;letter-spacing:2px;color:#{'00ffb4' if cat_key=='primary' else 'f0883e' if cat_key=='promotions' else 'ff5555'};">
            {'▶' if cat_key=='primary' else '◈' if cat_key=='promotions' else '⊗'} {active.upper()}
        </span>
        <span style="font-family:'Share Tech Mono',monospace;font-size:0.62rem;color:#484f58;margin-left:auto;">{len(filtered)} MESSAGES</span>
    </div>
    """, unsafe_allow_html=True)

    if not filtered:
        st.markdown('<div style="text-align:center;padding:2rem;color:#484f58;font-family:Share Tech Mono,monospace;font-size:0.75rem;letter-spacing:2px;">[ NO MESSAGES ]</div>', unsafe_allow_html=True)
    else:
        for msg in filtered:
            badge_cls, badge_txt = trust_label(msg)
            card_cls = "msg-card"
            if msg.get("reported") == "spam": card_cls += " spam"
            elif msg.get("reported") == "safe": card_cls += " safe"
            elif msg["category"] == "spam": card_cls += " spam"
            elif msg["category"] == "promotions": card_cls += " promo"
            else: card_cls += " safe"

            sc = msg["spam_score"]
            bar_cls = "conf-bar-spam" if sc>=60 else "conf-bar-promo" if sc>=20 else "conf-bar-ham"
            banner_html = warn_banner(msg)

            st.markdown(f"""
            <div class="{card_cls}">
                <div class="msg-header">
                    <span class="msg-sender">{msg['sender']}</span>
                    <span class="trust-badge {badge_cls}">{badge_txt}</span>
                    <span class="msg-time">{msg['time']}</span>
                </div>
                <div class="msg-body">{msg['body']}</div>
                {banner_html}
                <div class="conf-mini">THREAT SCORE: {sc:.1f}%</div>
                <div class="conf-bar-bg"><div class="{bar_cls}" style="width:{min(sc,100):.0f}%"></div></div>
            </div>
            """, unsafe_allow_html=True)

            # Action buttons
            idx = next(i for i,m in enumerate(inbox) if m["id"]==msg["id"])
            b1, b2, b3 = st.columns([1,1,1])
            with b1:
                r = msg.get("reported")
                label = "✓ REPORTED" if r=="spam" else "⚠ REPORT SPAM"
                if st.button(label, key=f"rspam_{msg['id']}"):
                    st.session_state.inbox[idx]["reported"] = "spam"
                    st.session_state.inbox[idx]["category"] = "spam"
                    save_inbox(st.session_state.inbox)
                    st.rerun()
            with b2:
                label2 = "✓ SAFE" if msg.get("reported")=="safe" else "✓ MARK SAFE"
                if st.button(label2, key=f"rsafe_{msg['id']}"):
                    st.session_state.inbox[idx]["reported"] = "safe"
                    st.session_state.inbox[idx]["category"] = "primary"
                    save_inbox(st.session_state.inbox)
                    st.rerun()
            with b3:
                if st.button("↺ RESET", key=f"rreset_{msg['id']}"):
                    st.session_state.inbox[idx]["reported"] = None
                    orig = next((m for m in SAMPLE_INBOX if m["id"]==msg["id"]), None)
                    if orig:
                        st.session_state.inbox[idx]["category"] = orig["category"]
                    save_inbox(st.session_state.inbox)
                    st.rerun()

            st.markdown("<hr style='border:none;border-top:1px solid #161b22;margin:4px 0 8px;'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# RIGHT — Scanner + Models
# ════════════════════════════════════════════════════════
with right:
    # ── Scan new message ──
    st.markdown('<div class="section-label">// Scan New Message</div>', unsafe_allow_html=True)

    if 'prefill' not in st.session_state:
        st.session_state.prefill = ""

    user_input = st.text_area(
        label="",
        value=st.session_state.prefill,
        placeholder="Paste or type any SMS to scan...",
        height=120,
        label_visibility="collapsed",
        key="msg_input"
    )

    st.markdown('<div class="section-label" style="margin-top:0.8rem;">// Quick Test Vectors</div>', unsafe_allow_html=True)
    examples = {
        "[SPAM] Prize":    "WINNER! You've been selected for a Rs.50,000 prize. Call now to claim!",
        "[SPAM] Phishing": "URGENT: Your bank account suspended. Verify at http://hdfc-secure.xyz now.",
        "[HAM] Friend":    "Hey are you coming tonight? Let me know by 7.",
        "[HAM] Delivery":  "Your order has been shipped. Expected delivery: Thursday.",
    }
    c1, c2 = st.columns(2)
    for i,(label,text) in enumerate(examples.items()):
        col = c1 if i%2==0 else c2
        with col:
            if st.button(label, key=f"ex_{i}"):
                st.session_state.prefill = text
                st.rerun()

    st.markdown("<div style='margin-top:0.8rem'></div>", unsafe_allow_html=True)

    scan_col, add_col = st.columns([2,1])
    with scan_col:
        run = st.button("[ RUN ANALYSIS ]", key="analyse")
    with add_col:
        add_inbox = st.button("[ + ADD TO INBOX ]", key="add_inbox")

    if run and user_input.strip():
        vec      = vectorizer.transform([user_input])
        pred     = model.predict(vec)[0]
        proba    = model.predict_proba(vec)[0]
        spam_pct = round(proba[1]*100,1)
        ham_pct  = round(proba[0]*100,1)

        # Categorise
        if spam_pct >= 60:
            result_cat = "spam"
        elif spam_pct >= 20:
            result_cat = "promotions"
        else:
            result_cat = "primary"

        if result_cat == "spam":
            st.markdown(f"""
            <div class="result-spam">
                <div class="result-label" style="color:#ff5555;">⚠ THREAT DETECTED</div>
                <div class="result-sub">SPAM &nbsp;·&nbsp; Confidence: {spam_pct}% &nbsp;·&nbsp; Category: BLOCKED</div>
            </div>""", unsafe_allow_html=True)
        elif result_cat == "promotions":
            st.markdown(f"""
            <div class="result-promo">
                <div class="result-label" style="color:#f0883e;">~ PROMOTIONAL</div>
                <div class="result-sub">LIKELY PROMO &nbsp;·&nbsp; Spam score: {spam_pct}% &nbsp;·&nbsp; Category: PROMOTIONS</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-ham">
                <div class="result-label" style="color:#00ffb4;">✓ CLEAR</div>
                <div class="result-sub">LEGITIMATE &nbsp;·&nbsp; Confidence: {ham_pct}% &nbsp;·&nbsp; Category: PRIMARY</div>
            </div>""", unsafe_allow_html=True)

        bar_cls = "conf-bar-spam" if spam_pct>=60 else "conf-bar-promo" if spam_pct>=20 else "conf-bar-ham"
        st.markdown(f"""
        <div style="margin-top:0.8rem;">
            <div class="conf-mini">LEGITIMATE &nbsp; {ham_pct}%</div>
            <div class="conf-bar-bg"><div class="conf-bar-ham" style="width:{ham_pct}%"></div></div>
            <div class="conf-mini" style="margin-top:8px;">SPAM &nbsp; {spam_pct}%</div>
            <div class="conf-bar-bg"><div class="{bar_cls}" style="width:{spam_pct}%"></div></div>
        </div>""", unsafe_allow_html=True)

        st.session_state["last_scan"] = {
            "body": user_input,
            "spam_score": spam_pct,
            "category": result_cat
        }

    elif run:
        st.warning("[ INPUT REQUIRED ] Enter a message to analyse.")

    # Add to inbox
    if add_inbox:
        last = st.session_state.get("last_scan")
        if last:
            new_id = max(m["id"] for m in st.session_state.inbox) + 1
            now = datetime.datetime.now().strftime("%H:%M")
            st.session_state.inbox.insert(0, {
                "id": new_id,
                "sender": "Scanned",
                "body": last["body"],
                "time": now,
                "category": last["category"],
                "spam_score": last["spam_score"],
                "reported": None
            })
            save_inbox(st.session_state.inbox)
            st.success(f"[ ADDED ] Message added to {last['category'].upper()} inbox.")
            st.rerun()
        else:
            st.warning("[ SCAN FIRST ] Run analysis before adding to inbox.")

    st.markdown("<div style='margin-top:1.4rem'></div>", unsafe_allow_html=True)

    # ── Classifier Benchmark ──
    st.markdown('<div class="section-label">// Classifier Benchmark</div>', unsafe_allow_html=True)

    for name, m in results.items():
        is_best  = name == best_name
        badge    = '<span class="best-badge">ACTIVE</span>' if is_best else ''
        card_cls = "model-panel best" if is_best else "model-panel"
        name_cls = "model-name best"  if is_best else "model-name"
        acc_cls  = "metric-val" if m['accuracy']>=97 else "metric-val warn"
        st.markdown(f"""
        <div class="{card_cls}">
            <div class="{name_cls}">{name}{badge}</div>
            <div class="metric-grid">
                <div class="metric-item"><span class="{acc_cls}">{m['accuracy']}%</span><span class="metric-key">Accuracy</span></div>
                <div class="metric-item"><span class="metric-val">{m['precision']}%</span><span class="metric-key">Precision</span></div>
                <div class="metric-item"><span class="metric-val">{m['recall']}%</span><span class="metric-key">Recall</span></div>
                <div class="metric-item"><span class="metric-val">{m['f1']}%</span><span class="metric-key">F1 Score</span></div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Pipeline ──
    st.markdown('<div class="section-label" style="margin-top:1.2rem;">// Pipeline</div>', unsafe_allow_html=True)
    for num,text in [
        ("01","<strong>Dataset</strong> — 5,574 labelled SMS messages (UCI)"),
        ("02","<strong>Vectorisation</strong> — TF-IDF converts text → numeric features"),
        ("03","<strong>Split</strong> — 80% train / 20% test, stratified"),
        ("04","<strong>Train</strong> — 3 classifiers fitted simultaneously"),
        ("05","<strong>Select</strong> — Best model chosen by F1 score"),
        ("06","<strong>Predict</strong> — Live inference with confidence scores"),
    ]:
        st.markdown(f'<div class="step-row"><span class="step-num">{num}</span><span class="step-text">{text}</span></div>', unsafe_allow_html=True)

st.markdown('<div class="cyber-footer">SPAMSHIELD v2.0 &nbsp;·&nbsp; SCIKIT-LEARN &nbsp;·&nbsp; TF-IDF &nbsp;·&nbsp; UCI SMS SPAM COLLECTION</div>', unsafe_allow_html=True)
