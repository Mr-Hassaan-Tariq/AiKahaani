import Col from 'components/ui/Col';
import Row from 'components/ui/Row';
import { Skeleton } from 'components/shadcn_ui/skeleton';

export default function TitleGeneratorSkeleton() {
  return (
    // Outer Container matching the card's dimensions and padding
    <div className="mx-auto w-full max-w-[864px] rounded-xl bg-neutral-800 p-8 font-sans shadow-2xl">
      <Col className="gap-8">
        {/* --- Header Skeleton --- */}
        <Col className="mb-2 w-full items-center gap-1">
          <Skeleton className="h-8 w-48" /> {/* Title */}
          <Skeleton className="h-4 w-64" /> {/* Subtitle */}
        </Col>
        {/* --- Generate/Optimize Tabs Skeleton --- */}
        <Row className="mb-4 justify-center space-x-4">
          <Skeleton className="h-10 w-32 rounded-full" /> {/* 'Generate New' button */}
          <Skeleton className="h-10 w-36 rounded-full" /> {/* 'Optimize Existing' button */}
        </Row>
        {/* --- Main Input Section Skeleton --- */}
        <Col className="mb-2 gap-2">
          <Row className="justify-normal gap-2">
            <Skeleton className="h-5 w-40" /> {/* Label */}
            <Skeleton className="h-4 w-4 rounded-full" /> {/* Info icon */}
          </Row>
          {/* Input field area */}
          <Skeleton className="h-24 w-full rounded-lg" />
        </Col>
        {/* --- Tone / Style Section Skeleton --- */}
        <Col className="gap-4">
          <Row className="items-center justify-between">
            <Row className="justify-normal gap-2">
              <Skeleton className="h-5 w-20" /> {/* 'Tone / Style' label */}
              <Skeleton className="h-4 w-4 rounded-full" /> {/* Info icon */}
            </Row>
            <Skeleton className="h-4 w-40" /> {/* 'Recommended for your niche' text */}
          </Row>

          {/* Tone/Style Buttons Skeleton */}
          <Row className="flex-wrap gap-2">
            {/* Generate 8 button placeholders */}
            {Array.from({ length: 8 }).map((_, index) => (
              <Skeleton key={index} className="h-8 w-24 rounded-full" />
            ))}
          </Row>
        </Col>
        {/* --- Generate Button Skeleton --- */}
        <Skeleton className="h-12 w-full rounded-xl" /> {/* 'Generate Title' button */}
      </Col>
    </div>
  );
}
