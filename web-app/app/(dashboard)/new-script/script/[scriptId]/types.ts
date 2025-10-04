export interface ScriptSectionType {
  title: string;
  timeRange?: string;
  content: string;
}

export interface ScriptType {
  uuid: string;
  title: string;
  content: string;
  sections: ScriptSectionType[];
  word_count: number;
  estimated_duration: number;
  status: string;
  version: number;
  is_published: boolean;
  tokens_used: number;
  generation_time: number;
  outline_title: string;
  created: string;
  modified: string;
}

export interface GenerateScriptType {
  script: ScriptType;
  message: string;
}
