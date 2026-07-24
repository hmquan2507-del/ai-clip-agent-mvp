import Link from "next/link";

export default function EditorNotFound() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-[#070A12] px-6 text-white">
      <section className="max-w-md text-center">
        <p className="text-sm font-medium text-violet-300">Editor</p>
        <h1 className="mt-3 text-3xl font-semibold">Production not found</h1>
        <p className="mt-3 text-sm leading-6 text-white/55">
          The requested production ID is empty or unavailable.
        </p>
        <Link
          href="/workspace"
          className="mt-6 inline-flex rounded-xl bg-violet-600 px-4 py-2.5 text-sm font-medium hover:bg-violet-500"
        >
          Back to workspace
        </Link>
      </section>
    </main>
  );
}
