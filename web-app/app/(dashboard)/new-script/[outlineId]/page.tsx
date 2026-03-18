import { getOutline } from './actions';
import OutlineComponent from './OutlineComponent';

export default async function Page({ params }: { params: Promise<{ outlineId: string }> }) {
  const { outlineId } = await params;

  const { data, error, isError } = await getOutline(outlineId);

  if (isError) {
    return (
      <div className="flex min-h-[300px] flex-col items-center justify-center gap-2 text-center">
        <p className="text-sm font-medium text-destructive">Failed to load outline</p>
        <p className="text-xs text-muted-foreground">{String((error as any)?.message ?? '')}</p>
      </div>
    );
  }

  return (
    <div className="p-7">
      <OutlineComponent outline={data} />
    </div>
  );
}
