import { cn } from 'lib/utils';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';
import { Skeleton } from 'components/shadcn_ui/skeleton';

export default function NewScriptLoading() {
  return (
    <Col className="gap-8">
      {/* Header Skeleton */}
      <Col className="w-full items-center gap-3">
        <Skeleton className="h-8 w-48 lg:h-9 lg:w-56" /> {/* Title */}
        <Skeleton className="h-5 w-80 lg:h-6 lg:w-96" /> {/* Subtitle */}
      </Col>

      {/* Form Skeleton */}
      <Col className="gap-8">
        {/* Description Textarea Section */}
        <div className="relative">
          <Col className="gap-2">
            <Row className="justify-normal gap-2">
              <Skeleton className="h-5 w-40" /> {/* Label */}
              <Skeleton className="h-4 w-4 rounded-full" /> {/* Info icon */}
            </Row>
            <Skeleton className="h-32 w-full rounded-lg" /> {/* Textarea */}
          </Col>
          {/* Context Button Skeleton */}
          <div className="absolute bottom-3 right-3">
            <Skeleton className="h-10 w-32 rounded-full" />
          </div>
        </div>

        {/* Templates Widget Skeleton */}
        <Col className="gap-4">
          <Skeleton className="h-6 w-32" /> {/* Templates label */}
          {/* <Row className="flex-wrap gap-3">
            {Array.from({ length: 4 }).map((_, index) => (
              <Skeleton key={index} className="h-12 w-24 rounded-lg lg:h-14 lg:w-28" />
            ))}
          </Row> */}
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            {Array.from({ length: 4 }).map((_, i) => (
              <Skeleton
                key={i}
                className={cn('flex cursor-pointer flex-col gap-3 rounded-2xl bg-white/10 p-4')}
              >
                <Row>
                  <Skeleton className="h-5 w-24" /> {/* Template name */}
                  <Row className="gap-2 text-xs text-white">
                    <Skeleton className="h-4 w-16" /> {/* Duration */}
                    <Skeleton className="h-4 w-16" /> {/* Word range */}
                  </Row>
                </Row>
                <Skeleton className="h-4 w-full" /> {/* Description */}
              </Skeleton>
            ))}
          </div>
        </Col>

        {/* Slider Widget Skeleton */}
        <Col className="gap-4">
          <Skeleton className="h-6 w-24" /> {/* Length label */}
          <Col className="gap-2">
            <Skeleton className="h-2 w-full rounded-full" /> {/* Slider track */}
            <Row className="justify-between">
              <Skeleton className="h-4 w-16" /> {/* Min value */}
              <Skeleton className="h-4 w-16" /> {/* Max value */}
            </Row>
          </Col>
        </Col>

        {/* Vibe/Tone Widget Skeleton */}

        {/* Submit Button Skeleton */}
        <Skeleton className="h-12 w-full rounded-full lg:h-14" />
        <Skeleton className="h-12 w-full rounded-full lg:h-14" />
      </Col>
    </Col>
  );
}
