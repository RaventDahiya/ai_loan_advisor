# 🏦 AI Loan Advisor – Agentic AI for Digital Lending

A full-stack loan application system using multi-agent AI architecture to automate the loan approval process.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      MASTER AGENT                           │
│              (Conversation Controller)                      │
└─────────────────┬───────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┬─────────────┬───────────────┐
    ▼             ▼             ▼             ▼               │
┌────────┐  ┌──────────┐  ┌────────────┐  ┌──────────┐        │
│ SALES  │  │VERIFICATION│ │UNDERWRITING│  │ SANCTION │       │
│ AGENT  │  │  AGENT    │  │   AGENT    │  │  AGENT   │       │
└────────┘  └──────────┘  └────────────┘  └──────────┘        │
     │            │              │              │              │
  Collect      KYC Check     ML Credit      Generate          │
  Details      via CRM       Scoring        PDF Letter        │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

Before running this application, ensure you have:

| Requirement | Version | Download |
|-------------|---------|----------|
| Python | 3.10+ | [python.org](https://python.org) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| MongoDB | Atlas (cloud) or Local | [mongodb.com](https://mongodb.com) |

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/RaventDahiya/ai-loan-advisor.git
cd ai-loan-advisor/ai_loan_advisor
```

### 2. Setup Backend

**Windows (PowerShell):**
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create `backend/.env` file:
```env
# MongoDB Connection (choose one)
# Option A: MongoDB Atlas (cloud - recommended)
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/

# Option B: Local MongoDB
# MONGO_URI=mongodb://localhost:27017

# OpenAI API Key (optional - for LLM responses)
OPENAI_API_KEY=your_openai_api_key_here
```

**To get MongoDB Atlas (Free):**
1. Go to [mongodb.com/atlas](https://mongodb.com/atlas)
2. Create free account → Create cluster
3. Get connection string → Replace `<username>` and `<password>`

### 4. Run Backend
```bash
# Make sure you're in backend/ folder with venv activated
python app.py
```
Backend runs at: **http://localhost:5000**

### 5. Setup & Run Frontend

**Open a new terminal:**

**Windows (PowerShell):**
```powershell
cd frontend
npm install
npm run dev
```

**Mac/Linux:**
```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: **http://localhost:5173**

## 🎯 How to Use

1. **Open** http://localhost:5173 in your browser
2. **Fill the loan form** with:
   - Loan Amount (e.g., 500000)
   - Tenure in months (e.g., 24)
   - Monthly Income (e.g., 80000)
   - Purpose (e.g., Home Renovation)
3. **Submit** the form → Sales Agent saves your data
4. **Chat** with the AI → Verification Agent asks for documents
5. **Upload** KYC documents (any file for demo)
6. **Continue chatting** → Underwriting Agent evaluates:
   - ✅ **Approved** → Download sanction letter PDF
   - 📋 **Need More Docs** → Upload salary slip
   - ❌ **Rejected** → See rejection reason
7. **Download** your sanction letter if approved!

## 📁 Project Structure

```
ai_loan_advisor/
├── backend/
│   ├── app.py              # Flask API server
│   ├── requirements.txt    # Python dependencies
│   ├── .env                # Environment variables (create this)
│   ├── agents/             # AI Agent logic
│   │   ├── orchestrator.py # Master agent routing
│   │   ├── sales.py        # Sales agent
│   │   ├── verification.py # KYC verification agent
│   │   └── underwriting.py # Credit scoring agent
│   ├── services/
│   │   ├── mongo.py        # Database connection
│   │   └── pdf_service.py  # PDF generation
│   └── ml/
│       └── train_model.py  # ML model training
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   ├── components/
│   │   │   ├── Chat.jsx    # AI chat interface
│   │   │   ├── LoanForm.jsx
│   │   │   ├── DocumentUpload.jsx
│   │   │   └── DecisionPanel.jsx
│   │   └── api/
│   │       └── client.js   # API calls
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/apply` | Submit loan application |
| POST | `/api/chat` | Chat with AI advisor |
| POST | `/api/upload` | Upload KYC documents |
| GET | `/api/status/<session_id>` | Get application status |
| GET | `/api/download/<pdf_id>` | Download sanction letter |
| GET | `/api/health` | Health check |

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| `python not found` | Add Python to PATH or use `python3` |
| `npm not found` | Install Node.js and restart terminal |
| `MongoDB connection failed` | Check your `MONGO_URI` in `.env` |
| `CORS error in browser` | Ensure backend is running on port 5000 |
| `Port already in use` | Kill existing process or use different port |

## 📄 License

MIT License - Feel free to use and modify!

## 👤 Author

**Ravent Dahiya** - [GitHub](https://github.com/RaventDahiya)
