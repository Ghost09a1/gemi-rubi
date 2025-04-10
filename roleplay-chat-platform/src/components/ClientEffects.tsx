"use client";

import { useEffect } from "react";

export default function ClientEffects() {
  // Remove any extension-added classes during hydration
  useEffect(() => {
    // This runs only on the client after hydration
    document.body.className = "antialiased";
  }, []);

  // Return null since this component is only for side effects
  return null;
}
