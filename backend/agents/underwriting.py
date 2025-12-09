import joblib
import os
from services.mongo import db

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml", "model.pkl")

try:
    _model = joblib.load(MODEL_PATH)
except Exception:
    _model = None


def score_and_decide(session_id: str, inputs: dict):
    # inputs expected: income, loan_amount, tenure
    income = float(inputs.get("income", 0))
    loan_amount = float(inputs.get("loan_amount", 0))
    tenure = float(inputs.get("tenure", 12))

    if _model is None:
        # Fallback rule
        emi = loan_amount / max(tenure, 1)
        approved = emi < 0.4 * income
        return {
            "approved": bool(approved),
            "confidence": 0.5,
            "reason": "Fallback rule used",
            "amount": loan_amount if approved else 0,
            "emi": round(emi, 2),
            "tenure": int(tenure),
        }

    X = [[income, loan_amount, tenure]]
    prob = float(_model.predict_proba(X)[0][1])
    approved = prob >= 0.5

    decision = {
        "approved": bool(approved),
        "confidence": prob,
        "reason": "Model-based underwriting",
        "amount": loan_amount if approved else 0,
        "emi": round(loan_amount / max(tenure, 1), 2),
        "tenure": int(tenure),
    }

    db.decisions.update_one({"sessionId": session_id}, {"$set": decision}, upsert=True)
    return decision
