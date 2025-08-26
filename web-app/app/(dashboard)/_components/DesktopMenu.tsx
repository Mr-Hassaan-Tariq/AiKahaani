import Col from 'components/ui/Col';

export default function DesktopMenu() {
  return (
    <div className="scrollbar sticky top-0 max-h-screen w-full overflow-hidden overflow-y-auto rounded-r border-r border-gray-800 bg-[#0E0F0C] px-7 py-8 text-white">
      <Col>
        {Array.from({ length: 25 }).map((_, i) => (
          <div key={i}>DesktopMenu</div>
        ))}
      </Col>
    </div>
  );
}
