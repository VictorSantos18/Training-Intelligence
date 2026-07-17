"use client";

import { useEffect, useState } from "react";

import { getApiUrl } from "@/lib/api";

import styles from "./system-status.module.css";

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

  return (
    <div className={`${styles.status} ${styles[status]}`}>
      <span className="font-medium">{statusLabel}</span>
    </div>
  );
}
