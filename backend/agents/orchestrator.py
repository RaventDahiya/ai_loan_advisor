from services.mongo import db


def route_next(session_id: str, message: str) -> str:
    app_doc = db.applications.find_one({"sessionId": session_id}) or {}
    status = app_doc.get("status", "start")
    docs = db.documents.find_one({"sessionId": session_id}) or {}
    has_docs = docs.get("uploaded", False)
    has_loan_data = app_doc.get("loan_amount") is not None

    if status == "start":
        db.applications.update_one(
            {"sessionId": session_id},
            {"$set": {"status": "sales"}},
            upsert=True,
        )
        return "sales"
    elif status == "sales":
        if has_loan_data:
            db.applications.update_one({"sessionId": session_id}, {"$set": {"status": "verification"}})
            return "verification"
        return "sales"
    elif status == "verification":
        if has_docs:
            db.applications.update_one({"sessionId": session_id}, {"$set": {"status": "underwriting"}})
            return "underwriting"
        return "verification"
    elif status == "underwriting":
        db.applications.update_one({"sessionId": session_id}, {"$set": {"status": "sanction"}})
        return "sanction"
    elif status == "sanction":
        db.applications.update_one({"sessionId": session_id}, {"$set": {"status": "end"}})
        return "end"
    else:
        return "end"
