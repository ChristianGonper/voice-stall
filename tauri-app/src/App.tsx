import { useEffect, useMemo, useState } from "react";
import { listen } from "@tauri-apps/api/event";
import { getMetrics, initApp, saveSettings, setHotkey, toggleDictation } from "./api";
import type { AppStateDto, FullConfig, MetricsSummary, StatusEvent } from "./types";

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
    return <div className="app">Cargando...</div>;
  }

  if (bootError || !config) {
    return (
      <div className="app">
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
    );
  }

  return (
    <div className="app">
      <div className="row">
        <h2 style={{ margin: 0 }}>Voice Stall Tauri</h2>
        <span className="state">{STATUS_LABELS[status] ?? status.toUpperCase()}</span>
      </div>
      <p>{statusMessage}</p>
      <p>Hotkey: {hotkeyLabel}</p>
      <div className="row">
        <button className="primary" onClick={onToggle}>
          {status === "recording" ? "Detener dictado" : "Iniciar dictado"}
        </button>
      </div>

      <div className="panel">
        <h3>Ajustes</h3>
        <div className="row">
          <label>Hotkey</label>
          <input
            value={config.app.hotkey}
            onChange={(e) => setConfig({ ...config, app: { ...config.app, hotkey: e.target.value } })}
          />
          <label>Modelo</label>
          <select
            value={config.engine.model_size}
            onChange={(e) => setConfig({ ...config, engine: { ...config.engine, model_size: e.target.value } })}
          >
            <option value="large-v3-turbo">large-v3-turbo</option>
            <option value="base">base</option>
          </select>
          <label>Idioma</label>
          <select
            value={config.engine.language}
            onChange={(e) => setConfig({ ...config, engine: { ...config.engine, language: e.target.value } })}
          >
            <option value="auto">auto</option>
            <option value="es">es</option>
            <option value="en">en</option>
          </select>
        </div>
        <div className="row">
          <label>Perfil</label>
          <select
            value={config.engine.profile}
            onChange={(e) => setConfig({ ...config, engine: { ...config.engine, profile: e.target.value } })}
          >
            <option value="fast">fast</option>
            <option value="balanced">balanced</option>
            <option value="accurate">accurate</option>
          </select>
          <label>Historial</label>
          <input
            type="number"
            min={1}
            max={20}
            value={config.app.history_limit}
            onChange={(e) =>
              setConfig({ ...config, app: { ...config.app, history_limit: Number(e.target.value) || 5 } })
            }
          />
          <label>
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

        <div className="panel">
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
          <div className="list">
            {Object.entries(config.dictionary).map(([k, v]) => (
              <div key={k}>
                {k} -&gt; {v}
              </div>
            ))}
          </div>
        </div>

        <button onClick={onSave}>Guardar configuracion</button>
      </div>

      <div className="panel">
        <h3>Metricas</h3>
        <div>Ciclos: {metrics.count}</div>
        <div>Total: {metrics.avg_total_ms.toFixed(1)} ms</div>
        <div>STT: {metrics.avg_transcribe_ms.toFixed(1)} ms</div>
        <div>Pegado: {metrics.avg_paste_ms.toFixed(1)} ms</div>
      </div>

      <div className="panel">
        <h3>Historial</h3>
        <div className="list">{historyText.join("\n\n") || "Sin historial"}</div>
      </div>
    </div>
  );
}
