import { ScriptFilters } from '../actions';

export type FiltersState = {
  lastEdited: string;
  wordCount: number[];
  videoDuration: string | null;
};

export function convertFiltersToAPI(filters: FiltersState): ScriptFilters {
  const apiFilters: ScriptFilters = {};

  // Handle ordering (last edited)
  if (filters.lastEdited === 'most_recent') {
    apiFilters.ordering = 'created';
  } else if (filters.lastEdited === 'oldest') {
    apiFilters.ordering = 'modified';
  }

  // Handle word count range
  if (filters.wordCount && filters.wordCount.length === 2) {
    const [min, max] = filters.wordCount;
    if (min > 0) apiFilters.word_count_min = min;
    if (max < 10000) apiFilters.word_count_max = max;
  }

  // Handle video duration
  if (filters.videoDuration) {
    const duration = filters.videoDuration;
    switch (duration) {
      case '<20':
        apiFilters.duration_max = 20;
        break;
      case '20':
        apiFilters.duration_min = 20;
        apiFilters.duration_max = 20;
        break;
      case '40':
        apiFilters.duration_min = 40;
        apiFilters.duration_max = 40;
        break;
      case '60':
        apiFilters.duration_min = 60;
        apiFilters.duration_max = 60;
        break;
      case '>60':
        apiFilters.duration_min = 60;
        break;
    }
  }

  return apiFilters;
}

export function convertURLParamsToFilters(searchParams: URLSearchParams): Partial<FiltersState> {
  const filters: Partial<FiltersState> = {};

  // Handle ordering
  const ordering = searchParams.get('ordering');
  if (ordering === 'created') {
    filters.lastEdited = 'most_recent';
  } else if (ordering === 'modified') {
    filters.lastEdited = 'oldest';
  }

  // Handle word count
  const wordCountMin = searchParams.get('word_count_min');
  const wordCountMax = searchParams.get('word_count_max');
  if (wordCountMin || wordCountMax) {
    const min = wordCountMin ? parseInt(wordCountMin) : 0;
    const max = wordCountMax ? parseInt(wordCountMax) : 10000;
    filters.wordCount = [min, max];
  }

  // Handle duration
  const durationMin = searchParams.get('duration_min');
  const durationMax = searchParams.get('duration_max');
  if (durationMin && durationMax) {
    const min = parseInt(durationMin);
    const max = parseInt(durationMax);
    if (min === max) {
      // Exact duration match
      if (min === 20) filters.videoDuration = '20';
      else if (min === 40) filters.videoDuration = '40';
      else if (min === 60) filters.videoDuration = '60';
    } else if (max === 20) {
      filters.videoDuration = '<20';
    } else if (min === 60) {
      filters.videoDuration = '>60';
    }
  }

  return filters;
}
