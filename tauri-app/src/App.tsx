import { useEffect, useMemo, useState } from "react";
import { listen } from "@tauri-apps/api/event";
import { getMetrics, initApp, saveSettings, setHotkey, toggleDictation } from "./api";
import type { AppStateDto, FullConfig, MetricsSummary, StatusEvent } from "./types";

type TabKey = "control" | "settings" | "history" | "metrics";

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

function statusTone(status: string): "idle" | "recording" | "processing" | "error" {
  if (status === "recording") {
    return "recording";
  }
  if (status === "processing" || status === "loading") {
    return "processing";
  }
  if (status === "error") {
    return "error";
  }
  return "idle";
}

function WaveBars({ status }: { status: string }) {
  const tone = statusTone(status);
  const bars = Array.from({ length: 12 });
  return (
    <div className={`wave wave-${tone}`}>
      {bars.map((_, index) => (
        <span
          key={index}
          className="wave-bar"
          style={{ animationDelay: `${index * 0.08}s` }}
        />
      ))}
    </div>
  );
}

function StatusOverlay({
  visible,
  status,
  statusMessage,
}: {
  visible: boolean;
  status: string;
  statusMessage: string;
}) {
  if (!visible) {
    return null;
  }

  return (
    <div className={`overlay overlay-${statusTone(status)}`}>
      <div className="overlay-head">
        <span className="dot" />
        <strong>{STATUS_LABELS[status] ?? status.toUpperCase()}</strong>
      </div>
      <WaveBars status={status} />
      <div className="overlay-msg">{statusMessage}</div>
    </div>
  );
}

