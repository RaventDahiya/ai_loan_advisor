"""
AI Loan Advisor - Multi-Agent Backend
Master Agent orchestrates: Sales → Verification → Underwriting → Sanction
"""
import os
import sys
import uuid
import traceback
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ============ IN-MEMORY STORAGE (MongoDB fallback) ============
class InMemoryDB:
    def __init__(self):
        self.applications = {}  # sessionId -> {status, loan_amount, tenure, income, ...}
        self.documents = {}     # sessionId -> {uploaded: bool, filename: str}
        self.decisions = {}     # sessionId -> {approved, confidence, reason, ...}
        self.sanctions = {}     # sessionId -> {pdfId, ...}

db = InMemoryDB()

# Try MongoDB Atlas connection
MONGO_URI = os.getenv("MONGO_URI", "")
mongo_db = None
if MONGO_URI:
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        mongo_db = client.ai_loan_advisor
        print("✓ Connected to MongoDB Atlas")
    except Exception as e:
        print(f"⚠ MongoDB not available: {e}")
        print("  Using in-memory storage instead")

# ============ HELPER FUNCTIONS ============
def strip_mongo_id(doc):
    """Remove MongoDB _id field from document"""
    if doc and "_id" in doc:
        doc = dict(doc)
        del doc["_id"]
    return doc

def get_app(session_id):
    if mongo_db is not None:
        return strip_mongo_id(mongo_db.applications.find_one({"sessionId": session_id})) or {}
    return db.applications.get(session_id, {})

def set_app(session_id, data):
    if mongo_db is not None:
        mongo_db.applications.update_one(
            {"sessionId": session_id},
            {"$set": data},
            upsert=True
        )
    else:
        if session_id not in db.applications:
            db.applications[session_id] = {"sessionId": session_id}
        db.applications[session_id].update(data)

def get_docs(session_id):
    if mongo_db is not None:
        return strip_mongo_id(mongo_db.documents.find_one({"sessionId": session_id})) or {}
    return db.documents.get(session_id, {})

def set_docs(session_id, data):
    if mongo_db is not None:
        mongo_db.documents.update_one(
            {"sessionId": session_id},
            {"$set": data},
            upsert=True
        )
    else:
        if session_id not in db.documents:
            db.documents[session_id] = {"sessionId": session_id}
        db.documents[session_id].update(data)

def get_decision(session_id):
    if mongo_db is not None:
        return strip_mongo_id(mongo_db.decisions.find_one({"sessionId": session_id})) or {}
    return db.decisions.get(session_id, {})

def set_decision(session_id, data):
    if mongo_db is not None:
        mongo_db.decisions.update_one(
            {"sessionId": session_id},
            {"$set": data},
            upsert=True
        )
    else:
        db.decisions[session_id] = data

# ============ AGENT FUNCTIONS ============

def sales_agent(session_id, message):
    """Sales Agent: Collects loan amount, purpose, personal details"""
    app_data = get_app(session_id)
    
    # Check what data we have
    has_amount = app_data.get("loan_amount") is not None
    has_income = app_data.get("income") is not None
    has_tenure = app_data.get("tenure") is not None
    
    if has_amount and has_income and has_tenure:
        # All data collected, move to verification
        set_app(session_id, {"status": "verification"})
        return {
            "step": "verification",
            "reply": f"✓ Thank you! I have your details:\n• Loan Amount: ₹{app_data.get('loan_amount'):,}\n• Monthly Income: ₹{app_data.get('income'):,}\n• Tenure: {app_data.get('tenure')} months\n\nNow let's verify your identity. Please upload your KYC documents (Aadhaar/PAN) using the upload section."
        }
    else:
        # Still collecting data
        missing = []
        if not has_amount:
            missing.append("loan amount")
        if not has_income:
            missing.append("monthly income")
        if not has_tenure:
            missing.append("preferred tenure")
        
        return {
            "step": "sales",
            "reply": f"👋 Hello! I'm your AI Loan Advisor.\n\nTo process your loan application, please fill out the Loan Requirements form on the left with:\n• Loan Amount\n• Tenure (months)\n• Monthly Income\n• Other details\n\nThen click Submit."
        }

