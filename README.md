# 🛡️ Job Fraud Detector — Streamlit App
Built by Nvvsatish | Powered by Claude AI + ML

## 🚀 Deploy on Streamlit Cloud (FREE)

### Step 1 — Create GitHub repo
1. Go to github.com → New repository
2. Name: `fakejob-detector`  
3. Public → NO README → Create repository

### Step 2 — Push code
Open terminal inside this folder and run:
```
git init
git add .
git commit -m "Job Fraud Detector"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/fakejob-detector.git
git push -u origin main
```

### Step 3 — Deploy on Streamlit Cloud
1. Go to share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Repository: fakejob-detector
5. Branch: main
6. Main file: app.py
7. Click "Deploy"

### Step 4 — Add API Key
1. App Settings (⋮) → Edit Secrets
2. Add this line:
```
ANTHROPIC_API_KEY = "sk-ant-api03-your-key-here"
```
3. Save → app restarts → WORKS ✅

## 💻 Run Locally
```
pip install -r requirements.txt
streamlit run app.py
```

## 🔑 Get API Key
1. console.anthropic.com → Sign up
2. API Keys → Create Key
3. Copy it (starts with sk-ant-)
