import type {
  ButtonHTMLAttributes,
  HTMLAttributes,
  ReactNode,
} from "react";

import type {
  ReviewBadgeTone,
  ReviewButtonVariant,
  ReviewControlSize,
  ReviewPanelVariant,
  ReviewSurfaceVariant,
} from "./contracts";

import {
  reviewClassNames,
} from "./utils";

const surfaceClasses:
  Record<ReviewSurfaceVariant, string> = {
    base:
      "bg-[var(--review-bg)]",

    raised:
      "bg-[var(--review-surface-1)] shadow-[var(--review-shadow-panel)]",

    floating:
      "border border-[var(--review-border-strong)] bg-[var(--review-surface-floating)] shadow-[var(--review-shadow-floating)] backdrop-blur-xl",
  };

const panelClasses:
  Record<ReviewPanelVariant, string> = {
    default:
      "border-[var(--review-border)] bg-[var(--review-surface-1)]",

    subtle:
      "border-[var(--review-border-subtle)] bg-[var(--review-surface-2)]",

    active:
      "border-[var(--review-accent-border)] bg-[var(--review-accent-soft)] shadow-[inset_0_0_0_1px_var(--review-accent-ring)]",
  };

const buttonVariantClasses:
  Record<ReviewButtonVariant, string> = {
    primary:
      "border-transparent bg-[var(--review-accent)] text-white shadow-[var(--review-shadow-accent)] hover:bg-[var(--review-accent-hover)] active:bg-[var(--review-accent-active)]",

    secondary:
      "border-[var(--review-border-strong)] bg-[var(--review-surface-3)] text-[var(--review-text)] hover:border-[var(--review-border-hover)] hover:bg-[var(--review-surface-hover)]",

    ghost:
      "border-transparent bg-transparent text-[var(--review-text-muted)] hover:bg-[var(--review-surface-hover)] hover:text-[var(--review-text)]",

    danger:
      "border-[var(--review-danger-border)] bg-[var(--review-danger-soft)] text-[var(--review-danger-text)] hover:bg-[var(--review-danger-hover)]",
  };

const controlSizeClasses:
  Record<ReviewControlSize, string> = {
    sm:
      "h-8 gap-1.5 rounded-lg px-2.5 text-xs",

    md:
      "h-9 gap-2 rounded-[10px] px-3 text-sm",

    lg:
      "h-11 gap-2.5 rounded-xl px-4 text-sm",
  };

const iconSizeClasses:
  Record<ReviewControlSize, string> = {
    sm:
      "size-8 rounded-lg",

    md:
      "size-9 rounded-[10px]",

    lg:
      "size-11 rounded-xl",
  };

const badgeClasses:
  Record<ReviewBadgeTone, string> = {
    neutral:
      "border-[var(--review-border)] bg-[var(--review-surface-3)] text-[var(--review-text-muted)]",

    brand:
      "border-[var(--review-accent-border)] bg-[var(--review-accent-soft)] text-[var(--review-accent-text)]",

    info:
      "border-[var(--review-info-border)] bg-[var(--review-info-soft)] text-[var(--review-info-text)]",

    success:
      "border-[var(--review-success-border)] bg-[var(--review-success-soft)] text-[var(--review-success-text)]",

    warning:
      "border-[var(--review-warning-border)] bg-[var(--review-warning-soft)] text-[var(--review-warning-text)]",

    danger:
      "border-[var(--review-danger-border)] bg-[var(--review-danger-soft)] text-[var(--review-danger-text)]",
  };

export interface ReviewEditorSurfaceProps
  extends HTMLAttributes<HTMLDivElement> {
  variant?: ReviewSurfaceVariant;
}

export function ReviewEditorSurface({
  variant = "base",
  className,
  ...props
}: ReviewEditorSurfaceProps) {
  return (
    <div
      data-review-surface={variant}
      className={reviewClassNames(
        "review-editor-theme min-h-0 text-[var(--review-text)] antialiased",
        surfaceClasses[variant],
        className,
      )}
      {...props}
    />
  );
}

export interface ReviewPanelProps
  extends HTMLAttributes<HTMLDivElement> {
  variant?: ReviewPanelVariant;
}

export function ReviewPanel({
  variant = "default",
  className,
  ...props
}: ReviewPanelProps) {
  return (
    <div
      data-review-panel={variant}
      className={reviewClassNames(
        "min-h-0 rounded-[var(--review-radius-panel)] border",
        panelClasses[variant],
        className,
      )}
      {...props}
    />
  );
}

export function ReviewPanelHeader({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={reviewClassNames(
        "flex min-h-11 items-center justify-between gap-3 border-b border-[var(--review-border-subtle)] px-3.5 py-2",
        className,
      )}
      {...props}
    />
  );
}

export function ReviewPanelTitle({
  className,
  ...props
}: HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h2
      className={reviewClassNames(
        "truncate text-xs font-semibold tracking-[0.01em] text-[var(--review-text)]",
        className,
      )}
      {...props}
    />
  );
}

