export default function WorkspaceLoading() {
  return (
    <main className="min-h-screen bg-[#070A12] p-8 text-white">
      <div className="mx-auto max-w-7xl animate-pulse space-y-6">
        <div className="h-10 w-56 rounded-xl bg-white/10" />
        <div className="h-44 rounded-3xl bg-white/5" />
        <div className="grid gap-4 md:grid-cols-3">
          <div className="h-32 rounded-2xl bg-white/5" />
          <div className="h-32 rounded-2xl bg-white/5" />
          <div className="h-32 rounded-2xl bg-white/5" />
        </div>
      </div>
    </main>
  );
}
