mod sidecar;

use serde::de::DeserializeOwned;
use serde::{Deserialize, Serialize};
use serde_json::json;
use sidecar::SidecarManager;
use std::sync::{Arc, Mutex};
use tauri::Manager;

struct AppState {
    sidecar: Arc<Mutex<SidecarManager>>,
}

#[derive(Serialize, Deserialize)]
struct ToggleResult {
    status: String,
    message: String,
    text: Option<String>,
}

async fn call_sidecar<T>(
    state: tauri::State<'_, AppState>,
    method: &'static str,
    params: serde_json::Value,
) -> Result<T, String>
where
    T: DeserializeOwned + Send + 'static,
{
    let sidecar = state.sidecar.clone();
    tauri::async_runtime::spawn_blocking(move || {
        let mut guard = sidecar.lock().map_err(|_| "lock sidecar".to_string())?;
        guard.request::<T>(method, params).map_err(|e| e.to_string())
    })
    .await
    .map_err(|e| format!("Error task sidecar: {e}"))?
}

#[tauri::command]
async fn init_app(state: tauri::State<'_, AppState>) -> Result<serde_json::Value, String> {
    call_sidecar::<serde_json::Value>(state, "load_app_state", json!({})).await
}

#[tauri::command]
async fn toggle_dictation(state: tauri::State<'_, AppState>) -> Result<ToggleResult, String> {
    call_sidecar::<ToggleResult>(state, "toggle_dictation", json!({})).await
}

#[tauri::command]
async fn save_settings(
    state: tauri::State<'_, AppState>,
    config: serde_json::Value,
) -> Result<serde_json::Value, String> {
    call_sidecar::<serde_json::Value>(state, "save_config", json!({ "config": config })).await
}

#[tauri::command]
async fn get_metrics(state: tauri::State<'_, AppState>, last_n: u32) -> Result<serde_json::Value, String> {
    call_sidecar::<serde_json::Value>(state, "get_recent_metrics", json!({ "last_n": last_n })).await
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_clipboard_manager::init())
        .setup(|app| {
            let mut manager = SidecarManager::new(app.handle().clone()).map_err(|e| {
                let msg = format!("No se pudo iniciar sidecar: {e}");
                std::io::Error::new(std::io::ErrorKind::Other, msg)
            })?;
            manager
                .request::<serde_json::Value>("health", json!({}))
                .map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, format!("Sidecar health failed: {e}")))?;
            app.manage(AppState {
                sidecar: Arc::new(Mutex::new(manager)),
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            init_app,
            toggle_dictation,
            save_settings,
            get_metrics,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
