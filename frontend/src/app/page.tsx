import { ArrowRight, UploadCloud } from "lucide-react";
import { DashboardShell } from "@/components/layout/dashboard-shell";
import { Badge } from "@/components/ui/badge";
import { ButtonLink } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { SectionHeader } from "@/components/ui/section-header";
import { ProductionCard } from "@/features/production/production-card";
import { ActivityFeed } from "@/features/workspace/activity-feed";
import { ContinueProductionCard } from "@/features/workspace/continue-production-card";
import { QuickActions } from "@/features/workspace/quick-actions";
import { productions } from "@/lib/mock-productions";

const stats = [
  { label: "Active Productions", value: "3", helper: "+2 hôm nay" },
  { label: "Ready for Review", value: "1", helper: "Cần kiểm tra" },
  { label: "Processing", value: "1", helper: "AI đang chạy" },
  { label: "Exported", value: "8", helper: "Tháng này" },
];

export default function HomePage() {
  const continueProduction = productions[0];

  return (
    <DashboardShell title="Home">
        <div className="grid gap-6">
        <section className="rounded-3xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-900 to-violet-950/40 p-5 shadow-sm md:p-6">
          <div className="grid gap-6 xl:grid-cols-[1.25fr_0.85fr]">
            <div>
              <Badge tone="violet">AI Production Workspace</Badge>

              <h2 className="mt-4 max-w-3xl text-3xl font-semibold tracking-tight text-white md:text-4xl">
                Biến video thô thành production sẵn sàng xuất bản.
              </h2>

              <p className="mt-4 max-w-2xl text-sm leading-6 text-slate-300">
                Workspace này đi theo flow chính: Home → Upload → AI Queue →
                Review → Export. Người dùng bắt đầu từ Production, không phải
                dashboard admin.
              </p>

              <div className="mt-6 flex flex-col gap-3 sm:flex-row">
                <ButtonLink href="/upload">
                  <UploadCloud className="h-4 w-4" />
                  Start Production
                </ButtonLink>

                <ButtonLink href="/productions" variant="secondary">
                  View Productions
                  <ArrowRight className="h-4 w-4" />
                </ButtonLink>
              </div>
            </div>

            <ContinueProductionCard production={continueProduction} />
          </div>
        </section>

        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {stats.map((stat) => (
            <Card key={stat.label}>
              <CardContent>
                <p className="text-sm text-slate-400">{stat.label}</p>
                <p className="mt-2 text-3xl font-semibold text-white">
                  {stat.value}
                </p>
                <p className="mt-1 text-sm text-slate-500">{stat.helper}</p>
              </CardContent>
            </Card>
          ))}
        </section>

        <QuickActions />

        <section className="grid gap-6 xl:grid-cols-[1.35fr_0.75fr]">
          <div>
            <SectionHeader
              eyebrow="Production First"
              title="Recent Productions"
              description="Các production gần đây, trạng thái xử lý và tiến độ AI."
              action={
                <ButtonLink href="/productions" variant="ghost" size="sm">
                  View all
                </ButtonLink>
              }
            />

            <div className="grid gap-4">
              {productions.map((production) => (
                <ProductionCard key={production.id} production={production} />
              ))}
            </div>
          </div>

          <div>
            <ActivityFeed />
          </div>
        </section>
      </div>
    </DashboardShell>
  );
}