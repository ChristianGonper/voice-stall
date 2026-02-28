import { useEffect, useMemo, useState } from "react";
import { listen } from "@tauri-apps/api/event";
import { LogicalSize } from "@tauri-apps/api/dpi";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { getMetrics, initApp, saveSettings, setHotkey, toggleDictation } from "./api";
import type { AppStateDto, FullConfig, MetricsSummary, StatusEvent } from "./types";

type TabKey = "control" | "settings" | "history" | "metrics";
type ResizeDirection =
  | "East"
  | "North"
  | "NorthEast"
  | "NorthWest"
  | "South"
  | "SouthEast"
  | "SouthWest"
  | "West";

const STATUS_LABELS: Record<string, string> = {
  idle: "IDLE",
  loading: "LOAD",
  recording: "REC",
  processing: "PROC",
  error: "ERR",
};

const EMPTY_METRICS: MetricsSummary = {
  count: 0,
  avg_total_ms: 0,
  avg_transcribe_ms: 0,
  avg_paste_ms: 0,
};

const NORMAL_WINDOW_SIZE = new LogicalSize(900, 760);
const MINI_WINDOW_SIZE = new LogicalSize(360, 168);
const RESIZE_HANDLES: { direction: ResizeDirection; className: string }[] = [
  { direction: "North", className: "resize-north" },
  { direction: "South", className: "resize-south" },
  { direction: "East", className: "resize-east" },
  { direction: "West", className: "resize-west" },
  { direction: "NorthEast", className: "resize-north-east" },
  { direction: "NorthWest", className: "resize-north-west" },
  { direction: "SouthEast", className: "resize-south-east" },
  { direction: "SouthWest", className: "resize-south-west" },
];

function statusTone(status: string): "idle" | "recording" | "processing" | "error" {
  if (status === "recording") return "recording";
  if (status === "processing" || status === "loading") return "processing";
  if (status === "error") return "error";
  return "idle";
}

function WaveBars({ status }: { status: string }) {
  const tone = statusTone(status);
  const bars = Array.from({ length: 6 });
  return (
    <div className={`wave wave-${tone}`}>
      {bars.map((_, index) => (
        <span
          key={index}
          className="wave-bar"
          style={{ animationDelay: `${index * 0.15}s` }}
        />
      ))}
    </div>
  );
}

