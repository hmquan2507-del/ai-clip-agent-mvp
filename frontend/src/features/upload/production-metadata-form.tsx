"use client";

import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

export type ProductionMetadata = {
  title: string;
  description: string;
  style: string;
};

type ProductionMetadataFormProps = {
  value: ProductionMetadata;
  onChange: (value: ProductionMetadata) => void;
};

const styleOptions = [
  "Podcast",
  "Education",
  "Business",
  "Finance",
  "Storytelling",
  "Gaming",
  "Luxury",
  "Real Estate",
];

export function ProductionMetadataForm({
  value,
  onChange,
}: ProductionMetadataFormProps) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-900/60 p-6">
      <div>
        <h3 className="text-lg font-semibold text-white">
          Production Metadata
        </h3>
        <p className="mt-1 text-sm text-slate-400">
          Thông tin này giúp AI chọn style và workflow phù hợp.
        </p>
      </div>

      <div className="mt-6 grid gap-5">
        <Input
          label="Production title"
          name="title"
          placeholder="Ví dụ: Podcast bán hàng tự động"
          value={value.title}
          onChange={(event) =>
            onChange({
              ...value,
              title: event.target.value,
            })
          }
        />

        <Textarea
          label="Description"
          name="description"
          placeholder="Mô tả ngắn về mục tiêu video..."
          value={value.description}
          onChange={(event) =>
            onChange({
              ...value,
              description: event.target.value,
            })
          }
        />

        <label className="block">
          <span className="mb-2 block text-sm font-medium text-slate-300">
            Style
          </span>

          <select
            value={value.style}
            onChange={(event) =>
              onChange({
                ...value,
                style: event.target.value,
              })
            }
            className="h-11 w-full rounded-xl border border-slate-800 bg-slate-950 px-3 text-sm text-white outline-none transition focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20"
          >
            {styleOptions.map((style) => (
              <option key={style} value={style}>
                {style}
              </option>
            ))}
          </select>
        </label>
      </div>
    </div>
  );
}