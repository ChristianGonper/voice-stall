import { invoke } from "@tauri-apps/api/core";
import type { AppStateDto, FullConfig, MetricsSummary, ToggleResult } from "./types";

export const initApp = () => invoke<AppStateDto>("init_app");

export const toggleDictation = () => invoke<ToggleResult>("toggle_dictation");

export const saveSettings = (config: FullConfig) =>
  invoke<{ ok: boolean }>("save_settings", { config });

export const setHotkey = (hotkey: string) =>
  invoke<{ ok: boolean; hotkey: string }>("set_hotkey", { hotkey });

export const getMetrics = (lastN = 5) =>
  invoke<MetricsSummary>("get_metrics", { lastN });

export const getHistory = (limit = 10) =>
  invoke("get_history", { limit });
