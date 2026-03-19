export interface ScriptSectionType {
  title: string;
  timeRange?: string;
  content: string;
}

export interface ScriptType {
  id: string;
  title: string;
  content: string;
  sections: Record<string, any>[];
  word_count: number;
  estimated_duration: number;
  status: string;
  openai_model?: string;
  tokens_used: number;
  generation_time: number;
  outline_id: string;
  created_at: string;
  updated_at: string;
}

export interface GenerateScriptType {
  script: ScriptType;
  metadata: Record<string, any>;
}
