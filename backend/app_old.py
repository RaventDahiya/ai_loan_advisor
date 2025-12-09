import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
from services.mongo import db
from services.pdf_service import generate_sanction_letter
from agents.orchestrator import route_next
from agents.sales import collect_requirements
from agents.verification import verify_kyc
from agents.underwriting import score_and_decide

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route("/api/apply", methods=["POST"])
def apply():
    data = request.get_json() or {}
    session_id = data.get("sessionId")
    if not session_id:
        return jsonify({"error": "missing sessionId"}), 400
    fields = {k: data.get(k) for k in [
        "loan_amount", "tenure", "purpose", "income", "employment", "age"
    ]}
    db.applications.update_one({"sessionId": session_id}, {"$set": fields, "$setOnInsert": {"status": "sales"}}, upsert=True)
    return jsonify({"ok": True})


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json() or {}
    session_id = data.get("sessionId")
    message = data.get("message", "")
    if not session_id:
        return jsonify({"error": "missing sessionId"}), 400

    step = route_next(session_id, message)

    if step == "sales":
        reply = collect_requirements(session_id, message)
    elif step == "verification":
        reply = verify_kyc(session_id)
    elif step == "underwriting":
        # gather basic inputs from last stored application record
        app_doc = db.applications.find_one({"sessionId": session_id}) or {}
        inputs = {
            "income": app_doc.get("income", 50000),
            "loan_amount": app_doc.get("loan_amount", 200000),
            "tenure": app_doc.get("tenure", 12),
        }
        decision = score_and_decide(session_id, inputs)
        db.applications.update_one({"sessionId": session_id}, {"$set": {"status": "underwriting"}}, upsert=True)
        reply = f"Underwriting result: {'Approved' if decision['approved'] else 'Rejected'} (confidence: {round(decision['confidence']*100,1)}%)."
    elif step == "sanction":
        decision = db.decisions.find_one({"sessionId": session_id}) or {}
        pdf_id = generate_sanction_letter(session_id, decision)
        reply = f"Sanction letter generated. ID: {pdf_id}"
    else:
        reply = "Thank you! Conversation ended."

    return jsonify({"step": step, "reply": reply})


@app.route("/api/upload", methods=["POST"])
def upload():
    session_id = request.form.get("sessionId")
    file = request.files.get("file")
    if not session_id or not file:
        return jsonify({"error": "missing sessionId or file"}), 400

    # For demo, don't persist file, just mark uploaded
    db.documents.update_one({"sessionId": session_id}, {"$set": {"uploaded": True}}, upsert=True)
    return jsonify({"ok": True})


@app.route("/api/download/<pdf_id>", methods=["GET"])
def download(pdf_id: str):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(base_dir, "ml", f"{pdf_id}.pdf")
    if not os.path.exists(pdf_path):
        return jsonify({"error": "not found"}), 404
    return send_file(pdf_path, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
