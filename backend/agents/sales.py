from services.mongo import db


def collect_requirements(session_id: str, message: str) -> str:
    db.applications.update_one(
        {"sessionId": session_id},
        {"$setOnInsert": {"status": "sales"}, "$set": {"lastMessage": message}},
        upsert=True,
    )
    return "Please provide loan amount, tenure, purpose, monthly income, employment, and age (if available)."
