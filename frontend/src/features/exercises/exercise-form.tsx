"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import type {
  Exercise,
  ExerciseCategory,
  ExerciseFormValues,
  ExerciseMeasurementType,
  Skill,
} from "@/types";

import styles from "./exercise-form.module.css";

const exerciseCategories: ExerciseCategory[] = [
  "HOLD",
  "PRESS",
  "PULL",
  "RAISE",
  "NEGATIVE",
  "ACCESSORY",
];

const measurementTypes: ExerciseMeasurementType[] = ["REPS", "SECONDS", "DISTANCE", "CUSTOM"];

const exerciseFormSchema = z.object({
  skill_id: z.string().optional().default(""),
  name: z.string().trim().min(1, "Informe o nome do exercicio.").max(150),
  category: z.enum(["HOLD", "PRESS", "PULL", "RAISE", "NEGATIVE", "ACCESSORY"]),
  measurement_type: z.enum(["REPS", "SECONDS", "DISTANCE", "CUSTOM"]),
});

type ExerciseFormProps = {
  categoryLabels: Record<ExerciseCategory, string>;
  initialExercise?: Exercise;
  measurementLabels: Record<ExerciseMeasurementType, string>;
  skills: Skill[];
  submitLabel: string;
  onCancel?: () => void;
  onSubmit: (values: ExerciseFormValues) => Promise<void>;
};

function getDefaultValues(exercise?: Exercise): ExerciseFormValues {
  return {
    skill_id: exercise?.skill_id ?? "",
    name: exercise?.name ?? "",
    category: exercise?.category ?? "HOLD",
    measurement_type: exercise?.measurement_type ?? "SECONDS",
  };
}

export function ExerciseForm({
  categoryLabels,
  initialExercise,
  measurementLabels,
  skills,
  submitLabel,
  onCancel,
  onSubmit,
}: ExerciseFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ExerciseFormValues>({
    resolver: zodResolver(exerciseFormSchema),
    defaultValues: getDefaultValues(initialExercise),
  });

  useEffect(() => {
    reset(getDefaultValues(initialExercise));
  }, [initialExercise, reset]);

  async function submit(values: ExerciseFormValues) {
    await onSubmit(values);
    if (!initialExercise) {
      reset(getDefaultValues());
    }
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit(submit)}>
      <label className={styles.field}>
        <span>Skill</span>
        <select className={styles.select} {...register("skill_id")}>
          <option value="">Acessorio geral</option>
          {skills.map((skill) => (
            <option key={skill.id} value={skill.id}>
              {skill.name}
            </option>
          ))}
        </select>
      </label>

      <label className={styles.field}>
        <span>Nome</span>
        <input
          className={styles.input}
          placeholder="Front Lever Hold"
          type="text"
          {...register("name")}
        />
        {errors.name ? <small className={styles.error}>{errors.name.message}</small> : null}
      </label>

      <label className={styles.field}>
        <span>Categoria</span>
        <select className={styles.select} {...register("category")}>
          {exerciseCategories.map((category) => (
            <option key={category} value={category}>
              {categoryLabels[category]}
            </option>
          ))}
        </select>
      </label>

      <label className={styles.field}>
        <span>Medicao principal</span>
        <select className={styles.select} {...register("measurement_type")}>
          {measurementTypes.map((measurementType) => (
            <option key={measurementType} value={measurementType}>
              {measurementLabels[measurementType]}
            </option>
          ))}
        </select>
      </label>

      <div className={styles.actions}>
        {onCancel ? (
          <button className={styles.secondary} type="button" onClick={onCancel}>
            Cancelar
          </button>
        ) : null}
        <button className={styles.primary} type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Salvando..." : submitLabel}
        </button>
      </div>
    </form>
  );
}
