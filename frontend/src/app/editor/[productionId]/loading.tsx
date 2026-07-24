export default function EditorLoading() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[#05070d] text-white">
      <div className="text-center">
        <div className="mx-auto h-9 w-9 animate-spin rounded-full border-2 border-white/20 border-t-violet-500" />
        <p className="mt-4 text-sm text-white/60">Opening editor…</p>
      </div>
    </main>
  );
}