export function ReviewPanelBody({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={reviewClassNames(
        "min-h-0 p-3.5",
        className,
      )}
      {...props}
    />
  );
}

export interface ReviewButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ReviewButtonVariant;
  size?: ReviewControlSize;
}

export function ReviewButton({
  variant = "primary",
  size = "md",
  type = "button",
  className,
  ...props
}: ReviewButtonProps) {
  return (
    <button
      type={type}
      data-review-button={variant}
      className={reviewClassNames(
        "inline-flex shrink-0 items-center justify-center border font-medium outline-none transition-[background-color,border-color,color,box-shadow,transform] duration-150 focus-visible:ring-2 focus-visible:ring-[var(--review-focus)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--review-bg)] disabled:pointer-events-none disabled:opacity-40 active:translate-y-px",
        buttonVariantClasses[variant],
        controlSizeClasses[size],
        className,
      )}
      {...props}
    />
  );
}

export interface ReviewIconButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement> {
  "aria-label": string;
  variant?: ReviewButtonVariant;
  size?: ReviewControlSize;
}

export function ReviewIconButton({
  variant = "ghost",
  size = "md",
  type = "button",
  className,
  ...props
}: ReviewIconButtonProps) {
  return (
    <button
      type={type}
      data-review-icon-button={variant}
      className={reviewClassNames(
        "inline-flex shrink-0 items-center justify-center border outline-none transition-[background-color,border-color,color,box-shadow,transform] duration-150 focus-visible:ring-2 focus-visible:ring-[var(--review-focus)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--review-bg)] disabled:pointer-events-none disabled:opacity-40 active:translate-y-px [&_svg]:size-4",
        buttonVariantClasses[variant],
        iconSizeClasses[size],
        className,
      )}
      {...props}
    />
  );
}

export interface ReviewBadgeProps
  extends HTMLAttributes<HTMLSpanElement> {
  tone?: ReviewBadgeTone;
  dot?: boolean;
}

export function ReviewBadge({
  tone = "neutral",
  dot = false,
  className,
  children,
  ...props
}: ReviewBadgeProps) {
  return (
    <span
      data-review-badge={tone}
      className={reviewClassNames(
        "inline-flex h-6 items-center gap-1.5 rounded-full border px-2 text-[11px] font-medium",
        badgeClasses[tone],
        className,
      )}
      {...props}
    >
      {dot ? (
        <span
          className="size-1.5 rounded-full bg-current"
          aria-hidden="true"
        />
      ) : null}

      {children}
    </span>
  );
}

export function ReviewToolbarGroup({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      role="group"
      className={reviewClassNames(
        "inline-flex items-center gap-0.5 rounded-xl border border-[var(--review-border)] bg-[var(--review-surface-2)] p-1",
        className,
      )}
      {...props}
    />
  );
}

export function ReviewDivider({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      role="separator"
      className={reviewClassNames(
        "h-px w-full shrink-0 bg-[var(--review-border-subtle)]",
        className,
      )}
      {...props}
    />
  );
}

export function ReviewKeyboardHint({
  className,
  ...props
}: HTMLAttributes<HTMLElement>) {
  return (
    <kbd
      className={reviewClassNames(
        "inline-flex min-w-5 items-center justify-center rounded-md border border-[var(--review-border-strong)] bg-[var(--review-surface-3)] px-1.5 py-0.5 font-mono text-[10px] leading-none text-[var(--review-text-subtle)] shadow-[inset_0_-1px_0_var(--review-border-strong)]",
        className,
      )}
      {...props}
    />
  );
}

export function ReviewSkeleton({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      aria-hidden="true"
      className={reviewClassNames(
        "review-skeleton rounded-lg bg-[var(--review-surface-3)]",
        className,
      )}
      {...props}
    />
  );
}

export interface ReviewEmptyStateProps
  extends HTMLAttributes<HTMLDivElement> {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
}

export function ReviewEmptyState({
  icon,
  title,
  description,
  action,
  className,
  ...props
}: ReviewEmptyStateProps) {
  return (
    <div
      className={reviewClassNames(
        "flex min-h-40 flex-col items-center justify-center gap-2 px-6 py-8 text-center",
        className,
      )}
      {...props}
    >
      {icon ? (
        <div className="mb-1 flex size-10 items-center justify-center rounded-xl border border-[var(--review-border)] bg-[var(--review-surface-3)] text-[var(--review-text-muted)] [&_svg]:size-5">
          {icon}
        </div>
      ) : null}

      <p className="text-sm font-semibold text-[var(--review-text)]">
        {title}
      </p>

      {description ? (
        <p className="max-w-xs text-xs leading-5 text-[var(--review-text-subtle)]">
          {description}
        </p>
      ) : null}

      {action ? (
        <div className="mt-2">
          {action}
        </div>
      ) : null}
    </div>
  );
}