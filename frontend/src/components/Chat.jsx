import { useEffect, useRef, useState, useCallback } from "react";
import { postChat, API_BASE } from "../api/client";

export default function Chat({ sessionId, onDecision, uploadTrigger }) {
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hello! I'm your AI loan advisor. Fill out the form and submit, then chat with me to proceed!" }
  ]);
  const [input, setInput] = useState("");
  const [pdfId, setPdfId] = useState(null);
  const [processing, setProcessing] = useState(false);
  const listRef = useRef(null);
  const lastUploadTrigger = useRef(0);

  useEffect(() => {
    listRef.current?.scrollTo(0, listRef.current.scrollHeight);
  }, [messages]);
  
  // React to document upload
  useEffect(() => {
    if (uploadTrigger && uploadTrigger !== lastUploadTrigger.current) {
      lastUploadTrigger.current = uploadTrigger;
      // Auto-send message to continue after upload
      sendMessage("I uploaded my documents, please continue with verification");
    }
  }, [uploadTrigger]);

  const processResponse = useCallback(async (resp) => {
    // Add reply to messages
    let text = resp.reply || "(no reply)";
    
    // Handle PDF download link
    if (resp.pdfId) {
      setPdfId(resp.pdfId);
      text += `\n\n📥 **[Click here to download your Sanction Letter](${API_BASE}/api/download/${resp.pdfId})**`;
    }
    
    const botMsg = { role: "assistant", text, step: resp.step, pdfId: resp.pdfId };
    setMessages((m) => [...m, botMsg]);
    
    // Report decision to parent
    if (onDecision && resp.decision) {
      onDecision(resp.decision);
    }
    
    // Auto-continue for certain steps
    if (resp.step === "sanction" && !resp.pdfId) {
      // Need to call again to generate PDF
      setMessages((m) => [...m, { role: "system", text: "⏳ Generating Sanction Letter..." }]);
      await new Promise(r => setTimeout(r, 500));
      const nextResp = await postChat({ sessionId, message: "generate sanction letter" });
      await processResponse(nextResp);
    } else if (resp.step === "underwriting" && resp.reply && !resp.reply.includes("APPROVED") && !resp.reply.includes("Declined")) {
      // Auto-continue to get underwriting result
      await new Promise(r => setTimeout(r, 1000));
      const nextResp = await postChat({ sessionId, message: "check status" });
      await processResponse(nextResp);
    }
  }, [sessionId, onDecision]);

  async function sendMessage(msg, showInChat = true) {
    if (!msg.trim() || processing) return;
    
    if (showInChat) {
      const userMsg = { role: "user", text: msg };
      setMessages((m) => [...m, userMsg]);
    }
    setInput("");
    
    setProcessing(true);
    try {
      const resp = await postChat({ sessionId, message: msg });
      await processResponse(resp);
    } catch (e) {
      setMessages((m) => [...m, { role: "assistant", text: `Error: ${e.message}` }]);
    } finally {
      setProcessing(false);
    }
  }
  
  function send(customMessage) {
    const msg = customMessage || input;
    sendMessage(msg, !customMessage);
  }

  function onKey(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  // Render message with markdown-like formatting
  function renderMessage(text) {
    // Convert **bold** to <strong>
    let html = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    // Convert [text](url) to clickable links
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    // Convert newlines to <br>
    html = html.replace(/\n/g, '<br/>');
    return <span dangerouslySetInnerHTML={{ __html: html }} />;
  }

  return (
    <div className="card">
      <h3 style={{marginTop:0}}>💬 Chat with AI Advisor</h3>
      <div ref={listRef} className="chat" style={{maxHeight: 350, overflowY: 'auto'}}>
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`} style={{ 
            textAlign: m.role === "user" ? "right" : "left",
            marginBottom: 8
          }}>
            <span className="bubble" style={{
              display: 'inline-block',
              padding: '8px 12px',
              borderRadius: 12,
              backgroundColor: m.role === "user" ? '#3b82f6' : m.role === "system" ? '#f59e0b' : '#e2e8f0',
              color: m.role === "user" ? 'white' : m.role === "system" ? 'white' : '#1e293b',
              maxWidth: '85%'
            }}>
              {renderMessage(m.text)}
            </span>
          </div>
        ))}
        {processing && (
          <div className="msg assistant" style={{ textAlign: 'left' }}>
            <span className="bubble" style={{ display: 'inline-block', padding: '8px 12px', borderRadius: 12, backgroundColor: '#e2e8f0' }}>
              ⏳ Processing...
            </span>
          </div>
        )}
      </div>
      
      {pdfId && (
        <div style={{ marginTop: 12, padding: 12, backgroundColor: '#dcfce7', borderRadius: 8, textAlign: 'center' }}>
          <strong>🎉 Loan Approved!</strong><br/>
          <a href={`${API_BASE}/api/download/${pdfId}`} target="_blank" rel="noopener" 
             style={{ color: '#16a34a', fontWeight: 'bold' }}>
            📥 Download Sanction Letter (PDF)
          </a>
        </div>
      )}
      
      <textarea className="input" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={onKey}
        rows={2} style={{ width: "100%", marginTop: 8 }} placeholder="Type a message..." disabled={processing} />
      <div style={{display:'flex', justifyContent:'space-between', marginTop:8, gap: 8}}>
        <button className="button" onClick={() => send("Check my application status")} disabled={processing}
          style={{ flex: 1, backgroundColor: '#64748b' }}>
          Check Status
        </button>
        <button className="button" onClick={() => send()} disabled={processing || !input.trim()}
          style={{ flex: 1 }}>
          Send
        </button>
      </div>
    </div>
  );
}
