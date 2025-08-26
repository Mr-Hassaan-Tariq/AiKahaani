import DesktopMenu from './_components/DesktopMenu';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="h-[100dvh] min-h-screen w-full overflow-hidden bg-[#0E0F0C]">
      <div className="mx-auto flex max-w-screen-2xl">
        {/* Desktop Sidebar */}
        <div className="hidden h-screen lg:block lg:w-[265px]">
          <DesktopMenu />
        </div>

        {/* Mobile Top Navigation */}
        <div className="fixed left-0 right-0 top-0 z-40 border-b border-gray-800 bg-[#0E0F0C] px-4 py-3 lg:hidden">
          <div className="flex items-center justify-between text-white">
            <div className="text-lg font-semibold">Menu</div>
            {/* Add mobile menu toggle button here */}
          </div>
        </div>

        {/* Main Content Area */}
        <div className="scrollbar max-h-screen min-h-screen w-full overflow-y-auto">
          <div className="hidden h-20 w-full items-center border-b border-gray-200 text-white lg:flex">
            Menu
          </div>
          <div className="mx-auto px-4 py-10 lg:px-16 lg:py-16">{children}</div>
        </div>
      </div>
    </div>
  );
}
