"use client";

import { useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { LoadingState } from "@/components/ui/loading-state";
import { useAuthenticatedSession } from "@/features/auth/use-authenticated-session";
import type { AuthenticatedSession } from "@/types";

import styles from "./protected-view.module.css";

type ProtectedViewProps = {
  children: ReactNode | ((session: AuthenticatedSession) => ReactNode);
  errorTitle?: string;
};

export function ProtectedView({
  children,
  errorTitle = "Não foi possível abrir esta área",
}: ProtectedViewProps) {
  const router = useRouter();
  const { sessionState, session, error } = useAuthenticatedSession();

  useEffect(() => {
    if (sessionState === "unauthenticated" && !session && !error) {
      router.replace("/login");
    }
  }, [error, router, session, sessionState]);

  if (sessionState === "checking") {
    return (
      <LoadingState
        title="Validando sessão"
        message="Estamos conferindo seu acesso e preparando seu painel."
      />
    );
  }

  if (!session && !error) {
    return (
      <LoadingState
        title="Redirecionando"
        message="Vamos levar você para a tela de login."
      />
    );
  }

  if (!session) {
    return (
      <main className={styles.loadingPage}>
        <div className={styles.errorPanel}>
          <h1>{errorTitle}</h1>
          <p>{error ?? "Entre novamente para continuar."}</p>
          <button type="button" onClick={() => router.replace("/login")}>
            Voltar para login
          </button>
        </div>
      </main>
    );
  }

  const content = typeof children === "function" ? children(session) : children;

  return <AppShell user={session.user}>{content}</AppShell>;
}
