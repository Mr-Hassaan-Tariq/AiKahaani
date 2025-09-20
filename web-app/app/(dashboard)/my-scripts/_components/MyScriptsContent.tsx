import { getScriptGenerations, ScriptFilters } from '../actions';
import MyScriptsList from './MyScriptsList';
import MyScriptsTabWrapper from './MyScriptsTabWrapper';
import OutlinesPage from './OutlinesPage';
import ScriptsPage from './ScriptsPage';

interface MyScriptsContentProps {
  searchParams?: {
    query?: string;
    search?: string;
    ordering?: string;
    word_count_min?: string;
    word_count_max?: string;
    duration_min?: string;
    duration_max?: string;
  };
}

export default async function MyScriptsContent({ searchParams }: MyScriptsContentProps) {
  const query = searchParams?.query;
  const search = searchParams?.search;

  // Build filters object from search params
  const filters: ScriptFilters = {
    search,
    type: query === 'outlines' ? 'outline' : query === 'scripts' ? 'script' : undefined,
    ordering: searchParams?.ordering as 'created' | 'modified' | undefined,
    word_count_min: searchParams?.word_count_min
      ? parseInt(searchParams.word_count_min)
      : undefined,
    word_count_max: searchParams?.word_count_max
      ? parseInt(searchParams.word_count_max)
      : undefined,
    duration_min: searchParams?.duration_min ? parseInt(searchParams.duration_min) : undefined,
    duration_max: searchParams?.duration_max ? parseInt(searchParams.duration_max) : undefined,
  };

  // Fetch initial data server-side
  const { data: initialScripts, error, isError } = await getScriptGenerations(filters);

  // Render content based on query
  const renderContent = () => {
    if (query === 'outlines') {
      return <OutlinesPage initialScripts={initialScripts} />;
    }

    if (query === 'scripts') {
      return <ScriptsPage initialScripts={initialScripts} />;
    }

    return (
      <MyScriptsList
        initialScripts={initialScripts}
        error={error}
        isError={isError}
        searchQuery={search}
      />
    );
  };

  return <MyScriptsTabWrapper searchValue={search}>{renderContent()}</MyScriptsTabWrapper>;
}
