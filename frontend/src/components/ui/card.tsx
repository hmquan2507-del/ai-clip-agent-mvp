import type { HTMLAttributes, ReactNode } from "react";

type CardProps = HTMLAttributes<HTMLDivElement> & {
  children: ReactNode;
};

export function Card({
  children,
  className = "",
  ...props
}: CardProps) {
  return (
    <div
      className={`rounded-3xl border border-slate-800 bg-slate-900/60 shadow-sm ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

type CardHeaderProps = {
  title: string;
  description?: string;
};

export function CardHeader({
  title,
  description,
}: CardHeaderProps) {
  return (
    <div className="border-b border-slate-800 px-6 py-5">
      <h3 className="text-lg font-semibold text-white">
        {title}
      </h3>

      {description && (
        <p className="mt-1 text-sm text-slate-400">
          {description}
        </p>
      )}
    </div>
  );
}

export function CardContent({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div className="p-6">
      {children}
    </div>
  );
}

export function CardFooter({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div className="border-t border-slate-800 px-6 py-4">
      {children}
    </div>
  );
}