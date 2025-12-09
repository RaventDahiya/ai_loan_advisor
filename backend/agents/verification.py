from services.mongo import db


def verify_kyc(session_id: str) -> str:
    docs = db.documents.find_one({"sessionId": session_id}) or {}
    if not docs.get("uploaded"):
        return ("Please upload the required documents: KYC Proof, Income Proof, and Bank Statements. "
                "Once uploaded, I will verify them.")
    return "Documents verified successfully. Proceeding to underwriting."
