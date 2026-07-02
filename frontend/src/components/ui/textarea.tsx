import type { TextareaHTMLAttributes } from "react";

type TextareaProps = TextareaHTMLAttributes<HTMLTextAreaElement> & {
  label?: string;
  error?: string;
};

export function Textarea({ label, error, className = "", id, ...props }: TextareaProps) {
  const textareaId = id ?? props.name;

  return (
    <label className="block">
      {label && (
        <span className="mb-2 block text-sm font-medium text-slate-300">
          {label}
        </span>
      )}

      <textarea
        id={textareaId}
        className={`min-h-28 w-full resize-y rounded-xl border border-slate-800 bg-slate-950 px-3 py-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 disabled:cursor-not-allowed disabled:opacity-50 ${className}`}
        {...props}
      />

      {error && (
        <span className="mt-2 block text-sm text-rose-300">
          {error}
        </span>
      )}
    </label>
  );
}
