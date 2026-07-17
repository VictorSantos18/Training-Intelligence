"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { getSupabaseClient, isSupabaseConfigured } from "@/lib/supabase";

import styles from "@/app/page.module.css";

export function AuthRedirect() {
  const router = useRouter();

  useEffect(() => {
    if (!isSupabaseConfigured()) {
      router.replace("/login");
      return;
    }

    getSupabaseClient()
      .auth.getSession()
      .then(({ data }) => {
        router.replace(data.session ? "/dashboard" : "/login");
      })
      .catch(() => router.replace("/login"));
  }, [router]);

  return (
    <main className={styles.page}>
      <p className={styles.status}>Carregando sua area de treino...</p>
    </main>
  );
}
