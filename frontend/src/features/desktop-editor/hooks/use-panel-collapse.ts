"use client";

import { useCallback, useState } from "react";

export function usePanelCollapse(initialCollapsed = false) {
  const [collapsed, setCollapsed] = useState(initialCollapsed);

  const collapse = useCallback(() => setCollapsed(true), []);
  const expand = useCallback(() => setCollapsed(false), []);
  const toggle = useCallback(() => setCollapsed((value) => !value), []);

  return { collapsed, collapse, expand, toggle };
}
