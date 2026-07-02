type LoadingStateProps = {
  title?: string;
  description?: string;
};

export function LoadingState({
  title = "Loading",
  description = "Please wait while we prepare your workspace.",
}: LoadingStateProps) {
  return (
    <div className="flex min-h-64 flex-col items-center justify-center rounded-3xl border border-slate-800 bg-slate-900/40 px-6 py-10 text-center">
      <div className="h-10 w-10 animate-spin rounded-full border-2 border-slate-700 border-t-violet-500" />

      <h3 className="mt-4 text-lg font-semibold text-white">{title}</h3>

      <p className="mt-2 max-w-md text-sm leading-6 text-slate-400">
        {description}
      </p>
    </div>
  );
}
