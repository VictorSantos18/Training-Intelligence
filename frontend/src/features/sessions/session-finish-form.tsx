"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import type { TrainingSession, TrainingSessionFinishFormValues } from "@/types";

import { getDefaultFinishedAtValue } from "./session-formatters";
import styles from "./session-finish-form.module.css";

type SessionFinishFormProps = {
  session: TrainingSession;
  onCancel: () => void;
  onSubmit: (values: TrainingSessionFinishFormValues) => Promise<void>;
};

export function SessionFinishForm({ session, onCancel, onSubmit }: SessionFinishFormProps) {
  const finishFormSchema = z
    .object({
      finished_at: z.string().min(1, "Informe o horário de término."),
      notes_after: z.string().optional().default(""),
    })
    .refine((values) => new Date(values.finished_at) > new Date(session.started_at), {
      message: "O término precisa ser posterior ao início da sessão.",
      path: ["finished_at"],
    });

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<TrainingSessionFinishFormValues>({
    resolver: zodResolver(finishFormSchema),
    defaultValues: {
      finished_at: getDefaultFinishedAtValue(session.started_at),
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
          <p>Finalizar sessão</p>
          <h2 id="finish-session-title">
            {new Date(session.started_at).toLocaleString("pt-BR")}
          </h2>
        </header>

        <form className={styles.form} onSubmit={handleSubmit(onSubmit)}>
          <label className={styles.field}>
            <span>Término</span>
            <input type="datetime-local" {...register("finished_at")} />
            {errors.finished_at ? <small>{errors.finished_at.message}</small> : null}
          </label>

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
