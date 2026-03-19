export interface ToneType {
  id: number;
  name: string;
}

export interface TemplateStyleType {
  id: number;
  name: string;
  min_length: number;
  max_length: number;
  duration: number;
  description: string;
  word_range: string;
}

export interface LengthRangeType {
  min: number;
  max: number;
  default: number;
}

export interface GenerationPromptType {
  tones: ToneType[];
  template_styles: TemplateStyleType[];
  length_range: LengthRangeType;
}
export interface FormType {
  description: string;
  tones: number[];
  template_style?: number;
  min_length: number;
  max_length: number;
  title: string;
  youtube_url?: string | string[];
  article_url?: string | string[];
  image?: File | File[];
}
export interface OutlineSectionType {
  title: string;
  description: string;
  key_points: string[];
  timing: string;
  transition: string;
}

interface OutlineDataType {
  sections: OutlineSectionType[];
}

export interface OutlineType {
  id: string;
  title: string;
  outline_text: string;
  outline_data: OutlineDataType;
  section_order: number[];
  status: string;
  openai_model?: string;
  tokens_used: number;
  generation_time: number;
  tones: ToneType[];
  created_at: string;
  updated_at: string;
  // Optional fields stored client-side (not returned by backend)
  description?: string;
  template_style?: number;
  min_length?: number;
  max_length?: number;
}

export interface GeneratedOutlineType {
  id: string;
  title: string;
  outline_text: string;
  outline_data: OutlineDataType;
  section_order: number[];
  status: string;
  openai_model: string;
  tokens_used: number;
  generation_time: number;
  tones: ToneType[];
  created_at: string;
  updated_at: string;
}

export interface OutlineMetadataType {
  tokens_used: number;
  generation_time: number;
  model_used: string;
  method: string;
  sections_generated: number;
}

export interface OutlineResponseType {
  outline: GeneratedOutlineType;
  metadata: OutlineMetadataType;
  is_script_allowed: boolean;
}
