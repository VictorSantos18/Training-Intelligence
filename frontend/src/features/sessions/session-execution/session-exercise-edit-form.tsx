"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import type { SessionExerciseFormValues } from "@/types";

import styles from "./session-exercise-edit-form.module.css";

const sessionExerciseEditSchema = z.object({
  exercise_id: z.string(),
  execution_order: z.string().min(1, "Informe a ordem."),
  notes: z.string().optional().default(""),
});

type SessionExerciseEditFormProps = {
  initialValues: SessionExerciseFormValues;
  onCancel: () => void;
  onSubmit: (values: SessionExerciseFormValues) => Promise<void>;
};

export function SessionExerciseEditForm({
  initialValues,
  onCancel,
  onSubmit,
}: SessionExerciseEditFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SessionExerciseFormValues>({
    resolver: zodResolver(sessionExerciseEditSchema),
    defaultValues: initialValues,
  });

  return (
    <form className={styles.form} onSubmit={handleSubmit(onSubmit)}>
      <input type="hidden" {...register("exercise_id")} />

      <label className={styles.field}>
        <span>Ordem</span>
        <input min="1" type="number" {...register("execution_order")} />
        {errors.execution_order ? <small>{errors.execution_order.message}</small> : null}
      </label>

      <label className={styles.field}>
        <span>Notas</span>
        <input placeholder="Objetivo, variação, ajuste..." type="text" {...register("notes")} />
      </label>

      <button className={styles.primary} type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Salvando..." : "Salvar"}
      </button>
      <button className={styles.secondary} type="button" onClick={onCancel}>
        Cancelar
      </button>
    </form>
  );
}