def verification_agent(session_id):
    """Verification Agent: Performs KYC checks via Dummy CRM"""
    docs = get_docs(session_id)
    
    if docs.get("uploaded"):
        # Documents uploaded, perform "KYC check" (dummy)
        set_app(session_id, {"status": "underwriting", "kyc_verified": True})
        return {
            "step": "underwriting",
            "reply": f"✓ KYC Verification Complete!\n• Document: {docs.get('filename', 'Uploaded')}\n• Status: Verified ✓\n\nNow running credit assessment and ML prediction..."
        }
    else:
        return {
            "step": "verification",
            "reply": "📄 Please upload your KYC documents (Aadhaar, PAN, or Salary Slip) using the Document Upload section above.\n\nThis is required for identity verification."
        }

def underwriting_agent(session_id):
    """Underwriting Agent: Fetches credit score and runs ML prediction"""
    app_data = get_app(session_id)
    docs = get_docs(session_id)
    
    # Get loan parameters
    income = float(app_data.get("income", 50000))
    loan_amount = float(app_data.get("loan_amount", 200000))
    tenure = float(app_data.get("tenure", 12))
    
    # Calculate EMI and eligibility
    emi = loan_amount / max(tenure, 1)
    emi_to_income_ratio = emi / max(income, 1)
    
    # Dummy credit score (random but deterministic per session)
    credit_score = 650 + (hash(session_id) % 200)  # 650-850
    
    # ML-style decision logic
    if emi_to_income_ratio < 0.3 and credit_score >= 700:
        # Approved
        confidence = min(0.95, 0.7 + (credit_score - 700) / 500)
        decision = {
            "approved": True,
            "status": "approved",
            "confidence": round(confidence, 2),
            "credit_score": credit_score,
            "loan_amount": loan_amount,
            "emi": round(emi, 2),
            "tenure": int(tenure),
            "reason": "Good credit score and healthy EMI-to-income ratio"
        }
        set_decision(session_id, decision)
        set_app(session_id, {"status": "sanction"})
        return {
            "step": "sanction",
            "reply": f"🎉 **Congratulations! Your loan is APPROVED!**\n\n📊 Assessment Results:\n• Credit Score: {credit_score}\n• EMI: ₹{emi:,.0f}/month\n• Confidence: {confidence*100:.0f}%\n\nGenerating your Sanction Letter..."
        }
    
    elif emi_to_income_ratio < 0.5 and credit_score >= 600:
        # Need more docs (salary slip)
        if docs.get("salary_slip_uploaded"):
            # Re-evaluation after salary slip
            confidence = 0.75
            decision = {
                "approved": True,
                "status": "approved",
                "confidence": confidence,
                "credit_score": credit_score,
                "loan_amount": loan_amount,
                "emi": round(emi, 2),
                "tenure": int(tenure),
                "reason": "Approved after salary verification"
            }
            set_decision(session_id, decision)
            set_app(session_id, {"status": "sanction"})
            return {
                "step": "sanction",
                "reply": f"🎉 **Your loan is APPROVED after document verification!**\n\n📊 Assessment Results:\n• Credit Score: {credit_score}\n• EMI: ₹{emi:,.0f}/month\n\nGenerating your Sanction Letter..."
            }
        else:
            set_app(session_id, {"status": "need_docs"})
            return {
                "step": "need_docs",
                "reply": f"📋 **Additional Documents Required**\n\nYour application looks promising, but we need:\n• **Salary Slip** (last 3 months)\n\nPlease upload using the Document Upload section.\n\n📊 Current Assessment:\n• Credit Score: {credit_score}\n• EMI-to-Income: {emi_to_income_ratio*100:.0f}%"
            }
    else:
        # Rejected
        decision = {
            "approved": False,
            "status": "rejected",
            "confidence": 0.85,
            "credit_score": credit_score,
            "reason": f"EMI-to-income ratio too high ({emi_to_income_ratio*100:.0f}%) or credit score below threshold"
        }
        set_decision(session_id, decision)
        set_app(session_id, {"status": "rejected"})
        return {
            "step": "rejected",
            "reply": f"❌ **Loan Application Declined**\n\n📊 Assessment Results:\n• Credit Score: {credit_score}\n• EMI-to-Income Ratio: {emi_to_income_ratio*100:.0f}%\n• Required: Below 50%\n\n**Reason:** {decision['reason']}\n\nYou may apply again after 6 months or with a co-applicant."
        }

