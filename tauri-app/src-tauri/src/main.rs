mod sidecar;

use serde::{Deserialize, Serialize};
use serde_json::json;
use sidecar::SidecarManager;
use std::sync::Mutex;
use tauri::Manager;

struct AppState {
    sidecar: Mutex<SidecarManager>,
}

#[derive(Serialize, Deserialize)]
struct ToggleResult {
    status: String,
    message: String,
    text: Option<String>,
}

#[tauri::command]
fn init_app(state: tauri::State<AppState>) -> Result<serde_json::Value, String> {
    let mut sidecar = state.sidecar.lock().map_err(|_| "lock sidecar".to_string())?;
    sidecar
        .request::<serde_json::Value>("load_app_state", json!({}))
        .map_err(|e| e.to_string())
}

#[tauri::command]
fn toggle_dictation(state: tauri::State<AppState>) -> Result<ToggleResult, String> {
    let mut sidecar = state.sidecar.lock().map_err(|_| "lock sidecar".to_string())?;
    sidecar
        .request::<ToggleResult>("toggle_dictation", json!({}))
        .map_err(|e| e.to_string())
}

#[tauri::command]
fn save_settings(state: tauri::State<AppState>, config: serde_json::Value) -> Result<serde_json::Value, String> {
    let mut sidecar = state.sidecar.lock().map_err(|_| "lock sidecar".to_string())?;
    sidecar
        .request::<serde_json::Value>("save_config", json!({ "config": config }))
        .map_err(|e| e.to_string())
}

#[tauri::command]
fn set_hotkey(state: tauri::State<AppState>, hotkey: String) -> Result<serde_json::Value, String> {
    let mut sidecar = state.sidecar.lock().map_err(|_| "lock sidecar".to_string())?;
    sidecar
        .request::<serde_json::Value>("set_hotkey", json!({ "hotkey": hotkey }))
        .map_err(|e| e.to_string())
}

#[tauri::command]
fn get_history(state: tauri::State<AppState>, limit: u32) -> Result<serde_json::Value, String> {
    let mut sidecar = state.sidecar.lock().map_err(|_| "lock sidecar".to_string())?;
    sidecar
        .request::<serde_json::Value>("get_history", json!({ "limit": limit }))
        .map_err(|e| e.to_string())
}

#[tauri::command]
fn get_metrics(state: tauri::State<AppState>, last_n: u32) -> Result<serde_json::Value, String> {
    let mut sidecar = state.sidecar.lock().map_err(|_| "lock sidecar".to_string())?;
    sidecar
        .request::<serde_json::Value>("get_recent_metrics", json!({ "last_n": last_n }))
        .map_err(|e| e.to_string())
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            let manager = SidecarManager::new(app.handle().clone()).map_err(|e| {
                let msg = format!("No se pudo iniciar sidecar: {e}");
                std::io::Error::new(std::io::ErrorKind::Other, msg)
            })?;
            app.manage(AppState {
                sidecar: Mutex::new(manager),
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            init_app,
            toggle_dictation,
            save_settings,
            set_hotkey,
            get_history,
            get_metrics,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
