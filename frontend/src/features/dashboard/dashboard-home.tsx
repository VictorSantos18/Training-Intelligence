"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/layout/app-shell";
import { SystemStatus } from "@/components/system-status";
import { getCurrentUser } from "@/lib/api";
import { getSupabaseClient, isSupabaseConfigured } from "@/lib/supabase";
import type { AuthSessionState, CurrentUser } from "@/types";

import styles from "./dashboard-home.module.css";

export function DashboardHome() {
  const router = useRouter();
  const [sessionState, setSessionState] = useState<AuthSessionState>("checking");
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadUser() {
      if (!isSupabaseConfigured()) {
        setError("Supabase nao esta configurado no frontend.");
        setSessionState("unauthenticated");
        return;
      }

      const supabase = getSupabaseClient();
      const { data } = await supabase.auth.getSession();

      if (!data.session) {
        router.replace("/login");
        return;
      }

      try {
        const currentUser = await getCurrentUser(data.session.access_token);
        if (!isMounted) {
          return;
        }
        setUser(currentUser);
        setSessionState("authenticated");
      } catch (err) {
        if (!isMounted) {
          return;
        }
        setError(err instanceof Error ? err.message : "Falha ao validar usuario.");
        setSessionState("unauthenticated");
      }
    }

    void loadUser();

    return () => {
      isMounted = false;
    };
  }, [router]);

  if (sessionState === "checking") {
    return (
      <main className={styles.loadingPage}>
        <p>Validando sessao...</p>
      </main>
    );
  }

  if (!user) {
    return (
      <main className={styles.loadingPage}>
        <div className={styles.errorPanel}>
          <h1>Nao foi possivel abrir o painel</h1>
          <p>{error ?? "Entre novamente para continuar."}</p>
          <button type="button" onClick={() => router.replace("/login")}>
            Voltar para login
          </button>
        </div>
      </main>
    );
  }

  return (
    <AppShell user={user}>
      <section className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Painel autenticado</p>
          <h2>Seu sistema esta pronto para dados reais.</h2>
          <p>
            A autenticacao ja esta conectada ao Supabase e o backend responde usando o
            token do usuario atual.
          </p>
        </div>
        <SystemStatus />
      </section>

      <section className={styles.grid} aria-label="Resumo do sistema">
        <article className={styles.metric}>
          <span>Status</span>
          <strong>Autenticado</strong>
          <p>GET /me validado com token Supabase.</p>
        </article>
        <article className={styles.metric}>
          <span>Proximo modulo</span>
          <strong>Skills</strong>
          <p>Cadastro e listagem serao a primeira tela de dominio.</p>
        </article>
        <article className={styles.metric}>
          <span>Foco visual</span>
          <strong>Dark + roxo</strong>
          <p>Base minimalista preparada para fluxo mobile-first.</p>
        </article>
      </section>
    </AppShell>
  );
}
