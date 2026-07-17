"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { LoadingState } from "@/components/ui/loading-state";
import { getSupabaseClient, isSupabaseConfigured } from "@/lib/supabase";

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
    <LoadingState
      title="Carregando sua area de treino"
      message="Estamos direcionando você para o melhor ponto de partida."
    />
  );
}