export function App() {
  const appWindow = useMemo(() => getCurrentWindow(), []);
  const [ready, setReady] = useState(false);
  const [bootError, setBootError] = useState<string | null>(null);
  const [status, setStatus] = useState("loading");
  const [statusMessage, setStatusMessage] = useState("Cargando motor...");
  const [config, setConfig] = useState<FullConfig | null>(null);
  const [historyItems, setHistoryItems] = useState<{ ts: string, text: string }[]>([]);
  const [metrics, setMetrics] = useState<MetricsSummary>(EMPTY_METRICS);
  const [newDictKey, setNewDictKey] = useState("");
  const [newDictValue, setNewDictValue] = useState("");
  const [tab, setTab] = useState<TabKey>("control");
  const [miniMode, setMiniMode] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);

  const syncWindowState = async () => {
    try {
      setIsMaximized(await appWindow.isMaximized());
    } catch (err) {
      console.error("Failed to read window state", err);
    }
  };

  const loadInitialState = async () => {
    try {
      const state: AppStateDto = await initApp();
      setConfig(state.config);
      setMetrics(state.metrics);
      setHistoryItems(state.history);
      setStatus(state.status);
      setStatusMessage(state.status_message);
      setBootError(null);
      setReady(true);
    } catch (err) {
      console.error("Init error", err);
      setBootError(String(err));
      setReady(true);
    }
  };

  useEffect(() => {
    let unlistenStatus: (() => void) | undefined;
    let unlistenDiag: (() => void) | undefined;
    let unlistenTranscription: (() => void) | undefined;

    const setup = async () => {
      await syncWindowState();
      unlistenStatus = await listen<StatusEvent>("status", (ev) => {
        setStatus(ev.payload.state);
        setStatusMessage(ev.payload.message);
      });
      unlistenDiag = await listen("diag", async () => {
        const m = await getMetrics(5);
        setMetrics(m);
      });
      unlistenTranscription = await listen<{ text: string; ts: string }>("transcription", (ev) => {
        setHistoryItems((prev) => [ev.payload, ...prev].slice(0, config?.app.history_limit || 10));
      });

      await loadInitialState();
    };

    setup().catch((err) => {
      setStatus("error");
      setStatusMessage(`Error init: ${String(err)}`);
      setBootError(String(err));
      setReady(true);
    });

    return () => {
      if (unlistenStatus) unlistenStatus();
      if (unlistenDiag) unlistenDiag();
      if (unlistenTranscription) unlistenTranscription();
    };
  }, [appWindow, config?.app.history_limit]);

  const hotkeyLabel = useMemo(() => {
    const value = config?.app.hotkey ?? "ctrl+alt+s";
    return value.split("+").map((x) => x.toUpperCase());
  }, [config]);

  const onToggle = async () => {
    try {
      const result = await toggleDictation();
      setStatus(result.status);
      setStatusMessage(result.message);
      // Transcription history is now handled by the 'transcription' event listener
      const updatedMetrics = await getMetrics(5);
      setMetrics(updatedMetrics);
    } catch (err) {
      setStatus("error");
      setStatusMessage(`Error dictado: ${String(err)}`);
    }
  };

  const onSave = async () => {
    if (!config) return;
    await saveSettings(config);
    const hotkeyResult = await setHotkey(config.app.hotkey);
    setStatus("idle");
    setStatusMessage(`Configuración aplicada (${hotkeyResult.hotkey})`);
  };

  const addDictionaryItem = () => {
    if (!config) return;
    const key = newDictKey.trim().toLowerCase();
    const value = newDictValue.trim();
    if (!key || !value) return;
    setConfig({
      ...config,
      dictionary: {
        ...config.dictionary,
        [key]: value,
      },
    });
    setNewDictKey("");
    setNewDictValue("");
  };

  const toggleMiniMode = async (enable: boolean) => {
    try {
      if (await appWindow.isMaximized()) {
        await appWindow.unmaximize();
      }

      if (enable) {
        await appWindow.setSize(MINI_WINDOW_SIZE);
        await appWindow.setAlwaysOnTop(true);
      } else {
        await appWindow.setSize(NORMAL_WINDOW_SIZE);
      }

      setMiniMode(enable);
      await syncWindowState();
    } catch (err) {
      console.error("Failed to resize window", err);
      setStatus("error");
      setStatusMessage("No se pudo cambiar el tamano de la ventana.");
    }
  };

  const handleResize = async (direction: ResizeDirection) => {
    try {
      await appWindow.startResizeDragging(direction);
    } catch (err) {
      console.error("Failed to start resizing", err);
    }
  };

  const toggleWindowMaximize = async () => {
    try {
      if (miniMode) {
        await appWindow.setSize(NORMAL_WINDOW_SIZE);
        setMiniMode(false);
      }

      await appWindow.toggleMaximize();
      await syncWindowState();
    } catch (err) {
      console.error("Failed to toggle maximize", err);
      setStatus("error");
      setStatusMessage("No se pudo maximizar la ventana.");
    }
  };

  if (!ready) {
    return (
      <div className="shell" style={{ justifyContent: "center", alignItems: "center", background: "#0A0E17" }}>
        <div className="status-badge loading">Iniciando Voice Stall...</div>
      </div>
    );
  }

  if (bootError || !config) {
    return (
      <div className="shell">
        <div className="app-container" style={{ padding: 24, justifyContent: "center", alignItems: "center" }}>
          <h2>Error Fatal</h2>
          <p style={{ color: "var(--accent-red)" }}>{bootError ?? "No se pudo cargar la configuración."}</p>
          <button className="primary" onClick={() => window.location.reload()}>Reintentar</button>
        </div>
      </div>
    );
  }

  return (
    <div className="shell">
      <div
        className={`titlebar ${miniMode ? "compact" : ""}`}
      >
        <div
          className="titlebar-drag"
          data-tauri-drag-region
          onDoubleClick={() => {
            void toggleWindowMaximize();
          }}
          onPointerDown={(e) => {
            if (e.buttons === 1) {
              void appWindow.startDragging().catch(console.error);
            }
          }}
        >
          <div className="titlebar-title">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="22"></line></svg>
            Voice Stall
          </div>
        </div>
        <div className="titlebar-actions">
          <button
            className="titlebar-btn"
            onClick={() => {
              void toggleMiniMode(!miniMode);
            }}
            title={miniMode ? "Expandir panel" : "Acoplar panel"}
          >
            {miniMode ? (
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15 3 21 3 21 9"></polyline><polyline points="9 21 3 21 3 15"></polyline><line x1="21" y1="3" x2="14" y2="10"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>
            ) : (
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="4 14 10 14 10 20"></polyline><polyline points="20 10 14 10 14 4"></polyline><line x1="14" y1="10" x2="21" y2="3"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>
            )}
          </button>
          <button className="titlebar-btn" onClick={() => { void toggleWindowMaximize(); }} title={isMaximized ? "Restaurar" : "Maximizar"}>
            {isMaximized ? (
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M8 8h11v11H8z"></path><path d="M5 16H4V5h11v1"></path></svg>
            ) : (
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="5" y="5" width="14" height="14"></rect></svg>
            )}
          </button>
          <button className="titlebar-btn" onClick={() => { void appWindow.minimize().catch(console.error); }} title="Minimizar">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="5" y1="12" x2="19" y2="12"></line></svg>
          </button>
          <button className="titlebar-btn close" onClick={() => { void appWindow.close().catch(console.error); }} title="Cerrar">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>
      </div>

      <div className="app-container">
        {miniMode ? (
          <div className="mini-widget">
            <div
              className="mini-header"
              data-tauri-drag-region
              onPointerDown={(e) => {
                if (e.buttons === 1) {
                  void appWindow.startDragging().catch(console.error);
                }
              }}
            >
              <div className="mini-brand">
                <span className={`dot bg-${statusTone(status)}`}></span>
                Voice Stall
              </div>
              <span className={`status-badge ${statusTone(status)}`}>
                {STATUS_LABELS[status] ?? status.toUpperCase()}
              </span>
            </div>
            <div className="mini-body">
              <div className="mini-status-text">{statusMessage}</div>
              <WaveBars status={status} />
            </div>
            <div className="mini-footer">
              <button className={status === "recording" ? "danger" : "primary"} onClick={onToggle} style={{ flex: 1 }}>
                {status === "recording" ? "Detener" : "Dictar"}
              </button>
              <button onClick={() => toggleMiniMode(false)} title="Expandir">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15 3 21 3 21 9"></polyline><polyline points="9 21 3 21 3 15"></polyline><line x1="21" y1="3" x2="14" y2="10"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>
              </button>
            </div>
          </div>
        ) : (
          <div className="app-content">
            <div className="app-header">
              <div>
                <h1 className="brand">Voice Stall</h1>
                <div className="subtitle">Dictado STT local ultrarrápido</div>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px' }}>
                <span className={`status-badge ${statusTone(status)}`}>
                  {STATUS_LABELS[status] ?? status.toUpperCase()}
                </span>
                <div className="hotkey-display">
                  {hotkeyLabel.map((k, i) => (
                    <span key={i} className="kbd">{k}</span>
                  ))}
                </div>
              </div>
            </div>

            <div className="tabs-nav">
              {(["control", "settings", "history", "metrics"] as TabKey[]).map((t) => (
                <button
                  key={t}
                  className={`tab-btn ${tab === t ? "active" : ""}`}
                  onClick={() => setTab(t)}
                >
                  {t.charAt(0).toUpperCase() + t.slice(1)}
                </button>
              ))}
            </div>

            {tab === "control" && (
              <div className="panel">
                <h3>Panel de Control</h3>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
                  <div>
                    <div style={{ fontSize: '1.1rem', marginBottom: '8px' }}>{statusMessage}</div>
                    <WaveBars status={status} />
                  </div>
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <button onClick={() => { void toggleMiniMode(true); }}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="4 14 10 14 10 20"></polyline><polyline points="20 10 14 10 14 4"></polyline><line x1="14" y1="10" x2="21" y2="3"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>
                      Modo Mini
                    </button>
                    <button className={status === "recording" ? "danger" : "primary"} onClick={onToggle} style={{ padding: '12px 24px', fontSize: '1.1rem' }}>
                      {status === "recording" ? "Detener Dictado" : "Iniciar Dictado"}
                    </button>
                  </div>
                </div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: 6, verticalAlign: 'middle' }}><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                  Usa el atajo de teclado para alternar rápidamente en cualquier ventana.
                </div>
              </div>
            )}

            {tab === "settings" && (
              <div className="panel">
                <h3>Ajustes Generales</h3>
                <div className="grid-2">
                  <label>
                    Atajo de teclado
                    <input
                      value={config.app.hotkey}
                      onChange={(e) => setConfig({ ...config, app: { ...config.app, hotkey: e.target.value } })}
                    />
                  </label>
                  <label>
                    Límite historial
                    <input
                      type="number"
                      min={1}
                      max={50}
                      value={config.app.history_limit}
                      onChange={(e) =>
                        setConfig({ ...config, app: { ...config.app, history_limit: Number(e.target.value) || 10 } })
                      }
                    />
                  </label>
                  <label>
                    Modelo STT
                    <select
                      value={config.engine.model_size}
                      onChange={(e) => setConfig({ ...config, engine: { ...config.engine, model_size: e.target.value } })}
                    >
                      <option value="large-v3-turbo">large-v3-turbo (Rápido)</option>
                      <option value="base">base (Ligero)</option>
                    </select>
                  </label>
                  <label>
                    Idioma
                    <select
                      value={config.engine.language}
                      onChange={(e) => setConfig({ ...config, engine: { ...config.engine, language: e.target.value } })}
                    >
                      <option value="auto">Automático</option>
                      <option value="es">Español</option>
                      <option value="en">Inglés</option>
                    </select>
                  </label>
                </div>

                <div style={{ marginTop: '24px', marginBottom: '24px' }}>
                  <label className="row">
                    <input
                      type="checkbox"
                      checked={config.app.diagnostic_mode}
                      onChange={(e) =>
                        setConfig({ ...config, app: { ...config.app, diagnostic_mode: e.target.checked } })
                      }
                    />
                    Registrar métricas de diagnóstico de velocidad
                  </label>
                </div>

                <h3 style={{ marginTop: '32px' }}>Diccionario de Reemplazo</h3>
                <div className="flex-row" style={{ marginBottom: '16px' }}>
                  <input
                    placeholder="Si digo..."
                    value={newDictKey}
                    onChange={(e) => setNewDictKey(e.target.value)}
                    style={{ flex: 1 }}
                  />
                  <input
                    placeholder="Escribir..."
                    value={newDictValue}
                    onChange={(e) => setNewDictValue(e.target.value)}
                    style={{ flex: 1 }}
                  />
                  <button onClick={addDictionaryItem}>Añadir regla</button>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '8px' }}>
                  {Object.entries(config.dictionary).map(([k, v]) => (
                    <div key={k} style={{ background: 'rgba(0,0,0,0.2)', padding: '8px 12px', borderRadius: '8px', display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--text-muted)' }}>{k}</span>
                      <span style={{ fontWeight: 600 }}>{v}</span>
                    </div>
                  ))}
                </div>

                <div style={{ marginTop: '32px', display: 'flex', justifyContent: 'flex-end' }}>
                  <button className="primary" onClick={onSave} style={{ padding: '10px 24px' }}>Guardar y Aplicar</button>
                </div>
              </div>
            )}

            {tab === "history" && (
              <div className="panel">
                <h3>Historial Reciente</h3>
                {historyItems.length === 0 ? (
                  <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '40px' }}>No hay dictados recientes</p>
                ) : (
                  <div className="history-list">
                    {historyItems.map((item, i) => (
                      <div className="history-item" key={i}>
                        <div className="history-ts">{item.ts}</div>
                        <div className="history-text">{item.text}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {tab === "metrics" && (
              <div className="panel">
                <h3>Rendimiento (Últimos {metrics.count} ciclos)</h3>
                {metrics.count === 0 ? (
                  <p style={{ color: 'var(--text-muted)' }}>Activa el modo diagnóstico y realiza algunos dictados para ver métricas.</p>
                ) : (
                  <div className="metric-grid">
                    <div className="metric-card">
                      <span className="metric-label">Tiempo Total</span>
                      <span className="metric-val">{metrics.avg_total_ms.toFixed(0)} <span style={{ fontSize: '0.6em' }}>ms</span></span>
                    </div>
                    <div className="metric-card">
                      <span className="metric-label">Inferencia STT</span>
                      <span className="metric-val">{metrics.avg_transcribe_ms.toFixed(0)} <span style={{ fontSize: '0.6em' }}>ms</span></span>
                    </div>
                    <div className="metric-card">
                      <span className="metric-label">Pegado OS</span>
                      <span className="metric-val">{metrics.avg_paste_ms.toFixed(0)} <span style={{ fontSize: '0.6em' }}>ms</span></span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
      {RESIZE_HANDLES.map(({ direction, className }) => (
        <div
          key={direction}
          className={`resize-handle ${className}`}
          onMouseDown={(event) => {
            event.preventDefault();
            event.stopPropagation();
            void handleResize(direction);
          }}
        />
      ))}
    </div>
  );
}
