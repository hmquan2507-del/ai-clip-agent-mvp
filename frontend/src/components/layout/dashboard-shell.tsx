import { Sidebar } from "@/components/navigation/sidebar";
import Link from "next/link";

type DashboardShellProps = {
  children: React.ReactNode;
  title: string;
  eyebrow?: string;
  actionHref?: string;
  actionLabel?: string;
};

export function DashboardShell({
  children,
  title,
  eyebrow = "AI Production Workspace",
  actionHref = "/upload",
  actionLabel = "Start Production",
}: DashboardShellProps) {
  return (
    <div className="min-h-screen bg-[#070A12] text-white">
      <Sidebar />
      <main className="min-h-screen pl-64 max-lg:pl-0">
        <header className="flex min-h-16 items-center justify-between gap-4 border-b border-white/10 px-8 py-4 max-lg:pl-72 max-md:flex-col max-md:items-start max-md:px-5 max-md:pl-5">
          <div>
            <p className="text-sm text-white/50">{eyebrow}</p>
            <h1 className="text-lg font-semibold">{title}</h1>
          </div>
          <Link
            href={actionHref}
            className="rounded-xl bg-violet-600 px-4 py-2 text-sm font-medium hover:bg-violet-500"
          >
            {actionLabel}
          </Link>
        </header>

        <section className="p-8 max-md:p-5">{children}</section>
      </main>
    </div>
  );
}
