export function FloatingPill({ 
  status, 
  statusTone, 
  statusMessage, 
  onToggle, 
  onExpand 
}: { 
  status: string, 
  statusTone: (s: string) => string, 
  statusMessage: string, 
  onToggle: () => void, 
  onExpand: () => void 
}) {
  return (
    <div className="floating-pill" data-tauri-drag-region>
      <div className={`pill-status-dot dot bg-${statusTone(status)}`} />
      <div className="pill-transcription" data-tauri-drag-region>
        {statusMessage}
      </div>
      <div className="pill-actions">
        <button 
          className={`pill-btn record ${status === "recording" ? "danger" : "primary"}`} 
          onClick={onToggle}
          title={status === "recording" ? "Detener" : "Dictar"}
        >
          {status === "recording" ? (
            <svg viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="2" /></svg>
          ) : (
            <svg viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="6" /></svg>
          )}
        </button>
        <button className="pill-btn expand" onClick={onExpand} title="Expandir">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polyline points="15 3 21 3 21 9"></polyline><polyline points="9 21 3 21 3 15"></polyline></svg>
        </button>
      </div>
    </div>
  );
}
