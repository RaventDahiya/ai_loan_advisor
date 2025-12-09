# AI Loan Advisor – Redefining Digital Lending with Agentic AI

## Run locally (Windows PowerShell)
- Backend:
  - Create venv, activate, install deps, train model, run server

```powershell
python -m venv "backend/.venv"
"backend/.venv/Scripts/Activate.ps1"
pip install -r backend/requirements.txt
Copy-Item backend/.env.example backend/.env
python backend/ml/train_model.py
python backend/app.py
```

- Frontend:
```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

## Notes
- Ensure MongoDB is running locally on `mongodb://localhost:27017`.
- Set `OPENAI_API_KEY` in `backend/.env` if using an LLM.
- The sanction PDFs are written into `backend/ml` for simplicity.
