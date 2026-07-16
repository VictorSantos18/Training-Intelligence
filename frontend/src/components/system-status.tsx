"use client";

import { useEffect, useState } from "react";

import { getApiUrl } from "@/lib/api";

type HealthState = "checking" | "online" | "offline";

export function SystemStatus() {
  const [status, setStatus] = useState<HealthState>("checking");

  useEffect(() => {
    const controller = new AbortController();

    fetch(`${getApiUrl()}/health`, { signal: controller.signal })
      .then((response) => {
        setStatus(response.ok ? "online" : "offline");
      })
      .catch(() => {
        if (!controller.signal.aborted) {
          setStatus("offline");
        }
      });

    return () => controller.abort();
  }, []);

  const statusLabel = {
    checking: "Verificando API",
    online: "API online",
    offline: "API offline",
  }[status];

  const statusClass = {
    checking: "bg-slate-100 text-slate-700",
    online: "bg-emerald-50 text-emerald-700",
    offline: "bg-red-50 text-red-700",
  }[status];

  return (
    <div className={`w-full rounded-lg border border-slate-200 px-4 py-3 text-sm md:w-48 ${statusClass}`}>
      <span className="font-medium">{statusLabel}</span>
    </div>
  );
}

