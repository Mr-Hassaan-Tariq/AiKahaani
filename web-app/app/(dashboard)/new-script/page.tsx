import GenerateScriptForm from './_components/GenerateScriptForm';
import { getConfig } from './actions';
import Topbar from 'components/layout/Topbar';

export default async function NewScriptPage() {
  const { data, error, isError } = await getConfig();

  if (isError) {
    return (
      <div className="flex min-h-64 items-center justify-center">
        <p className="text-sm text-destructive">
          Failed to load configuration: {error?.message ?? 'Unknown error'}
        </p>
      </div>
    );
  }

  return (
    <>
      <Topbar
        title="Script Generator"
        subtitle="Describe your video and we'll build a complete script outline."
      />
      <div className="mx-auto max-w-3xl px-6 py-8">
        <GenerateScriptForm configData={data} />
      </div>
    </>
  );
}
