"use client";

import { useRouter } from "next/navigation";
import type { ReactNode } from "react";

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
  errorTitle = "Nao foi possivel abrir esta area",
}: ProtectedViewProps) {
  const router = useRouter();
  const { sessionState, session, error } = useAuthenticatedSession();

  if (sessionState === "checking") {
    return (
      <LoadingState
        title="Validando sessao"
        message="Estamos conferindo seu acesso e preparando seu painel."
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
