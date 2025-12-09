import { useState } from "react";
import { uploadDoc } from "../api/client";

export default function DocumentUpload({ sessionId, onUploadComplete }) {
  const [status, setStatus] = useState("");
  const [uploading, setUploading] = useState(false);

  async function handleUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setStatus("📤 Uploading...");
    try {
      const result = await uploadDoc(sessionId, file);
      const isSalary = result.salary_slip;
      setStatus(`✅ Uploaded: ${result.filename}${isSalary ? " (Salary Slip detected)" : ""}`);
      
      // Notify parent to trigger chat continuation
      if (onUploadComplete) {
        onUploadComplete(result);
      }
    } catch (e) {
      setStatus(`❌ Error: ${e.message}`);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="card">
      <h3 style={{marginTop:0}}>📄 Document Upload</h3>
      <p style={{ color: '#64748b', fontSize: 14, marginBottom: 12 }}>
        Upload KYC documents (Aadhaar/PAN) or Salary Slip for verification.
      </p>
      <input 
        type="file" 
        onChange={handleUpload} 
        disabled={uploading}
        accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
        style={{ marginBottom: 8 }}
      />
      <div style={{ 
        marginTop: 8, 
        padding: status ? 8 : 0,
        borderRadius: 6,
        backgroundColor: status.includes("✅") ? '#dcfce7' : status.includes("❌") ? '#fef2f2' : '#f1f5f9',
        color: status.includes("✅") ? '#16a34a' : status.includes("❌") ? '#dc2626' : '#64748b'
      }}>
        {status}
      </div>
    </div>
  );
}
