import { downloadUrl } from "../api/client";

export default function DecisionPanel({ decision }) {
  if (!decision) return null;
  const { status, amount, emi, tenure, pdfId, credit_score, confidence, loan_amount, reason } = decision;
  
  const isApproved = status === "approved";
  const isRejected = status === "rejected";
  
  return (
    <div className="card" style={{
      backgroundColor: isApproved ? '#dcfce7' : isRejected ? '#fef2f2' : '#f1f5f9',
      border: `2px solid ${isApproved ? '#16a34a' : isRejected ? '#dc2626' : '#64748b'}`
    }}>
      <h3 style={{ marginTop: 0, color: isApproved ? '#16a34a' : isRejected ? '#dc2626' : '#1e293b' }}>
        {isApproved ? '🎉 Loan Approved!' : isRejected ? '❌ Loan Declined' : '📊 Decision Status'}
      </h3>
      
      <div style={{ marginBottom: 12 }}>
        <strong>Status:</strong> <span style={{ 
          textTransform: 'capitalize',
          color: isApproved ? '#16a34a' : isRejected ? '#dc2626' : '#64748b',
          fontWeight: 'bold'
        }}>{status}</span>
      </div>
      
      {(loan_amount || amount) && (
        <p><strong>Loan Amount:</strong> ₹{(loan_amount || amount).toLocaleString()}</p>
      )}
      {emi && <p><strong>Monthly EMI:</strong> ₹{emi.toLocaleString()}</p>}
      {tenure && <p><strong>Tenure:</strong> {tenure} months</p>}
      {credit_score && <p><strong>Credit Score:</strong> {credit_score}</p>}
      {confidence && <p><strong>Confidence:</strong> {(confidence * 100).toFixed(0)}%</p>}
      {reason && <p><strong>Reason:</strong> {reason}</p>}
      
      {pdfId && (
        <div style={{ marginTop: 16, textAlign: 'center' }}>
          <a href={downloadUrl(pdfId)} target="_blank" rel="noreferrer"
            style={{
              display: 'inline-block',
              padding: '12px 24px',
              backgroundColor: '#16a34a',
              color: 'white',
              textDecoration: 'none',
              borderRadius: 8,
              fontWeight: 'bold'
            }}>
            📥 Download Sanction Letter
          </a>
        </div>
      )}
    </div>
  );
}
