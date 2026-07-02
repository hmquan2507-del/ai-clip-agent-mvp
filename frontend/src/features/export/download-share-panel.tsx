import {
  Copy,
  Download,
  ExternalLink,
  Link2,
  Share2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export function DownloadSharePanel() {
  return (
    <Card>
      <CardHeader
        title="Download & Share"
        description="Download exported files or share them with your team."
      />

      <CardContent>
        <div className="grid gap-4">
          <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
            <p className="text-sm text-slate-400">
              Export URL
            </p>

            <div className="mt-3 flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900 px-3 py-2">
              <Link2 className="h-4 w-4 text-slate-500" />

              <span className="flex-1 truncate text-sm text-slate-300">
                https://clipagent.ai/export/prd_001.mp4
              </span>

              <Button size="sm" variant="ghost">
                <Copy className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <Button>
              <Download className="h-4 w-4" />
              Download MP4
            </Button>

            <Button variant="secondary">
              <Share2 className="h-4 w-4" />
              Share Link
            </Button>

            <Button variant="ghost">
              <ExternalLink className="h-4 w-4" />
              Open Preview
            </Button>

            <Button variant="ghost">
              <Copy className="h-4 w-4" />
              Copy URL
            </Button>
          </div>

          <div className="rounded-2xl border border-emerald-900/30 bg-emerald-500/10 p-4">
            <p className="font-medium text-emerald-300">
              Export completed successfully
            </p>

            <p className="mt-2 text-sm leading-6 text-emerald-200/80">
              Video is ready for download or sharing.
              In later EPICs this panel will integrate with cloud storage,
              signed URLs, and publishing destinations.
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}