"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import type { Exercise, SessionExerciseFormValues } from "@/types";

import styles from "./execution-exercise-form.module.css";

const sessionExerciseSchema = z.object({
  exercise_id: z.string().min(1, "Escolha um exercício."),
  execution_order: z.string().min(1, "Informe a ordem."),
  notes: z.string().optional().default(""),
});

type ExecutionExerciseFormProps = {
  exercises: Exercise[];
  nextOrder: number;
  onSubmit: (values: SessionExerciseFormValues) => Promise<void>;
};

export function ExecutionExerciseForm({
  exercises,
  nextOrder,
  onSubmit,
}: ExecutionExerciseFormProps) {
  const hasExercises = exercises.length > 0;
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<SessionExerciseFormValues>({
    resolver: zodResolver(sessionExerciseSchema),
    defaultValues: {
      exercise_id: "",
      execution_order: String(nextOrder),
      notes: "",
    },
  });

  useEffect(() => {
    reset((values) => ({ ...values, execution_order: String(nextOrder) }));
  }, [nextOrder, reset]);

  async function submit(values: SessionExerciseFormValues) {
    await onSubmit(values);
    reset({
      exercise_id: "",
      execution_order: String(nextOrder + 1),
      notes: "",
    });
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit(submit)}>
      <label className={styles.field}>
        <span>Exercício</span>
        <select disabled={!hasExercises} {...register("exercise_id")}>
          <option value="">
            {hasExercises ? "Selecione" : "Nenhum exercício para esta skill"}
          </option>
          {exercises.map((exercise) => (
            <option key={exercise.id} value={exercise.id}>
              {exercise.name}
            </option>
          ))}
        </select>
        {errors.exercise_id ? <small>{errors.exercise_id.message}</small> : null}
      </label>

      <label className={styles.field}>
        <span>Ordem</span>
        <input min="1" type="number" {...register("execution_order")} />
        {errors.execution_order ? <small>{errors.execution_order.message}</small> : null}
      </label>

      <label className={styles.field}>
        <span>Notas</span>
        <input placeholder="Objetivo, variação, ajuste..." type="text" {...register("notes")} />
      </label>

      <button type="submit" disabled={isSubmitting || !hasExercises}>
        {isSubmitting ? "Adicionando..." : "Adicionar"}
      </button>
    </form>
  );
}
