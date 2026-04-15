# 🏥 Ambulatory Empires — Healthcare AI Agent

> Intelligent healthcare navigation for the 2026 care ecosystem — built in Python with Google Gemini AI.

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green) ![Gemini](https://img.shields.io/badge/Gemini-1.5--flash-orange)

---

## 🌟 Overview

The **Ambulatory Empires Healthcare AI Agent** routes patients and families to the right care setting in a world where most care happens outside hospitals. It operates across three pillars:

| Pillar | Setting | Best For |
|--------|---------|----------|
| 🏥 **Outpatient Surge** | Ambulatory Surgery Centers | Joint replacements, cataracts, hernias, scopes |
| 🏠 **Hospital-at-Home** | Remote Patient Monitoring | Heart failure, diabetes, hypertension, COPD |
| 🏪 **Retail Health** | Pharmacy & employer clinics | Physicals, vaccines, minor acute care, refills |

---

## 🚀 Quick Start

### 1. Setup environment

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Add your Gemini API key

```bash
cp .env.example .env
# Edit .env and set: GOOGLE_API_KEY=your_key_here
# Get a free key at: https://aistudio.google.com/app/apikey
```

### 3. Run the agent

```bash
# Interactive CLI chat
python main.py chat

# Run demo (all 3 pillars)
python main.py demo

# Start REST API server
python main.py serve
```

---

## 📁 Project Structure

```
health ai agent/
├── agent/
│   ├── core.py          # 🧠 Main agent orchestrator (Gemini LLM)
│   ├── triage.py        # 🔀 Clinical triage engine (rule-based + LLM)
│   ├── memory.py        # 💾 Patient session & vitals memory
│   └── prompts.py       # 📝 System prompts & templates
├── modules/
│   ├── outpatient.py    # 🏥 ASC finder, pre/post-op protocols
│   ├── hospital_at_home.py  # 🏠 RPM, vitals analysis, trend detection
│   └── retail_health.py # 🏪 Clinic finder, screening schedules
├── api/
│   └── app.py           # 🌐 FastAPI REST server
├── ui/
│   └── dashboard.html   # 💻 Rich web dashboard (glassmorphic UI)
├── tests/
│   └── test_agent.py    # ✅ Unit tests (pytest)
├── config.py            # ⚙️ Configuration
├── main.py              # 🚪 CLI entry point
└── requirements.txt
```

---

## 🎯 Triage Logic

The engine uses a **two-stage triage** approach:

1. **Rule-based fast path** — keyword matching for speed and safety
2. **Gemini LLM fallback** — for ambiguous or complex presentations

```
Patient message
      │
      ▼
Emergency keywords? ──YES──► 🚨 EMERGENCY (call 911)
      │NO
      ▼
Surgical keywords?  ──YES──► 🏥 ASC (Ambulatory Surgery Center)
      │NO
      ▼
Monitoring keywords?──YES──► 🏠 HOME_MONITORING (RPM)
      │NO
      ▼
Retail keywords?    ──YES──► 🏪 RETAIL (pharmacy/employer clinic)
      │NO
      ▼
Gemini LLM triage ──────────► Classified response
```

---

## 🌐 REST API Endpoints

Start the server:
```bash
python main.py serve
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/welcome` | Start session, get welcome message |
| `POST` | `/chat` | Send message, get AI response + triage |
| `POST` | `/vitals` | Submit vitals for AI analysis |
| `POST` | `/triage` | Classify a message (no reply) |
| `POST` | `/clinics/retail` | Find retail health clinics |
| `POST` | `/clinics/asc` | Find Ambulatory Surgery Centers |
| `GET`  | `/rpm/guide/{condition}` | Get RPM device setup guide |
| `GET`  | `/screenings` | Get preventive screening schedule |
| `GET`  | `/preop/{procedure}` | Pre/post-op checklists |

---

## 💻 Web Dashboard

Open the dashboard in your browser (API must be running):

```bash
open ui/dashboard.html     # macOS
# Or just open the file in Chrome/Safari/Firefox
```

Features:
- 📊 **Dashboard** — Key stats, pillar overview, quick-access cards
- 💬 **AI Chat** — Real-time conversation with triage badges
- ❤️ **Vitals Monitor** — Input readings, get AI analysis, track trends on chart

---

## ✅ Running Tests

```bash
# Run all tests (no API key needed)
python -m pytest tests/ -v

# Run specific test group
python -m pytest tests/ -v -k "triage"
python -m pytest tests/ -v -k "vitals"
```

---

## 🔑 Key Statistics Referenced

- **40%** reduction in hospital-acquired infections with outpatient model
- **85%** of patients prefer retail clinics for non-emergency care  
- **30%** reduction in hospital readmissions via Remote Patient Monitoring
- **50%** cost savings — ASC procedures vs hospital-based
- **48 hours** early warning — wearables detect trends before symptoms

---

## ⚠️ Disclaimer

This agent is a **navigator and educational tool** — it does not:
- Provide medical diagnoses
- Replace licensed healthcare providers
- Make treatment decisions

Always consult a qualified healthcare professional for medical advice.

---

## 📄 License

MIT License — built for the 2026 healthcare ecosystem.
