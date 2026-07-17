"use client";

import { useRouter } from "next/navigation";
import type { ReactNode } from "react";

import { getSupabaseClient } from "@/lib/supabase";
import type { CurrentUser } from "@/types";

import styles from "./app-shell.module.css";

type AppShellProps = {
  user: CurrentUser;
  children: ReactNode;
};

export function AppShell({ user, children }: AppShellProps) {
  const router = useRouter();

  async function handleLogout() {
    await getSupabaseClient().auth.signOut();
    router.replace("/login");
  }

  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar}>
        <div>
          <p className={styles.brandEyebrow}>Training</p>
          <h1 className={styles.brand}>Intelligence</h1>
        </div>

        <nav className={styles.nav} aria-label="Navegacao principal">
          <a className={styles.navItemActive} href="/dashboard">
            Dashboard
          </a>
          <span className={styles.navItemMuted}>Skills</span>
          <span className={styles.navItemMuted}>Exercicios</span>
          <span className={styles.navItemMuted}>Sessoes</span>
        </nav>

        <div className={styles.account}>
          <span className={styles.accountLabel}>Conta</span>
          <strong className={styles.email}>{user.email ?? "Usuario autenticado"}</strong>
          <button className={styles.logout} type="button" onClick={handleLogout}>
            Sair
          </button>
        </div>
      </aside>

      <main className={styles.content}>{children}</main>
    </div>
  );
}
