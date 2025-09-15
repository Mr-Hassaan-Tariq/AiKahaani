'use client';

import { useSearchParams } from 'next/navigation';
import ComponentNav from '@/(dashboard)/_components/ComponentNav';

import { Magicpan } from './_components/components';
import OutlinesPage from './_components/OutlinesPage';
import ScriptList from './_components/ScriptList';
import ScriptsPage from './_components/ScriptsPage';
import ScriptsTab from './_components/ScriptsTab';
import { MOCK_SCRIPTS } from './_constants';
import { useScripts } from './_hooks/useScripts';

export default function HomePage() {
  const searchParams = useSearchParams();
  const query = searchParams.get('query');

  // Initialize scripts hook
  const { filteredScripts, searchQuery, actions, loading, error, setSearchQuery } = useScripts({
    initialScripts: MOCK_SCRIPTS,
    onScriptUpdate: (updatedScripts) => {
      console.log('Scripts updated:', updatedScripts);
    },
  });

  // Handle search
  const handleSearch = (searchQuery: string) => {
    setSearchQuery(searchQuery);
  };

  // Handle filter changes
  const handleFilter = () => {
    console.log('Filter clicked');
    // TODO: Implement filter modal
  };

  // Handle create actions
  const handleCreateScript = () => {
    console.log('Create script');
    // TODO: Implement create script functionality
  };

  // Render content based on query
  const renderContent = () => {
    if (query === 'outlines') {
      return <OutlinesPage />;
    }

    if (query === 'scripts') {
      return <ScriptsPage />;
    }

    return (
      <ScriptList
        scripts={filteredScripts}
        actions={actions}
        loading={loading}
        emptyState={
          searchQuery ? (
            <div className="py-12 text-center">
              <div className="mb-4 text-6xl">🔍</div>
              <h3 className="mb-2 text-xl font-semibold text-white">
                No scripts found for {searchQuery}
              </h3>
              <p className="text-gray-400">
                Try adjusting your search terms or create a new script.
              </p>
            </div>
          ) : undefined
        }
      />
    );
  };

  return (
    <div className="space-y-6">
      <ComponentNav
        title="My Scripts"
        buttonText="Generate New Script"
        buttonIcon={Magicpan}
        buttonClassName="lg:max-w-[240px]"
        _onButtonClick={handleCreateScript}
      />

      {error && (
        <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-4">
          <p className="text-red-400">Error: {error}</p>
        </div>
      )}

      <ScriptsTab onSearch={handleSearch} onFilter={handleFilter} searchValue={searchQuery}>
        {renderContent()}
      </ScriptsTab>
    </div>
  );
}
