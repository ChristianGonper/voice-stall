import { invoke } from "@tauri-apps/api/core";
import type { AppStateDto, FullConfig, MetricsSummary, ToggleResult } from "./types";

export const initApp = () => invoke<AppStateDto>("init_app");

export const toggleDictation = () => invoke<ToggleResult>("toggle_dictation");

export const saveSettings = (config: FullConfig) =>
  invoke<{ ok: boolean }>("save_settings", { config });

export const getMetrics = (lastN = 5) =>
  invoke<MetricsSummary>("get_metrics", { lastN });
