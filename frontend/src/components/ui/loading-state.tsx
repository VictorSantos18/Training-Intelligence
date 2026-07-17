import styles from "./loading-state.module.css";

type LoadingStateProps = {
  eyebrow?: string;
  message: string;
  title: string;
};

export function LoadingState({
  eyebrow = "Training Intelligence",
  message,
  title,
}: LoadingStateProps) {
  return (
    <main className={styles.page}>
      <section className={styles.panel} aria-live="polite">
        <div className={styles.orbit} aria-hidden="true">
          <span />
        </div>
        <div className={styles.copy}>
          <p className={styles.eyebrow}>{eyebrow}</p>
          <h1>{title}</h1>
          <p>{message}</p>
        </div>
      </section>
    </main>
  );
}
