import Row from 'components/ui/Row';

export default function Tabs({
  activeTab,
  setActiveTab,
  isGenerating,
}: {
  activeTab: 'generate' | 'optimize';
  setActiveTab: (tab: 'generate' | 'optimize') => void;
  isGenerating: boolean;
}) {
  return (
    <Row className="mt-1 flex w-full flex-col gap-2 sm:flex-row sm:justify-center">
      {['generate', 'optimize'].map((tab) => (
        <button
          key={tab}
          disabled={isGenerating}
          onClick={() => setActiveTab(tab as 'generate' | 'optimize')}
          className={`w-full rounded-[100px] px-[24px] py-[18px] font-bold transition-colors sm:w-auto ${
            activeTab === tab ? 'bg-white text-black' : 'bg-[#2B2B2B] text-white'
          } ${isGenerating ? 'cursor-not-allowed opacity-50' : ''}`}
        >
          {tab === 'generate' ? 'Generate New' : 'Optimize Existing'}
        </button>
      ))}
    </Row>
  );
}
