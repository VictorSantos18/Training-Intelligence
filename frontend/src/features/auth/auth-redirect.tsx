"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { LoadingState } from "@/components/ui/loading-state";
import { useAuthenticatedSession } from "@/features/auth/use-authenticated-session";

export function AuthRedirect() {
  const router = useRouter();
  const { sessionState, session } = useAuthenticatedSession();

  useEffect(() => {
    if (sessionState === "checking") {
      return;
    }

    if (session) {
      router.replace("/dashboard");
      return;
    }

    if (sessionState === "unauthenticated") {
      router.replace("/login");
    }
  }, [router, session, sessionState]);

  return (
    <LoadingState
      title="Carregando sua area de treino"
      message="Estamos direcionando você para o melhor ponto de partida."
    />
  );
}
