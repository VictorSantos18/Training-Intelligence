import { AuthCard } from "@/features/auth/auth-card";

import styles from "./page.module.css";

export default function SignupPage() {
  return (
    <main className={styles.page}>
      <AuthCard mode="signup" />
    </main>
  );
}
