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
  uuid: string;
  title: string;
  outline_text: string;
  outline_data: OutlineDataType;
  section_order: number[];
  status: string;
  version: number;
  tokens_used: number;
  generation_time: number;
  created: string;
  modified: string;
}

export interface OutlineResponseType {
  outline: OutlineType;
  message: string;
  status: string;
}
