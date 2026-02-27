use anyhow::{anyhow, Context, Result};
use serde::de::DeserializeOwned;
use serde_json::{json, Value};
use std::collections::HashMap;
use std::io::{BufRead, BufReader, Write};
use std::path::{Path, PathBuf};
use std::process::{Child, ChildStdin, Command, Stdio};
use std::sync::mpsc::{self, Receiver, Sender};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use tauri::{AppHandle, Emitter};
use uuid::Uuid;

struct PendingResponse {
    tx: Sender<Value>,
}

pub struct SidecarManager {
    _child: Child,
    stdin: ChildStdin,
    pending: Arc<Mutex<HashMap<String, PendingResponse>>>,
}

impl SidecarManager {
    fn resolve_python_executable(repo_root: &Path) -> (String, Vec<String>) {
        let venv_windows = repo_root.join(".venv").join("Scripts").join("python.exe");
        if venv_windows.exists() {
            return (venv_windows.to_string_lossy().to_string(), vec![]);
        }

        let venv_unix = repo_root.join(".venv").join("bin").join("python");
        if venv_unix.exists() {
            return (venv_unix.to_string_lossy().to_string(), vec![]);
        }

        ("python".to_string(), vec![])
    }

    pub fn new(app: AppHandle) -> Result<Self> {
        let repo_root: PathBuf = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("..")
            .join("..");
        let sidecar_path = repo_root.join("python_backend.py");

        if !sidecar_path.exists() {
            return Err(anyhow!("No se encontro python_backend.py en {}", sidecar_path.display()));
        }

        let (python_exec, python_args) = Self::resolve_python_executable(&repo_root);
        let mut cmd = Command::new(&python_exec);
        cmd.args(python_args)
            .arg(&sidecar_path)
            .current_dir(&repo_root)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped());
        let mut child = cmd.spawn().with_context(|| {
            format!(
                "No se pudo iniciar sidecar Python (exec: {}, script: {})",
                python_exec,
                sidecar_path.display()
            )
        })?;

        let stdin = child.stdin.take().context("No stdin sidecar")?;
        let stdout = child.stdout.take().context("No stdout sidecar")?;
        let stderr = child.stderr.take().context("No stderr sidecar")?;

        let pending: Arc<Mutex<HashMap<String, PendingResponse>>> = Arc::new(Mutex::new(HashMap::new()));
        let pending_clone = Arc::clone(&pending);
        let app_for_events = app.clone();

        thread::spawn(move || {
            let reader = BufReader::new(stdout);
            for line in reader.lines() {
                let Ok(raw_line) = line else {
                    continue;
                };
                let parsed: Value = match serde_json::from_str(&raw_line) {
                    Ok(v) => v,
                    Err(_) => continue,
                };

                if let Some(event_name) = parsed.get("event").and_then(|v| v.as_str()) {
                    let payload = parsed.get("payload").cloned().unwrap_or_else(|| json!({}));
                    let _ = app_for_events.emit(event_name, payload);
                    continue;
                }

                if let Some(id) = parsed.get("id").and_then(|v| v.as_str()) {
                    if let Ok(mut table) = pending_clone.lock() {
                        if let Some(waiter) = table.remove(id) {
                            let _ = waiter.tx.send(parsed);
                        }
                    }
                }
            }
        });

        thread::spawn(move || {
            let reader = BufReader::new(stderr);
            for line in reader.lines() {
                if let Ok(row) = line {
                    eprintln!("[python-sidecar] {row}");
                }
            }
        });

        Ok(Self {
            _child: child,
            stdin,
            pending,
        })
    }

    pub fn request<T: DeserializeOwned>(&mut self, method: &str, params: Value) -> Result<T> {
        let id = Uuid::new_v4().to_string();
        let payload = json!({
            "id": id,
            "method": method,
            "params": params,
        });

        let (tx, rx): (Sender<Value>, Receiver<Value>) = mpsc::channel();
        {
            let mut table = self.pending.lock().map_err(|_| anyhow!("lock pending"))?;
            table.insert(id.clone(), PendingResponse { tx });
        }

        self.stdin
            .write_all(format!("{}\n", payload).as_bytes())
            .context("No se pudo escribir request")?;
        self.stdin.flush().context("No se pudo flush request")?;

        let response = rx
            .recv_timeout(Duration::from_secs(90))
            .context("Timeout esperando respuesta sidecar")?;

        let ok = response.get("ok").and_then(|v| v.as_bool()).unwrap_or(false);
        if !ok {
            let message = response
                .get("error")
                .and_then(|v| v.get("message"))
                .and_then(|v| v.as_str())
                .unwrap_or("Error sidecar");
            return Err(anyhow!(message.to_string()));
        }

        let result = response.get("result").cloned().unwrap_or(Value::Null);
        serde_json::from_value(result).context("No se pudo deserializar resultado")
    }
}
