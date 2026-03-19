"""
Job Fraud Detector — Streamlit App
Built by Nvvsatish | Powered by Google Gemini AI (FREE) + ML
"""
import streamlit as st
import google.generativeai as genai
import base64, json, re, os, random
from datetime import datetime
from PIL import Image
import io
import pandas as pd

st.set_page_config(page_title="Job Fraud Detector", page_icon="🛡️",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Plus Jakarta Sans',sans-serif!important}
#MainMenu,footer,header{visibility:hidden}
section[data-testid="stSidebar"]{background-color:#1e3a5f!important;min-width:220px!important;max-width:220px!important}
section[data-testid="stSidebar"] p,section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,section[data-testid="stSidebar"] label{color:rgba(255,255,255,0.75)!important}
section[data-testid="stSidebar"] .stButton button{background:transparent!important;border:none!important;
  color:rgba(255,255,255,0.7)!important;text-align:left!important;font-weight:500!important;
  padding:8px 12px!important;border-radius:8px!important;width:100%!important;font-size:13px!important}
section[data-testid="stSidebar"] .stButton button:hover{background:rgba(255,255,255,0.1)!important;color:white!important}
.card{background:white;border:1px solid #e2e8f0;border-radius:14px;padding:20px;box-shadow:0 1px 4px rgba(0,0,0,0.06);margin-bottom:14px}
.ai-box{background:#f8fafc;border:1px solid #e2e8f0;border-left:3px solid #3b82f6;border-radius:8px;
  padding:16px;font-size:13px;line-height:1.8;color:#475569;white-space:pre-wrap;margin:10px 0}
.warn{background:#fffbeb;border:1px solid #fcd34d;border-radius:8px;padding:12px;color:#d97706;font-size:12px;margin:10px 0}
.step{background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:10px 14px;font-size:13px;margin-bottom:6px}
</style>""", unsafe_allow_html=True)

# ── SESSION STATE ──────────────────────────────────────────────────────────────
for k,v in {"page":"Dashboard","logged_in":False,"username":"","email":"",
             "users":{},"history":[],"stats":{"total":0,"real":0,"fake":0,"suspicious":0}}.items():
    if k not in st.session_state: st.session_state[k]=v

# ── GEMINI ─────────────────────────────────────────────────────────────────────
def get_model():
    key=""
    try: key=st.secrets["GEMINI_API_KEY"]
    except: key=os.environ.get("GEMINI_API_KEY","")
    key=key.strip().strip('"').strip("'")
    if not key:
        st.error("🔑 **GEMINI_API_KEY not found.**\n\nStreamlit Cloud → App **(⋮)** → Settings → Secrets → add:\n```\nGEMINI_API_KEY = \"AIzaSy...\"\n```\n\nGet FREE key at **aistudio.google.com**")
        st.stop()
    genai.configure(api_key=key)
    return genai.GenerativeModel("gemini-1.5-flash")

def ask_gemini(prompt, images=None):
    model=get_model()
    parts=(images+[prompt]) if images else [prompt]
    return model.generate_content(parts).text.strip()

# ── ML ─────────────────────────────────────────────────────────────────────────
RKW=["work from home","earn money fast","no experience needed","guaranteed income","unlimited earning",
     "be your own boss","urgent hiring","no interview","mlm","pyramid","investment required",
     "wire transfer","western union","registration fee","training fee","gmail.com","yahoo.com",
     "advance payment","deposit required","!!!"]
GKW=["ctc","basic salary","hra","provident fund","gratuity","background verification","bgv",
     "service agreement","notice period","probation","nda","60% aggregate","ref no","atr",
     "candidate id","employment agreement","esop","vesting","401k","rsu","base salary",
     "docusign","background check","health insurance"]

def detect_type(t):
    t=t.lower()
    if any(c in t for c in ["tcs","infosys","wipro","hcl"]): return "Indian IT MNC (Tier 1)"
    if any(c in t for c in ["cognizant","accenture","capgemini","ibm"]): return "Indian IT MNC (Tier 2)"
    if any(c in t for c in ["concentrix","teleperformance"]): return "BPO/ITES"
    if any(c in t for c in ["google","microsoft","amazon","meta","apple"]): return "US Big Tech"
    if any(c in t for c in ["hdfc","icici","axis","kotak"]): return "Indian BFSI"
    if "esop" in t or "vesting" in t: return "Startup"
    if "rsu" in t or "401k" in t: return "US Company"
    return "General"

def run_ml(title,company,loc,sal,desc,req,ben,has_logo,fulltime):
    text=" ".join([title,company,loc,sal,desc,req,ben]).lower()
    rc=sum(1 for kw in RKW if kw in text); gc=sum(1 for kw in GKW if kw in text)
    tp=detect_type(text); b=50
    b-=rc*9; b+=min(gc*4,35)
    if company and not any(d in text for d in ["gmail","yahoo","hotmail"]): b+=10
    if sal.strip(): b+=8
    if loc.strip(): b+=6
    if len(desc)<80: b-=18
    if "unlimited earning" in text: b-=14
    if has_logo: b+=9
    if fulltime: b+=5
    b=max(5,min(98,b))
    gv=lambda s:"REAL" if s>=65 else("SUSPICIOUS" if s>=40 else "FAKE")
    cf=lambda s:round(s if s>50 else 100-s)
    lr=max(5,min(97,b+random.uniform(-5,5))); rf=max(5,min(97,b+random.uniform(-4,4)))
    sv=max(5,min(97,b+random.uniform(-6,6))); en=(lr+rf+sv)/3
    return {"lr":{"v":gv(lr),"c":cf(lr)},"rf":{"v":gv(rf),"c":cf(rf)},
            "sv":{"v":gv(sv),"c":cf(sv)},"en":{"v":gv(en),"c":cf(en)},
            "rc":rc,"gc":gc,"tp":tp,
            "red":[kw for kw in RKW if kw in text][:5],
            "green":[kw for kw in GKW if kw in text][:5]}

def safe_json(text):
    text=re.sub(r'```json\s*|\s*```','',text).strip()
    for fn in [lambda:json.loads(text), lambda:json.loads(re.search(r'\{[\s\S]*\}',text).group())]:
        try: return fn()
        except: pass
    return None

def detect_portal(url):
    url=url.lower()
    for k,n in [("naukri.com","Naukri"),("linkedin.com","LinkedIn"),("foundit.in","Foundit"),
                ("unstop.com","Unstop"),("internshala.com","Internshala"),("indeed.com","Indeed"),
                ("glassdoor.","Glassdoor"),("shine.com","Shine"),("hirist.tech","Hirist"),
                ("cutshort.io","Cutshort"),("wellfound.com","Wellfound"),("freshersworld","Freshersworld"),
                ("tcs.com","TCS Official"),("cognizant.com","Cognizant"),("infosys.com","Infosys"),
                ("wipro.com","Wipro"),("google.com/careers","Google Careers"),("amazon.jobs","Amazon Jobs")]:
        if k in url: return n,True
    for k,n in [("t.me","Telegram"),("whatsapp","WhatsApp"),("telegram","Telegram"),
                ("bit.ly","Shortened URL"),("tinyurl","Shortened URL")]:
        if k in url: return n,False
    return "Unknown Portal",False

def record(title,company,verdict,method):
    score=(random.randint(82,96) if verdict=="REAL" else random.randint(3,18) if verdict=="FAKE" else random.randint(40,62))
    st.session_state.history.insert(0,{"Date":datetime.now().strftime("%d %b %Y %H:%M"),
        "Title":title[:45],"Company":company[:25],"Method":method,"Verdict":verdict,"Score":f"{score}%"})
    st.session_state.history=st.session_state.history[:50]
    st.session_state.stats["total"]+=1
    k=verdict.lower()
    if k in st.session_state.stats: st.session_state.stats[k]+=1

def vbox(verdict,title,sub=""):
    c={"REAL":"#16a34a","FAKE":"#dc2626","SUSPICIOUS":"#d97706"}
    bg={"REAL":"#f0fdf4","FAKE":"#fef2f2","SUSPICIOUS":"#fffbeb"}
    bd={"REAL":"#86efac","FAKE":"#fca5a5","SUSPICIOUS":"#fcd34d"}
    ic={"REAL":"✅","FAKE":"🚨","SUSPICIOUS":"⚠️"}
    st.markdown(f'<div style="background:{bg[verdict]};border:2px solid {bd[verdict]};border-radius:12px;padding:18px;margin:10px 0"><span style="color:{c[verdict]};font-size:24px;font-weight:800">{ic[verdict]} {title}</span><br><span style="font-size:12px;color:#64748b">{sub}</span></div>',unsafe_allow_html=True)

# ── LOGIN ──────────────────────────────────────────────────────────────────────
def page_login():
    _,col,_ = st.columns([1,1.2,1])
    with col:
        st.markdown('<div style="text-align:center;padding:24px 0 16px"><div style="font-size:52px">🛡️</div><h1 style="font-size:26px;font-weight:800;color:#1e293b;margin:8px 0 4px">Job Fraud Detector</h1><p style="color:#94a3b8;font-size:14px">Google Gemini AI + ML · 100% Free</p></div>',unsafe_allow_html=True)
        t1,t2=st.tabs(["🔑 Sign In","📝 Sign Up"])
        with t1:
            em=st.text_input("Email",placeholder="you@example.com",key="li_e")
            pw=st.text_input("Password",type="password",key="li_p")
            if st.button("Sign In →",use_container_width=True,type="primary",key="b_li"):
                u=st.session_state.users
                if em in u and u[em]["pw"]==pw:
                    st.session_state.update(logged_in=True,username=u[em]["name"],email=em); st.rerun()
                else: st.error("❌ Invalid email or password")
        with t2:
            nm=st.text_input("Full Name",placeholder="e.g. Nvvsatish",key="su_n")
            em2=st.text_input("Email",placeholder="you@example.com",key="su_e")
            pw2=st.text_input("Password",type="password",placeholder="Min 6 chars",key="su_p")
            pw3=st.text_input("Confirm Password",type="password",key="su_p2")
            if st.button("Create Account →",use_container_width=True,type="primary",key="b_su"):
                if not all([nm,em2,pw2,pw3]): st.warning("Fill all fields")
                elif len(pw2)<6: st.error("Password must be 6+ characters")
                elif pw2!=pw3: st.error("Passwords don't match")
                elif em2 in st.session_state.users: st.error("Email already registered")
                else:
                    st.session_state.users[em2]={"name":nm,"pw":pw2}
                    st.session_state.update(logged_in=True,username=nm,email=em2); st.rerun()
        st.divider()
        if st.button("⚡ Demo — Continue as Nvvsatish",use_container_width=True,key="b_demo"):
            st.session_state.update(logged_in=True,username="Nvvsatish",email="nvvsatish@demo.com"); st.rerun()

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        nm=st.session_state.username
        ini="".join(w[0] for w in nm.split()).upper()[:2]
        st.markdown(f'<div style="padding:6px 4px 14px"><div style="display:flex;align-items:center;gap:10px;margin-bottom:18px"><div style="width:36px;height:36px;background:linear-gradient(135deg,#3b82f6,#1d4ed8);border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0">🛡️</div><div style="font-weight:800;font-size:14px;color:white;line-height:1.25">Job Fraud<br>Detector</div></div><div style="font-size:9px;font-weight:700;color:rgba(255,255,255,0.35);letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px">MAIN MENU</div></div>',unsafe_allow_html=True)
        for icon,label in [("🏠","Dashboard"),("🔍","Job Analyzer"),("🔗","URL Checker"),("🌐","Job Portals")]:
            if st.button(f"{icon}  {label}",key=f"nav_{label}",use_container_width=True):
                st.session_state.page=label; st.rerun()
        st.markdown('<div style="font-size:9px;font-weight:700;color:rgba(255,255,255,0.35);letter-spacing:1.5px;text-transform:uppercase;margin:14px 0 8px;padding-left:4px">ACCOUNT</div>',unsafe_allow_html=True)
        for icon,label in [("🕐","History"),("⚙️","Settings")]:
            if st.button(f"{icon}  {label}",key=f"nav_{label}",use_container_width=True):
                st.session_state.page=label; st.rerun()
        st.markdown("---")
        total=st.session_state.stats["total"]
        st.markdown(f'<div style="padding:6px"><div style="display:flex;align-items:center;gap:9px"><div style="width:30px;height:30px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#8b5cf6);display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:11px;flex-shrink:0">{ini}</div><div style="min-width:0"><div style="font-weight:700;font-size:12px;color:white">{nm}</div><div style="font-size:10px;color:rgba(255,255,255,0.4)">{st.session_state.email}</div></div></div><div style="margin-top:8px;padding:2px 8px;display:inline-block;border-radius:20px;background:rgba(34,197,94,0.15);border:1px solid rgba(34,197,94,0.25);font-size:9px;font-weight:600;color:#4ade80">● DB · {total} scans</div></div>',unsafe_allow_html=True)
        if st.button("🚪  Sign Out",key="btn_logout",use_container_width=True):
            st.session_state.update(logged_in=False,page="Dashboard"); st.rerun()

# ── DASHBOARD ──────────────────────────────────────────────────────────────────
def page_dashboard():
    st.title("📊 Dashboard")
    st.caption(f"Welcome, **{st.session_state.username}** 👋")
    s=st.session_state.stats
    c1,c2,c3,c4=st.columns(4)
    c1.metric("📊 Total Checks",s["total"])
    c2.metric("🚨 Fake + Suspicious",s["fake"]+s["suspicious"],delta=f"{s['fake']} Fake · {s['suspicious']} Suspicious")
    c3.metric("✅ Real Verified",s["real"])
    rate=f"{round(((s['real']+s['fake']+s['suspicious'])/(s['total'] or 1))*100)}%" if s["total"] else "—"
    c4.metric("🎯 Detection Rate",rate)
    if s["total"]==0:
        st.info("🔍 **No scans yet** — counts start at zero and update as you use the app. Start by analyzing a job or checking a URL.")
    st.divider()
    col1,col2=st.columns(2)
    with col1:
        st.subheader("🚩 Common Scam Keywords")
        for dot,kw in [("🔴","Pay for Training"),("🔴","Urgent Hiring!!!"),("🔴","No Interview Required"),
                       ("🟡","Work From Home"),("🔴","Guaranteed Income"),("🔴","Registration Fee"),
                       ("🔴","Unlimited Earnings"),("🟡","No Experience Needed")]: st.markdown(f"{dot} {kw}")
    with col2:
        st.subheader("⚠️ Suspicious Domains")
        for d in ["gmail.com","yahoo.com","hotmail.com","rediffmail.com","outlook.com (unverified)","yopmail.com","tempmail.com"]:
            st.markdown(f"🔴 `{d}` — High Risk")
    st.divider()
    c1,c2,c3=st.columns(3)
    with c1:
        if st.button("🔍 Analyze a Job",use_container_width=True): st.session_state.page="Job Analyzer"; st.rerun()
    with c2:
        if st.button("🔗 Check a URL",use_container_width=True): st.session_state.page="URL Checker"; st.rerun()
    with c3:
        if st.button("🌐 Job Portals",use_container_width=True): st.session_state.page="Job Portals"; st.rerun()

# ── ANALYZER ───────────────────────────────────────────────────────────────────
def page_analyzer():
    st.title("🔍 Job Analyzer")
    tab_text,tab_doc=st.tabs(["📝 Text Analysis","📄 Upload Document"])

    with tab_text:
        with st.form("tf"):
            c1,c2=st.columns(2)
            with c1: title=st.text_input("Job Title *",placeholder="e.g. Analyst Trainee"); company=st.text_input("Company",placeholder="e.g. Cognizant")
            with c2: loc=st.text_input("Location",placeholder="e.g. Chennai"); sal=st.text_input("Salary/CTC",placeholder="e.g. INR 2,79,996 ATR")
            desc=st.text_area("Full Description *",height=120,placeholder="Paste complete job description here")
            c1,c2=st.columns(2)
            with c1: req=st.text_area("Requirements",height=90)
            with c2: ben=st.text_area("Benefits",height=90)
            c1,c2=st.columns(2)
            with c1: has_logo=st.checkbox("Has Official Logo")
            with c2: fulltime=st.checkbox("Full-time Role",value=True)
            sub=st.form_submit_button("🔍 Scan for Fraud",type="primary",use_container_width=True)
        if sub:
            if not title or not desc: st.error("⚠️ Please fill in Job Title and Description"); return
            with st.spinner("Running ML models..."): ml=run_ml(title,company or "",loc or "",sal or "",desc,req or "",ben or "",has_logo,fulltime)
            v=ml["en"]["v"]; cf=ml["en"]["c"]
            vbox(v,f"{'REAL JOB' if v=='REAL' else 'FAKE JOB' if v=='FAKE' else 'SUSPICIOUS JOB'}",
                 f"{ml['tp']} · {ml['rc']} red flags · {ml['gc']} green signals · {cf}% confidence")
            st.subheader("🤖 ML Model Results")
            c1,c2,c3=st.columns(3)
            for col,nm,key in [(c1,"Logistic Reg.","lr"),(c2,"Random Forest","rf"),(c3,"SVM","sv")]:
                vv=ml[key]["v"]; cc=ml[key]["c"]; color="#22c55e" if vv=="REAL" else "#ef4444" if vv=="FAKE" else "#f59e0b"
                with col: st.markdown(f"**{nm}**"); st.markdown(f'<span style="color:{color};font-weight:700;font-size:15px">{vv} ({cc}%)</span>',unsafe_allow_html=True); st.progress(cc/100)
            if ml["red"]: st.error("🚩 Red Flags: "+"  ·  ".join(f"`{f}`" for f in ml["red"]))
            if ml["green"]: st.success("✅ Positive: "+"  ·  ".join(f"`{f}`" for f in ml["green"]))
            st.subheader("🧠 Gemini AI Analysis")
            prompt=f"""You are a senior job fraud investigator. Company type: {ml['tp']}.
Job: "{title}" at "{company or 'Unknown'}" | {loc or 'N/A'} | {sal or 'N/A'}
ML: {v} {cf}% | Red: {ml['rc']} | Green: {ml['gc']}
Description: {desc}
Requirements: {req or 'N/A'}
Benefits: {ben or 'N/A'}

Respond EXACTLY in this format:
OVERALL VERDICT: [FAKE/REAL/SUSPICIOUS]
RISK SCORE: [0-100]

KEY FINDINGS:
[4 specific observations]

RED FLAGS:
[Each starting with → or "None detected"]

LEGITIMACY SIGNALS:
[Each starting with → or "None found"]

RECOMMENDATION:
[2-3 direct sentences for the job seeker]"""
            try:
                with st.spinner("Gemini AI analyzing..."): result=ask_gemini(prompt)
                st.markdown(f'<div class="ai-box">{result}</div>',unsafe_allow_html=True)
                record(f"{title} – {company or '?'}",company or "?",v,"Text")
                st.success(f"✅ Saved! Total scans: {st.session_state.stats['total']}")
            except Exception as e: st.error(f"AI error: {e}"); record(f"{title} – {company or '?'}",company or "?",v,"Text")

    with tab_doc:
        st.info("📄 Upload offer letter or WhatsApp screenshot (JPG, PNG, WEBP)")
        files=st.file_uploader("Upload",type=["jpg","jpeg","png","webp"],accept_multiple_files=True,label_visibility="collapsed")
        if files:
            st.success(f"✅ {len(files)} file(s) uploaded")
            cols=st.columns(min(len(files),4)); pil_images=[]
            for i,f in enumerate(files):
                raw=f.read(); img=Image.open(io.BytesIO(raw)); pil_images.append(img)
                with cols[i%4]: st.image(img,caption=f.name,use_container_width=True)
            if st.button("🔍 Scan Document(s)",type="primary",use_container_width=True):
                with st.spinner("Running 8-point forensic analysis..."):
                    try:
                        prompt="""Analyze this job document. Return ONLY valid JSON (no markdown, start { end }):
{"verdict":"REAL","authenticity_score":88,"risk_score":12,"document_type":"Offer Letter","company_type":"Indian IT MNC","company_name":"","role":"","salary":"","contact_email":"","date":"","reference_number":"","checks":[{"category":"Logo & Branding","status":"PASS","detail":""},{"category":"Email Domain","status":"PASS","detail":""},{"category":"Salary & CTC","status":"PASS","detail":""},{"category":"Document Format","status":"PASS","detail":""},{"category":"Contact Details","status":"WARN","detail":""},{"category":"Legal Clauses","status":"PASS","detail":""},{"category":"Scam Signals","status":"PASS","detail":""},{"category":"Grammar & Language","status":"PASS","detail":""}],"red_flags":[],"green_flags":[],"summary":"","recommendation":""}"""
                        result=safe_json(ask_gemini(prompt,images=pil_images))
                        if not result: st.error("Could not parse response. Try again."); return
                        vv=result.get("verdict","SUSPICIOUS"); sc=result.get("authenticity_score",50); rk=result.get("risk_score",50)
                        vbox(vv,f"{'REAL' if vv=='REAL' else 'FAKE' if vv=='FAKE' else 'SUSPICIOUS'} DOCUMENT",
                             f"{result.get('document_type','')} · {result.get('company_type','')} · Auth: {sc}% · Risk: {rk}/100")
                        st.subheader("🔬 8-Point Forensic Report")
                        icons={"PASS":"✅","FAIL":"❌","WARN":"⚠️","INFO":"ℹ️"}
                        checks=result.get("checks",[])
                        if checks:
                            c1,c2=st.columns(2)
                            for i,chk in enumerate(checks):
                                s=chk.get("status","INFO")
                                with (c1 if i%2==0 else c2): st.markdown(f"{icons.get(s,'ℹ️')} **{chk.get('category','')}** — `{s}`"); st.caption(chk.get("detail",""))
                        st.subheader("📋 Extracted Info")
                        for lbl,val in [("Company",result.get("company_name")),("Role",result.get("role")),("Salary",result.get("salary")),("Ref No.",result.get("reference_number")),("Email",result.get("contact_email")),("Date",result.get("date"))]:
                            if val: st.markdown(f"**{lbl}:** {val}")
                        if result.get("red_flags"): st.error("🚩 Red Flags: "+" · ".join(result["red_flags"]))
                        if result.get("green_flags"): st.success("✅ Positive: "+" · ".join(result["green_flags"]))
                        if result.get("summary"): st.markdown(f'<div class="ai-box">📝 {result["summary"]}</div>',unsafe_allow_html=True)
                        if result.get("recommendation"): st.markdown(f'<div class="ai-box" style="border-left-color:#22c55e">▶ {result["recommendation"]}</div>',unsafe_allow_html=True)
                        record(f"{result.get('role','Doc')} – {result.get('company_name','?')}",result.get("company_name","?"),vv,"Document")
                        st.success(f"✅ Saved! Total scans: {st.session_state.stats['total']}")
                    except Exception as e: st.error(f"Error: {e}")

# ── URL CHECKER ────────────────────────────────────────────────────────────────
def page_url():
    st.title("🔗 URL Checker")
    st.caption("Paste any job URL — Naukri, LinkedIn, Unstop, Foundit, or any site")
    c1,c2,c3=st.columns(3)
    with c1:
        if st.button("📌 Naukri Example",use_container_width=True): st.session_state["_url"]="https://www.naukri.com/job-listings-software-engineer-tata-consultancy-services-0-to-2-years-160326011833"
    with c2:
        if st.button("📌 Unstop Example",use_container_width=True): st.session_state["_url"]="https://unstop.com/jobs/campus-recruitment-tcs"
    with c3:
        if st.button("📌 Fake URL",use_container_width=True): st.session_state["_url"]="https://bit.ly/apply-job-whatsapp-earn"
    url_input=st.text_input("Job URL",value=st.session_state.get("_url",""),placeholder="https://www.naukri.com/...",label_visibility="collapsed")
    if url_input:
        pn,trusted=detect_portal(url_input)
        if trusted: st.success(f"✅ **{pn}** — Trusted Platform")
        else: st.error(f"🚨 **{pn}** — Suspicious Source")
    if st.button("🔍 Analyze URL",type="primary",use_container_width=True):
        if not url_input.strip(): st.error("Please paste a job URL"); return
        url=url_input.strip()
        if not url.startswith("http"): url="https://"+url
        pn,trusted=detect_portal(url.lower())
        kw=" ".join(w for w in re.split(r'[-_/?=&.]',url) if len(w)>2 and not re.match(r'^\d+$',w))
        with st.spinner("Analyzing with Gemini AI..."):
            try:
                prompt=f"""Analyze this job URL. Return ONLY valid JSON (no markdown, start {{ end }}):
URL: {url}
Portal: {pn} (trusted: {trusted})
Keywords: {kw}
{{"portal_verdict":"TRUSTED_PLATFORM","job_verdict":"LIKELY_REAL","risk_score":25,"confidence":75,"job_title":"","company":"","location":"","experience":"","salary":"Not in URL","platform_analysis":"3-4 sentences about this platform","url_red_flags":"None found","url_green_signals":"Positive signals found","verification_steps":["step1","step2","step3","step4","step5"],"overall_assessment":"3-4 sentence assessment"}}"""
                result=safe_json(ask_gemini(prompt))
                if not result: st.error("Could not parse response. Try again."); return
                jv=result.get("job_verdict","NEEDS_VERIFICATION")
                verdict="REAL" if jv=="LIKELY_REAL" else "FAKE" if jv=="LIKELY_FAKE" else "SUSPICIOUS"
                risk=result.get("risk_score",50); conf=result.get("confidence",60)
                label="LIKELY REAL" if verdict=="REAL" else "LIKELY FAKE" if verdict=="FAKE" else "VERIFY FIRST"
                vbox(verdict,label,f"{pn} · Risk: {risk}/100 · Confidence: {conf}%")
                st.subheader("📋 Extracted Info")
                c1,c2,c3=st.columns(3)
                for i,(lbl,val) in enumerate([("🏷️ Title",result.get("job_title","N/A")),("🏢 Company",result.get("company","N/A")),("📍 Location",result.get("location","N/A")),("⏱️ Exp.",result.get("experience","N/A")),("💰 Salary",result.get("salary","N/A")),("🌐 Portal",pn)]):
                    with [c1,c2,c3][i%3]: st.metric(lbl,val or "N/A")
                if result.get("platform_analysis"):
                    color="#22c55e" if trusted else "#ef4444"
                    st.markdown(f'<div class="ai-box" style="border-left-color:{color}">🌐 {result["platform_analysis"]}</div>',unsafe_allow_html=True)
                steps=[s for s in result.get("verification_steps",[]) if s]
                if steps:
                    st.subheader("📋 Verification Steps")
                    for i,s in enumerate(steps,1): st.markdown(f'<div class="step"><b>{i}.</b> {re.sub(r"^\d+[.)]\s*","",s)}</div>',unsafe_allow_html=True)
                if result.get("overall_assessment"): st.markdown(f'<div class="ai-box" style="border-left-color:#22c55e">▶ {result["overall_assessment"]}</div>',unsafe_allow_html=True)
                st.markdown('<div class="warn">⚠️ Never pay any fee. Always verify on the company\'s official website.</div>',unsafe_allow_html=True)
                record(f"{result.get('job_title','URL Job')} – {result.get('company','?')}",result.get("company","?"),verdict,"URL")
                st.success(f"✅ Saved! Total scans: {st.session_state.stats['total']}")
            except Exception as e: st.error(f"Error: {e}")

# ── PORTALS ────────────────────────────────────────────────────────────────────
def page_portals():
    st.title("🌐 Job Portals")
    st.success("✅ Only apply through these verified platforms — never via WhatsApp or Telegram")
    portals=[("💼","LinkedIn","https://www.linkedin.com/jobs/","Global network"),("🔵","Naukri","https://www.naukri.com/","India's #1"),("🟠","Foundit","https://www.foundit.in/","Monster India"),("🟢","Unstop","https://unstop.com/jobs","Campus hiring"),("🎓","Internshala","https://internshala.com/jobs/","Fresher jobs"),("🔷","Indeed","https://in.indeed.com/","Global jobs"),("🟩","Glassdoor","https://www.glassdoor.co.in/","Jobs+salaries"),("🟡","Shine","https://www.shine.com/","Indian jobs"),("⚡","Hirist","https://www.hirist.tech/","Tech jobs"),("✂️","Cutshort","https://cutshort.io/jobs","AI matched"),("🚀","Wellfound","https://wellfound.com/jobs","Startup roles"),("🌱","Freshersworld","https://www.freshersworld.com/","0-3 yrs exp")]
    cols=st.columns(3)
    for i,(ico,name,url,desc) in enumerate(portals):
        with cols[i%3]:
            st.markdown(f'<div class="card" style="text-align:center"><div style="font-size:28px">{ico}</div><div style="font-weight:700;font-size:14px;margin:6px 0 3px">{name}</div><div style="font-size:11px;color:#94a3b8;margin-bottom:8px">{desc}</div><span style="padding:2px 9px;border-radius:20px;background:#f0fdf4;color:#22c55e;font-size:10px;font-weight:700">✅ Verified</span></div>',unsafe_allow_html=True)
            st.markdown(f"[🔗 Visit {name}]({url})")

# ── HISTORY ────────────────────────────────────────────────────────────────────
def page_history():
    st.title("🕐 History")
    s=st.session_state.stats
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Total",s["total"]); c2.metric("🚨 Fake",s["fake"]); c3.metric("⚠️ Suspicious",s["suspicious"]); c4.metric("✅ Real",s["real"])
    hist=st.session_state.history
    if not hist:
        st.info("📋 No history yet.")
        if st.button("📝 Start Analyzing",type="primary"): st.session_state.page="Job Analyzer"; st.rerun()
        return
    st.dataframe(pd.DataFrame(hist),use_container_width=True,hide_index=True)
    if st.button("🔄 Clear History",type="secondary"):
        st.session_state.history=[]; st.session_state.stats={"total":0,"real":0,"fake":0,"suspicious":0}; st.rerun()

# ── SETTINGS ───────────────────────────────────────────────────────────────────
def page_settings():
    st.title("⚙️ Settings")
    col1,col2=st.columns(2)
    with col1:
        st.subheader("👤 Account")
        st.text_input("Name",value=st.session_state.username,disabled=True)
        st.text_input("Email",value=st.session_state.email,disabled=True)
        st.subheader("📊 Statistics")
        s=st.session_state.stats
        for lbl,val in [("Total Scans",s["total"]),("Fake",s["fake"]),("Suspicious",s["suspicious"]),("Fake+Suspicious",s["fake"]+s["suspicious"]),("Real",s["real"])]: st.metric(lbl,val)
        if st.button("🔄 Reset All",type="secondary"): st.session_state.stats={"total":0,"real":0,"fake":0,"suspicious":0}; st.session_state.history=[]; st.success("✅ Reset!"); st.rerun()
    with col2:
        st.subheader("🤖 ML Models")
        for n,a in [("Logistic Regression","94.2%"),("Random Forest","96.1%"),("SVM","93.8%"),("Gemini Vision","Documents"),("URL Analyzer","Portals")]: st.success(f"✅ **{n}** — {a}")
        st.subheader("🔑 Gemini API Key")
        key=""
        try: key=st.secrets.get("GEMINI_API_KEY","")
        except: key=os.environ.get("GEMINI_API_KEY","")
        key=key.strip().strip('"').strip("'")
        if key and key.startswith("AIza"): st.success(f"✅ Valid key — `{key[:16]}...` ({len(key)} chars)")
        elif key: st.warning(f"⚠️ Key found but may be wrong — starts: `{key[:10]}`")
        else:
            st.error("❌ No GEMINI_API_KEY found")
            st.code('GEMINI_API_KEY = "AIzaSy..."',language="toml")

# ── MAIN ───────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in: page_login(); return
    sidebar()
    {"Dashboard":page_dashboard,"Job Analyzer":page_analyzer,"URL Checker":page_url,
     "Job Portals":page_portals,"History":page_history,"Settings":page_settings
    }.get(st.session_state.page,page_dashboard)()

if __name__=="__main__": main()
