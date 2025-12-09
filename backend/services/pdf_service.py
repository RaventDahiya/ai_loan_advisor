import os
import uuid
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from services.mongo import db


def generate_sanction_letter(session_id: str, decision: dict) -> str:
    pdf_id = str(uuid.uuid4())
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdf_dir = os.path.join(base_dir, "ml")
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, f"{pdf_id}.pdf")

    c = canvas.Canvas(pdf_path, pagesize=A4)
    text = c.beginText(40, 800)
    text.textLine("Sanction Letter")
    text.textLine("")
    for k, v in decision.items():
        text.textLine(f"{k}: {v}")
    c.drawText(text)
    c.showPage()
    c.save()

    db.sanctions.update_one({"sessionId": session_id}, {"$set": {"pdfId": pdf_id}}, upsert=True)
    return pdf_id
