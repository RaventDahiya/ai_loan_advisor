import { useState, useRef } from "react";
import Chat from "./components/Chat";
import LoanForm from "./components/LoanForm";
import DocumentUpload from "./components/DocumentUpload";
import DecisionPanel from "./components/DecisionPanel";

export default function App() {
  const [sessionId] = useState(() => Math.random().toString(36).slice(2));
  const [decision, setDecision] = useState(null);
  const [uploadTrigger, setUploadTrigger] = useState(0);

  function handleSubmitRequirements(req) {
    setDecision({ status: "submitted", amount: req.loan_amount, tenure: req.tenure });
  }
  
  function handleUploadComplete(result) {
    // Trigger chat to continue after document upload
    setUploadTrigger(t => t + 1);
  }
  
  function handleDecision(dec) {
    setDecision(dec);
  }

  return (
    <div className="container">
      <div className="header">
        <h2>🏦 AI Loan Advisor</h2>
        <small style={{ color: '#64748b' }}>Session: {sessionId}</small>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20 }}>
        <div>
          <LoanForm sessionId={sessionId} onSubmit={handleSubmitRequirements} />
          <DocumentUpload sessionId={sessionId} onUploadComplete={handleUploadComplete} />
        </div>
        <div>
          <Chat sessionId={sessionId} onDecision={handleDecision} uploadTrigger={uploadTrigger} />
        </div>
        {decision && <DecisionPanel decision={decision} />}
      </div>
    </div>
  );
}