def sanction_agent(session_id):
    """Sanction Agent: Generates the final sanction letter PDF"""
    decision = get_decision(session_id)
    app_data = get_app(session_id)
    
    if not decision.get("approved"):
        return {
            "step": "end",
            "reply": "No approved decision found."
        }
    
    # Generate PDF
    pdf_id = str(uuid.uuid4())
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_dir = os.path.join(base_dir, "ml")
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, f"{pdf_id}.pdf")
    
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas as pdf_canvas
        from reportlab.lib.units import inch
        
        c = pdf_canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        
        # Header
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width/2, height - inch, "LOAN SANCTION LETTER")
        
        c.setFont("Helvetica", 12)
        c.drawCentredString(width/2, height - 1.3*inch, "AI Loan Advisor")
        
        # Line
        c.line(inch, height - 1.5*inch, width - inch, height - 1.5*inch)
        
        # Content
        y = height - 2*inch
        c.setFont("Helvetica", 11)
        
        lines = [
            f"Date: {__import__('datetime').datetime.now().strftime('%B %d, %Y')}",
            f"Application ID: {session_id}",
            "",
            "Dear Applicant,",
            "",
            "We are pleased to inform you that your loan application has been APPROVED.",
            "",
            "Loan Details:",
            f"  • Sanctioned Amount: ₹{decision.get('loan_amount', 0):,.0f}",
            f"  • Tenure: {decision.get('tenure', 12)} months",
            f"  • Monthly EMI: ₹{decision.get('emi', 0):,.0f}",
            f"  • Credit Score: {decision.get('credit_score', 'N/A')}",
            "",
            "Terms & Conditions:",
            "  1. This sanction is valid for 30 days from the date of issue.",
            "  2. Final disbursement subject to document verification.",
            "  3. Interest rate as per prevailing market rates.",
            "",
            "Congratulations on your approval!",
            "",
            "Best regards,",
            "AI Loan Advisor Team"
        ]
        
        for line in lines:
            c.drawString(inch, y, line)
            y -= 18
        
        c.save()
        print(f"✓ PDF generated: {pdf_path}")
        
    except Exception as e:
        print(f"✗ PDF generation error: {e}")
        traceback.print_exc()
        return {
            "step": "error",
            "reply": f"Error generating PDF: {str(e)}"
        }
    
    # Save sanction info
    if mongo_db is not None:
        mongo_db.sanctions.update_one(
            {"sessionId": session_id},
            {"$set": {"pdfId": pdf_id}},
            upsert=True
        )
    else:
        db.sanctions[session_id] = {"pdfId": pdf_id}
    
    set_app(session_id, {"status": "completed", "pdfId": pdf_id})
    
    return {
        "step": "completed",
        "reply": f"📄 **Sanction Letter Generated!**\n\nYour loan of ₹{decision.get('loan_amount', 0):,.0f} has been approved.\n\n[Download Sanction Letter](/api/download/{pdf_id})\n\nThank you for choosing AI Loan Advisor!",
        "pdfId": pdf_id,
        "decision": decision
    }

def master_agent(session_id, message):
    """Master Agent: Orchestrates the entire workflow"""
    app_data = get_app(session_id)
    status = app_data.get("status", "start")
    
    print(f"[Master Agent] Session: {session_id}, Status: {status}, Message: {message[:50]}...")
    
    # Route to appropriate agent based on status
    if status == "start" or status == "sales":
        return sales_agent(session_id, message)
    
    elif status == "verification":
        return verification_agent(session_id)
    
    elif status == "underwriting":
        return underwriting_agent(session_id)
    
    elif status == "need_docs":
        # Check if new docs uploaded
        docs = get_docs(session_id)
        if docs.get("salary_slip_uploaded"):
            set_app(session_id, {"status": "underwriting"})
            return underwriting_agent(session_id)
        else:
            return {
                "step": "need_docs",
                "reply": "📋 Please upload your Salary Slip to continue with the application.\n\nUse the Document Upload section above."
            }
    
    elif status == "sanction":
        return sanction_agent(session_id)
    
    elif status == "completed":
        app_data = get_app(session_id)
        pdf_id = app_data.get("pdfId")
        return {
            "step": "completed",
            "reply": f"✅ Your application is complete!\n\n[Download Sanction Letter](/api/download/{pdf_id})" if pdf_id else "✅ Your application is complete!",
            "pdfId": pdf_id
        }
    
    elif status == "rejected":
        return {
            "step": "rejected",
            "reply": "❌ Your application was not approved. You may apply again after 6 months."
        }
    
    else:
        # Unknown status, restart
        set_app(session_id, {"status": "sales"})
        return sales_agent(session_id, message)

