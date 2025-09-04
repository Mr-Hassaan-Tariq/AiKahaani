import Card from 'components/ui/Card';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';
import { Skeleton } from 'components/shadcn_ui/skeleton';

export default function Loading() {
  return (
    <Col className="gap-10 text-white">
      {/* Profile Photo Card Skeleton */}
      <Card>
        <Col className="gap-6 lg:gap-8">
          {/* Title skeleton */}
          <Skeleton className="h-6 w-32 lg:h-7 lg:w-40" />

          <Row className="flex-col justify-normal gap-6 md:flex-row">
            {/* Profile image skeleton */}
            <Skeleton className="h-[120px] w-[120px] rounded-full" />

            <Col className="gap-6">
              <Col className="gap-3">
                {/* Recommendation text skeletons */}
                <Row className="justify-normal gap-2">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-4 w-20" />
                </Row>
                <Row className="justify-normal gap-2">
                  <Skeleton className="h-4 w-36" />
                  <Skeleton className="h-4 w-48" />
                </Row>
              </Col>
              {/* Button skeletons */}
              <Row className="justify-center gap-4 lg:justify-normal">
                <Skeleton className="h-10 w-32 rounded-md" />
                <Skeleton className="h-10 w-36 rounded-md" />
              </Row>
            </Col>
          </Row>
        </Col>
      </Card>

      {/* Profile Details Card Skeleton */}
      <Card>
        <Col className="gap-6 lg:gap-8">
          {/* Title skeleton */}
          <Skeleton className="h-6 w-36 lg:h-7 lg:w-44" />

          {/* First row of form inputs */}
          <Row className="flex-col gap-4 md:gap-6 lg:flex-row">
            <Col className="w-full flex-1 gap-2">
              <Skeleton className="h-4 w-20" /> {/* Label */}
              <Skeleton className="h-12 w-full rounded-md" /> {/* Input */}
            </Col>
            <Col className="w-full flex-1 gap-2">
              <Skeleton className="h-4 w-20" /> {/* Label */}
              <Skeleton className="h-12 w-full rounded-md" /> {/* Input */}
            </Col>
          </Row>

          {/* Second row of form inputs */}
          <Row className="flex-col gap-4 md:gap-6 lg:flex-row">
            <Col className="w-full flex-1 gap-2">
              <Skeleton className="h-4 w-28" /> {/* Label */}
              <Skeleton className="h-12 w-full rounded-md" /> {/* Input */}
            </Col>
            <Col className="w-full flex-1 gap-2">
              <Skeleton className="h-4 w-32" /> {/* Label */}
              <Skeleton className="h-12 w-full rounded-md" /> {/* Input */}
            </Col>
          </Row>
        </Col>
      </Card>
    </Col>
  );
}
