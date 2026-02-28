export type DictEntry = Record<string, string>;

export type EngineConfig = {
  model_size: string;
  language: string;
  compute_type: string;
  initial_prompt: string;
  profile: string;
};

export type AppConfig = {
  hotkey: string;
  history_limit: number;
  timing_log_max_kb: number;
  diagnostic_mode: boolean;
};

export type FullConfig = {
  config_version: number;
  engine: EngineConfig;
  app: AppConfig;
  dictionary: DictEntry;
};

export type HistoryEntry = {
  ts: string;
  text: string;
};

export type MetricsSummary = {
  count: number;
  avg_total_ms: number;
  avg_transcribe_ms: number;
  avg_paste_ms: number;
};

export type AppStateDto = {
  config: FullConfig;
  history: HistoryEntry[];
  metrics: MetricsSummary;
  status: string;
  status_message: string;
};

export type ToggleResult = {
  status: string;
  message: string;
  text?: string;
};

export type StatusEvent = {
  state: string;
  message: string;
};