export function App() {
  const [ready, setReady] = useState(false);
  const [bootError, setBootError] = useState<string | null>(null);
  const [status, setStatus] = useState("loading");
  const [statusMessage, setStatusMessage] = useState("Cargando motor...");
  const [config, setConfig] = useState<FullConfig | null>(null);
  const [historyText, setHistoryText] = useState<string[]>([]);
  const [metrics, setMetrics] = useState<MetricsSummary>(EMPTY_METRICS);
  const [newDictKey, setNewDictKey] = useState("");
  const [newDictValue, setNewDictValue] = useState("");
  const [tab, setTab] = useState<TabKey>("control");
  const [miniMode, setMiniMode] = useState(false);
  const [showOverlay, setShowOverlay] = useState(true);
  const [isCompactViewport, setIsCompactViewport] = useState(false);

  const loadInitialState = async () => {
    const state: AppStateDto = await initApp();
    setConfig(state.config);
    setMetrics(state.metrics);
    setHistoryText(state.history.map((h) => `${h.ts}\n${h.text}`));
    setStatus(state.status);
    setStatusMessage("Listo para dictar");
    setBootError(null);
    setReady(true);
  };

  useEffect(() => {
    let unlistenStatus: (() => void) | undefined;
    let unlistenDiag: (() => void) | undefined;

    const setup = async () => {
      unlistenStatus = await listen<StatusEvent>("status", (ev) => {
        setStatus(ev.payload.state);
        setStatusMessage(ev.payload.message);
      });
      unlistenDiag = await listen("diag", async () => {
        const m = await getMetrics(5);
        setMetrics(m);
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
      if (unlistenStatus) {
        unlistenStatus();
      }
      if (unlistenDiag) {
        unlistenDiag();
      }
    };
  }, []);

  useEffect(() => {
    const updateViewportFlag = () => {
      setIsCompactViewport(window.innerWidth < 1080 || window.innerHeight < 760);
    };
    updateViewportFlag();
    window.addEventListener("resize", updateViewportFlag);
    return () => window.removeEventListener("resize", updateViewportFlag);
  }, []);

  const hotkeyLabel = useMemo(() => {
    const value = config?.app.hotkey ?? "ctrl+alt+s";
    return value
      .split("+")
      .map((x) => x.toUpperCase())
      .join(" + ");
  }, [config]);

  const onToggle = async () => {
    try {
      const result = await toggleDictation();
      setStatus(result.status);
      setStatusMessage(result.message);
      if (result.text) {
        const entry = `${new Date().toISOString()}\n${result.text}`;
        setHistoryText((prev) => [entry, ...prev].slice(0, 20));
      }
      const updatedMetrics = await getMetrics(5);
      setMetrics(updatedMetrics);
    } catch (err) {
      setStatus("error");
      setStatusMessage(`Error dictado: ${String(err)}`);
    }
  };

  const onSave = async () => {
    if (!config) {
      return;
    }
    await saveSettings(config);
    const hotkeyResult = await setHotkey(config.app.hotkey);
    setStatus("idle");
    setStatusMessage(`Configuracion aplicada (${hotkeyResult.hotkey})`);
  };

  const addDictionaryItem = () => {
    if (!config) {
      return;
    }
    const key = newDictKey.trim().toLowerCase();
    const value = newDictValue.trim();
    if (!key || !value) {
      return;
    }
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

  if (!ready) {
    return <div className="shell">Cargando...</div>;
  }

  if (bootError || !config) {
    return (
      <div className="shell">
        <div className="app-card">
          <h2 style={{ marginTop: 0 }}>Voice Stall Tauri</h2>
          <p style={{ color: "#ffb8b8" }}>Error de inicializacion: {bootError ?? "No se pudo cargar estado"}</p>
          <div className="row">
            <button
              className="primary"
              onClick={() => {
                setReady(false);
                setStatus("loading");
                setStatusMessage("Reintentando...");
                loadInitialState().catch((err) => {
                  setStatus("error");
                  setStatusMessage(`Error init: ${String(err)}`);
                  setBootError(String(err));
                  setReady(true);
                });
              }}
            >
              Reintentar
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="shell">
      {miniMode ? (
        <div className="mini-card">
          <div className="row between">
            <strong>Voice Stall</strong>
            <span className={`state state-${statusTone(status)}`}>{STATUS_LABELS[status] ?? status.toUpperCase()}</span>
          </div>
          <div className="mini-message">{statusMessage}</div>
          <WaveBars status={status} />
          <div className="row between">
            <button className="primary" onClick={onToggle}>
              {status === "recording" ? "Detener" : "Dictar"}
            </button>
            <button onClick={() => setMiniMode(false)}>Expandir</button>
          </div>
          <div className="mini-hotkey">Hotkey: {hotkeyLabel}</div>
        </div>
      ) : (
        <div className="app-card">
          <div className="row between">
            <div>
              <h2 style={{ margin: 0 }}>Voice Stall Tauri</h2>
              <div className="sub">Estado visible y control rapido de dictado</div>
            </div>
            <span className={`state state-${statusTone(status)}`}>{STATUS_LABELS[status] ?? status.toUpperCase()}</span>
          </div>

          <div className="toolbar">
            <button className="primary" onClick={onToggle}>
              {status === "recording" ? "Detener dictado" : "Iniciar dictado"}
            </button>
            <button onClick={() => setMiniMode(true)}>Modo mini</button>
            <label className="row compact">
              <input type="checkbox" checked={showOverlay} onChange={(e) => setShowOverlay(e.target.checked)} />
              Overlay activo
            </label>
            {isCompactViewport && <span className="compact-hint">Overlay oculto en vista compacta</span>}
            <span className="hotkey-badge">{hotkeyLabel}</span>
          </div>

          <div className="panel hero">
            <div className="hero-text">{statusMessage}</div>
            <WaveBars status={status} />
          </div>

          <div className="tabs">
            <button className={tab === "control" ? "tab active" : "tab"} onClick={() => setTab("control")}>Control</button>
            <button className={tab === "settings" ? "tab active" : "tab"} onClick={() => setTab("settings")}>Ajustes</button>
            <button className={tab === "history" ? "tab active" : "tab"} onClick={() => setTab("history")}>Historial</button>
            <button className={tab === "metrics" ? "tab active" : "tab"} onClick={() => setTab("metrics")}>Metricas</button>
          </div>

          {tab === "control" && (
            <div className="panel">
              <h3>Control rapido</h3>
              <p>La app puede quedarse en modo mini para no ocupar espacio y seguir mostrando estado.</p>
              <div className="row">
                <button className="primary" onClick={onToggle}>
                  {status === "recording" ? "Detener dictado" : "Iniciar dictado"}
                </button>
                <button onClick={() => setMiniMode(true)}>Pasar a modo mini</button>
              </div>
            </div>
          )}

          {tab === "settings" && (
            <div className="panel">
              <h3>Ajustes</h3>
              <div className="grid-2">
                <label>
                  Hotkey
                  <input
                    value={config.app.hotkey}
                    onChange={(e) => setConfig({ ...config, app: { ...config.app, hotkey: e.target.value } })}
                  />
                </label>
                <label>
                  Historial
                  <input
                    type="number"
                    min={1}
                    max={20}
                    value={config.app.history_limit}
                    onChange={(e) =>
                      setConfig({ ...config, app: { ...config.app, history_limit: Number(e.target.value) || 5 } })
                    }
                  />
                </label>
                <label>
                  Modelo
                  <select
                    value={config.engine.model_size}
                    onChange={(e) => setConfig({ ...config, engine: { ...config.engine, model_size: e.target.value } })}
                  >
                    <option value="large-v3-turbo">large-v3-turbo</option>
                    <option value="base">base</option>
                  </select>
                </label>
                <label>
                  Idioma
                  <select
                    value={config.engine.language}
                    onChange={(e) => setConfig({ ...config, engine: { ...config.engine, language: e.target.value } })}
                  >
                    <option value="auto">auto</option>
                    <option value="es">es</option>
                    <option value="en">en</option>
                  </select>
                </label>
                <label>
                  Perfil
                  <select
                    value={config.engine.profile}
                    onChange={(e) => setConfig({ ...config, engine: { ...config.engine, profile: e.target.value } })}
                  >
                    <option value="fast">fast</option>
                    <option value="balanced">balanced</option>
                    <option value="accurate">accurate</option>
                  </select>
                </label>
                <label className="row compact">
                  <input
                    type="checkbox"
                    checked={config.app.diagnostic_mode}
                    onChange={(e) =>
                      setConfig({ ...config, app: { ...config.app, diagnostic_mode: e.target.checked } })
                    }
                  />
                  Diagnostico
                </label>
              </div>

              <div className="panel nested">
                <h4>Diccionario</h4>
                <div className="row">
                  <input
                    placeholder="Si digo..."
                    value={newDictKey}
                    onChange={(e) => setNewDictKey(e.target.value)}
                  />
                  <input
                    placeholder="Escribir..."
                    value={newDictValue}
                    onChange={(e) => setNewDictValue(e.target.value)}
                  />
                  <button onClick={addDictionaryItem}>Anadir</button>
                </div>
                <div className="list small">
                  {Object.entries(config.dictionary).map(([k, v]) => (
                    <div key={k}>
                      {k} -&gt; {v}
                    </div>
                  ))}
                </div>
              </div>

              <button className="primary" onClick={onSave}>Guardar configuracion</button>
            </div>
          )}

          {tab === "history" && (
            <div className="panel">
              <h3>Historial</h3>
              <div className="list">{historyText.join("\n\n") || "Sin historial"}</div>
            </div>
          )}

          {tab === "metrics" && (
            <div className="panel">
              <h3>Metricas</h3>
              <div className="metric-grid">
                <div className="metric-box"><span>Ciclos</span><strong>{metrics.count}</strong></div>
                <div className="metric-box"><span>Total</span><strong>{metrics.avg_total_ms.toFixed(1)} ms</strong></div>
                <div className="metric-box"><span>STT</span><strong>{metrics.avg_transcribe_ms.toFixed(1)} ms</strong></div>
                <div className="metric-box"><span>Pegado</span><strong>{metrics.avg_paste_ms.toFixed(1)} ms</strong></div>
              </div>
            </div>
          )}
        </div>
      )}

      <StatusOverlay
        visible={showOverlay && !miniMode && !isCompactViewport}
        status={status}
        statusMessage={statusMessage}
      />
    </div>
  );
}
