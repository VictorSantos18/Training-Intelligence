"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import type { TrainingSession, TrainingSessionFinishFormValues } from "@/types";

import styles from "./session-finish-form.module.css";

const zeroToTenString = z
  .string()
  .refine((value) => value === "" || (Number(value) >= 0 && Number(value) <= 10), {
    message: "Use um valor de 0 a 10.",
  });

const finishFormSchema = z.object({
  fatigue_after: zeroToTenString,
  performance_rating: zeroToTenString,
  notes_after: z.string().optional().default(""),
});

type SessionFinishFormProps = {
  session: TrainingSession;
  onCancel: () => void;
  onSubmit: (values: TrainingSessionFinishFormValues) => Promise<void>;
};

export function SessionFinishForm({ session, onCancel, onSubmit }: SessionFinishFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<TrainingSessionFinishFormValues>({
    resolver: zodResolver(finishFormSchema),
    defaultValues: {
      fatigue_after: "",
      performance_rating: "",
      notes_after: "",
    },
  });

  return (
    <div className={styles.backdrop} role="presentation" onMouseDown={onCancel}>
      <section
        aria-labelledby="finish-session-title"
        aria-modal="true"
        className={styles.dialog}
        role="dialog"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <header className={styles.header}>
          <p>Finalizar sessao</p>
          <h2 id="finish-session-title">
            {new Date(session.started_at).toLocaleString("pt-BR")}
          </h2>
        </header>

        <form className={styles.form} onSubmit={handleSubmit(onSubmit)}>
          <div className={styles.grid}>
            <label className={styles.field}>
              <span>Fadiga final</span>
              <input min="0" max="10" type="number" {...register("fatigue_after")} />
              {errors.fatigue_after ? (
                <small>{errors.fatigue_after.message}</small>
              ) : null}
            </label>

            <label className={styles.field}>
              <span>Performance</span>
              <input min="0" max="10" type="number" {...register("performance_rating")} />
              {errors.performance_rating ? (
                <small>{errors.performance_rating.message}</small>
              ) : null}
            </label>
          </div>

          <label className={styles.field}>
            <span>Notas depois</span>
            <textarea rows={4} {...register("notes_after")} />
          </label>

          <div className={styles.actions}>
            <button className={styles.secondary} type="button" onClick={onCancel}>
              Cancelar
            </button>
            <button className={styles.primary} type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Finalizando..." : "Finalizar"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
