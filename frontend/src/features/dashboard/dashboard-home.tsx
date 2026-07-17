"use client";

import { ProtectedView } from "@/components/layout/protected-view";
import { SystemStatus } from "@/components/system-status";

import styles from "./dashboard-home.module.css";

export function DashboardHome() {
  return (
    <ProtectedView errorTitle="Nao foi possivel abrir o painel">
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
    </ProtectedView>
  );
}
