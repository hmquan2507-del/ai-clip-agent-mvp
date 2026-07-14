"use client";

import { createContext } from "react";

import type {
  ReviewWorkspaceContextValue,
} from "./contracts";

export const ReviewWorkspaceContext =
  createContext<ReviewWorkspaceContextValue | null>(
    null,
  );

ReviewWorkspaceContext.displayName =
  "ReviewWorkspaceContext";