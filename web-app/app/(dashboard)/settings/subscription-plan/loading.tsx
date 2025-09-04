import Card from 'components/ui/Card';
import Col from 'components/ui/Col';
import Row from 'components/ui/Row';
import { Skeleton } from 'components/shadcn_ui/skeleton';

export default function loading() {
  return (
    <Card>
      <Col className="gap-8">
        {/* Plan header with title and pricing */}
        <Row>
          <Skeleton className="h-8 w-32 lg:h-9 lg:w-40" /> {/* Plan type */}
          <Row className="jus items-end gap-1">
            <Skeleton className="h-8 w-16 lg:h-9 lg:w-20" /> {/* Price */}
            <Skeleton className="mb-1 h-4 w-12" /> {/* Billing cycle */}
          </Row>
        </Row>

        <Col className="gap-4">
          {/* Status row */}
          <Row className="items-center justify-normal gap-3">
            <Skeleton className="h-5 w-12" /> {/* "Status:" */}
            <Skeleton className="h-3 w-3 rounded-full" /> {/* Status dot */}
            <Skeleton className="h-5 w-16" /> {/* Status value */}
          </Row>

          {/* End date row */}
          <Row className="items-center justify-normal gap-3">
            <Skeleton className="h-5 w-10" /> {/* "Ends:" */}
            <Skeleton className="h-5 w-32" /> {/* Date */}
          </Row>

          {/* Access and buttons row */}
          <Row className="flex-col gap-6 lg:flex-row">
            <Row className="items-center gap-3">
              <Skeleton className="h-5 w-14" /> {/* "Access:" */}
              <Skeleton className="h-5 w-48" /> {/* Access description */}
            </Row>

            {/* Action buttons */}
            <Row className="w-full gap-4 lg:w-fit">
              <Skeleton className="h-10 w-40 rounded-md" /> {/* Manage subscription */}
              <Skeleton className="h-10 w-32 rounded-md" /> {/* Upgrade plan */}
            </Row>
          </Row>
        </Col>

        {/* Feature access card */}
        <Card className="rounded-xl border-[#BAFF3812] bg-white/10 px-4 py-4 shadow-[0_0_4px_0_rgba(0,0,0,0.04),0_8px_16px_0_rgba(0,0,0,0.08)] lg:px-4 lg:py-4">
          <Col className="gap-5">
            {/* Header text */}
            <Skeleton className="h-5 w-full max-w-md" />

            {/* Feature list */}
            <Col className="gap-4">
              {[1, 2, 3].map((index) => (
                <Row key={index} className="justify-normal gap-2">
                  <Skeleton className="h-5 w-5 rounded-full" /> {/* Check icon */}
                  <Skeleton className="h-4 w-24" /> {/* Feature name */}
                </Row>
              ))}
            </Col>

            {/* Footer text */}
            <Skeleton className="h-5 w-full max-w-sm" />
          </Col>
        </Card>
      </Col>
    </Card>
  );
}
