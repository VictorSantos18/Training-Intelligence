import { AuthCard } from "@/features/auth/auth-card";

import styles from "./page.module.css";

export default function LoginPage() {
  return (
    <main className={styles.page}>
      <AuthCard mode="login" />
    </main>
  );
}