# ============ API ENDPOINTS ============

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "mongo": mongo_db is not None})

@app.route("/api/apply", methods=["POST"])
def apply():
    """Save loan application data from form"""
    try:
        data = request.get_json() or {}
        session_id = data.get("sessionId")
        
        if not session_id:
            return jsonify({"error": "Missing sessionId"}), 400
        
        # Extract and save fields
        fields = {}
        for key in ["loan_amount", "tenure", "purpose", "income", "employment", "age"]:
            if data.get(key) is not None:
                fields[key] = data[key]
        
        # Set initial status if new application
        app_data = get_app(session_id)
        if not app_data.get("status"):
            fields["status"] = "sales"
        
        set_app(session_id, fields)
        
        print(f"✓ Application saved: {session_id} -> {fields}")
        return jsonify({"ok": True, "saved": fields})
    
    except Exception as e:
        print(f"✗ Apply error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/chat", methods=["POST"])
def chat():
    """Main chat endpoint - Master Agent handles all messages"""
    try:
        data = request.get_json() or {}
        session_id = data.get("sessionId")
        message = data.get("message", "")
        
        if not session_id:
            return jsonify({"error": "Missing sessionId"}), 400
        
        # Initialize if new session
        app_data = get_app(session_id)
        if not app_data:
            set_app(session_id, {"status": "start"})
        
        # Route through Master Agent
        result = master_agent(session_id, message)
        
        print(f"✓ Chat response: {result.get('step')} -> {result.get('reply', '')[:50]}...")
        return jsonify(result)
    
    except Exception as e:
        print(f"✗ Chat error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e), "reply": f"Error: {str(e)}"}), 500

@app.route("/api/upload", methods=["POST"])
def upload():
    """Handle document upload"""
    try:
        session_id = request.form.get("sessionId")
        file = request.files.get("file")
        
        if not session_id:
            return jsonify({"error": "Missing sessionId"}), 400
        
        if not file:
            return jsonify({"error": "No file provided"}), 400
        
        filename = file.filename or "document"
        
        # Check if it's a salary slip (by name heuristic)
        is_salary_slip = "salary" in filename.lower() or "slip" in filename.lower() or "payslip" in filename.lower()
        
        # Save document info
        doc_data = {
            "uploaded": True,
            "filename": filename,
            "salary_slip_uploaded": is_salary_slip or get_docs(session_id).get("salary_slip_uploaded", False)
        }
        set_docs(session_id, doc_data)
        
        # Check current status and potentially advance
        app_data = get_app(session_id)
        status = app_data.get("status", "start")
        
        if status == "verification":
            set_app(session_id, {"status": "underwriting"})
        elif status == "need_docs" and is_salary_slip:
            set_app(session_id, {"status": "underwriting"})
        
        print(f"✓ Document uploaded: {session_id} -> {filename}")
        return jsonify({"ok": True, "filename": filename, "salary_slip": is_salary_slip})
    
    except Exception as e:
        print(f"✗ Upload error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/download/<pdf_id>", methods=["GET"])
def download(pdf_id):
    """Download generated PDF"""
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(base_dir, "ml", f"{pdf_id}.pdf")
        
        if not os.path.exists(pdf_path):
            return jsonify({"error": "PDF not found"}), 404
        
        return send_file(pdf_path, as_attachment=True, download_name=f"sanction_letter_{pdf_id[:8]}.pdf")
    
    except Exception as e:
        print(f"✗ Download error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/status/<session_id>", methods=["GET"])
def get_status(session_id):
    """Get current application status"""
    try:
        app_data = get_app(session_id)
        docs = get_docs(session_id)
        decision = get_decision(session_id)
        
        return jsonify({
            "application": app_data,
            "documents": docs,
            "decision": decision
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# ============ MAIN ============

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 AI Loan Advisor Backend Starting...")
    print("="*50)
    print(f"📦 MongoDB: {'Connected ✓' if mongo_db is not None else 'Using in-memory storage'}")
    print(f"🌐 Server: http://localhost:5000")
    print("="*50 + "\n")
    
    app.run(host="0.0.0.0", port=5000, debug=False)
