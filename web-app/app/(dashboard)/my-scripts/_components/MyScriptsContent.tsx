import PaginationClient from '../../../../components/common/PaginationClient';
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
    page?: string;
    limit?: string;
  };
}

export default async function MyScriptsContent({ searchParams }: MyScriptsContentProps) {
  const query = searchParams?.query;
  const search = searchParams?.search;

  const currentPage = searchParams?.page ? parseInt(searchParams.page) : 1;
  const pageSize = searchParams?.limit ? parseInt(searchParams.limit) : 12;

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
    limit: pageSize,
    offset: (currentPage - 1) * pageSize,
  };

  // Fetch initial data server-side
  const { data: initialScripts, error, isError } = await getScriptGenerations(filters);

  // Render content based on query
  const renderContent = () => {
    if (query === 'outlines') {
      return <OutlinesPage initialScripts={initialScripts?.results} />;
    }

    if (query === 'scripts') {
      return <ScriptsPage initialScripts={initialScripts?.results} />;
    }

    return (
      <MyScriptsList
        initialScripts={initialScripts?.results}
        error={error}
        isError={isError}
        searchQuery={search}
      />
    );
  };

  return (
    <div className="flex flex-col">
      <MyScriptsTabWrapper searchValue={search}>{renderContent()}</MyScriptsTabWrapper>
      <PaginationClient
        currentPage={currentPage}
        totalCount={initialScripts?.count || 0}
        pageSize={pageSize}
        searchParams={searchParams}
      />
    </div>
  );
}
