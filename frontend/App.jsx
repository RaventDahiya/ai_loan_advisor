import { useState } from "react";
import Chat from "./components/Chat";
import LoanForm from "./components/LoanForm";
import DocumentUpload from "./components/DocumentUpload";
import DecisionPanel from "./components/DecisionPanel";

export default function App() {
  const [sessionId] = useState(() => Math.random().toString(36).slice(2));
  const [decision, setDecision] = useState(null);

  function handleSubmitRequirements(req) {
    // In a fuller app, send to backend; for now, store
    setDecision({ status: "underwriting", amount: req.loan_amount, tenure: req.tenure });
  }

  return (
    <div style={{ maxWidth: 800, margin: "20px auto", fontFamily: "system-ui, sans-serif" }}>
      <h2>AI Loan Advisor</h2>
      <LoanForm onSubmit={handleSubmitRequirements} />
      <DocumentUpload sessionId={sessionId} />
      <Chat sessionId={sessionId} />
      <DecisionPanel decision={decision} />
    </div>
  );
}
