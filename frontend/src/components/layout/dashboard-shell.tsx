import { Sidebar } from "@/components/navigation/sidebar";

export function DashboardShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[#070A12] text-white">
      <Sidebar />
      <main className="pl-64">
        <header className="h-16 border-b border-white/10 px-8 flex items-center justify-between">
          <div>
            <p className="text-sm text-white/50">AI Clip Studio</p>
            <h1 className="text-lg font-semibold">Dashboard</h1>
          </div>
          <button className="rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium hover:bg-violet-500">
            Upload Video
          </button>
        </header>

        <section className="p-8">{children}</section>
      </main>
    </div>
  );
}
