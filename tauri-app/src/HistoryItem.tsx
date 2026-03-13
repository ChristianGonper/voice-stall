import { useState } from "react";
import { writeText } from "@tauri-apps/plugin-clipboard-manager";

export function HistoryItem({ ts, text }: { ts: string, text: string }) {
  const [copied, setCopied] = useState(false);

  const onCopy = async () => {
    try {
      await writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy", err);
    }
  };

  return (
    <div className="history-item">
      <div className="history-content">
        <div className="history-ts">{ts}</div>
        <div className="history-text">{text}</div>
      </div>
      <button 
        className={`history-copy-btn ${copied ? "copied" : ""}`} 
        onClick={onCopy}
        title={copied ? "¡Copiado!" : "Copiar al portapapeles"}
      >
        {copied ? (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
        ) : (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
        )}
      </button>
    </div>
  );
}
