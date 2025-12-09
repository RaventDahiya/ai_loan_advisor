import { useState } from "react";
import { saveApplication } from "../api/client";

export default function LoanForm({ onSubmit, sessionId }) {
  const [status, setStatus] = useState("");
  const [submitted, setSubmitted] = useState(false);
  
  function handleSubmit(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target).entries());
    data.loan_amount = Number(data.loan_amount);
    data.tenure = Number(data.tenure);
    data.income = Number(data.income);
    data.age = Number(data.age);
    
    setStatus("Saving...");
    saveApplication(sessionId, data)
      .then(() => {
        setStatus("✅ Saved! Now chat with the AI advisor to proceed.");
        setSubmitted(true);
        onSubmit?.(data);
      })
      .catch((err) => setStatus(`❌ Error: ${err.message}`));
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h3 style={{ marginTop: 0 }}>📋 Loan Requirements</h3>
      <div className="form-grid">
        <div>
          <label className="label">Loan Amount (₹)</label>
          <input className="input" name="loan_amount" type="number" min="10000" step="1000" required placeholder="e.g., 500000" />
        </div>
        <div>
          <label className="label">Tenure (months)</label>
          <input className="input" name="tenure" type="number" min="6" max="360" step="1" required placeholder="e.g., 12" />
        </div>
        <div>
          <label className="label">Monthly Income (₹)</label>
          <input className="input" name="income" type="number" min="5000" step="100" required placeholder="e.g., 80000" />
        </div>
        <div>
          <label className="label">Purpose</label>
          <input className="input" name="purpose" type="text" placeholder="e.g., Home Renovation" />
        </div>
        <div>
          <label className="label">Employment</label>
          <select className="input" name="employment" required>
            <option value="">Select...</option>
            <option value="Salaried">Salaried</option>
            <option value="Self-employed">Self-employed</option>
            <option value="Business">Business Owner</option>
            <option value="Freelancer">Freelancer</option>
          </select>
        </div>
        <div>
          <label className="label">Age</label>
          <input className="input" name="age" type="number" min="18" max="70" required placeholder="e.g., 30" />
        </div>
      </div>
      <div style={{ marginTop: 16, display: 'flex', alignItems: 'center', gap: 12 }}>
        <button className="button" type="submit" disabled={submitted}>
          {submitted ? '✓ Submitted' : 'Submit Application'}
        </button>
      </div>
      {status && (
        <div style={{ 
          marginTop: 12, 
          padding: 10, 
          borderRadius: 6,
          backgroundColor: status.includes("✅") ? '#dcfce7' : status.includes("❌") ? '#fef2f2' : '#f1f5f9',
          color: status.includes("✅") ? '#16a34a' : status.includes("❌") ? '#dc2626' : '#64748b',
          fontSize: 14
        }}>
          {status}
        </div>
      )}
    </form>
  );
}
