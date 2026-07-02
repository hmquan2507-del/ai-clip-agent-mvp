type ProgressProps = {
  value: number;
  label?: string;
  helperText?: string;
};

export function Progress({ value, label, helperText }: ProgressProps) {
  const safeValue = Math.min(100, Math.max(0, value));

  return (
    <div className="w-full">
      {(label || helperText) && (
        <div className="mb-2 flex items-center justify-between gap-3 text-sm">
          {label && <span className="font-medium text-slate-300">{label}</span>}
          {helperText && <span className="text-slate-500">{helperText}</span>}
        </div>
      )}

      <div className="h-2 overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full rounded-full bg-violet-500 transition-all"
          style={{ width: `${safeValue}%` }}
        />
      </div>
    </div>
  );
}
