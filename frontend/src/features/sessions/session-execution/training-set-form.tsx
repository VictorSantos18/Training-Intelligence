"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import type { TrainingSetFormValues } from "@/types";

import styles from "./training-set-form.module.css";

const setSchema = z
  .object({
    set_number: z.string().min(1),
    repetitions: z.string().optional().default(""),
    duration_seconds: z.string().optional().default(""),
    assistance_level: z.string().optional().default(""),
    rpe: z.string().optional().default(""),
    result: z.enum(["SUCCESS", "PARTIAL", "FAILED", "SKIPPED"]),
    technical_quality: z.enum(["", "EXCELLENT", "GOOD", "ACCEPTABLE", "POOR"]),
    rest_seconds: z.string().optional().default(""),
    notes: z.string().optional().default(""),
  })
  .refine(
    (values) =>
      values.result === "SKIPPED" || values.repetitions !== "" || values.duration_seconds !== "",
    {
      message: "Informe repetições ou duração, salvo se o set foi pulado.",
      path: ["duration_seconds"],
    },
  );

type TrainingSetFormProps = {
  initialValues?: TrainingSetFormValues;
  nextSetNumber: number;
  resetOnSubmit?: boolean;
  submitLabel?: string;
  submittingLabel?: string;
  onSubmit: (values: TrainingSetFormValues) => Promise<void>;
};

function getDefaultValues(nextSetNumber: number, initialValues?: TrainingSetFormValues) {
  return {
    set_number: initialValues?.set_number ?? String(nextSetNumber),
    repetitions: initialValues?.repetitions ?? "",
    duration_seconds: initialValues?.duration_seconds ?? "",
    assistance_level: initialValues?.assistance_level ?? "",
    rpe: initialValues?.rpe ?? "",
    result: initialValues?.result ?? "SUCCESS",
    technical_quality: initialValues?.technical_quality ?? "",
    rest_seconds: initialValues?.rest_seconds ?? "",
    notes: initialValues?.notes ?? "",
  };
}

export function TrainingSetForm({
  initialValues,
  nextSetNumber,
  resetOnSubmit = true,
  submitLabel = "Registrar set",
  submittingLabel = "Salvando...",
  onSubmit,
}: TrainingSetFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<TrainingSetFormValues>({
    resolver: zodResolver(setSchema),
    defaultValues: getDefaultValues(nextSetNumber, initialValues),
  });

  useEffect(() => {
    reset(getDefaultValues(nextSetNumber, initialValues));
  }, [initialValues, nextSetNumber, reset]);

  async function submit(values: TrainingSetFormValues) {
    await onSubmit(values);
    if (resetOnSubmit) {
      reset(getDefaultValues(nextSetNumber + 1));
    }
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit(submit)}>
      <input aria-label="Número do set" min="1" type="number" {...register("set_number")} />
      <input
        aria-label="Repetições"
        min="0"
        placeholder="Reps"
        type="number"
        {...register("repetitions")}
      />
      <input
        aria-label="Duração em segundos"
        min="0"
        placeholder="Segundos"
        step="0.01"
        type="number"
        {...register("duration_seconds")}
      />
      <input
        aria-label="RPE"
        max="10"
        min="0"
        placeholder="RPE"
        step="0.1"
        type="number"
        {...register("rpe")}
      />
      <select aria-label="Resultado" {...register("result")}>
        <option value="SUCCESS">Sucesso</option>
        <option value="PARTIAL">Parcial</option>
        <option value="FAILED">Falha</option>
        <option value="SKIPPED">Pulada</option>
      </select>
      <select aria-label="Qualidade técnica" {...register("technical_quality")}>
        <option value="">Qualidade</option>
        <option value="EXCELLENT">Excelente</option>
        <option value="GOOD">Boa</option>
        <option value="ACCEPTABLE">Aceitável</option>
        <option value="POOR">Ruim</option>
      </select>
      <input
        aria-label="Descanso em segundos"
        min="0"
        placeholder="Descanso"
        type="number"
        {...register("rest_seconds")}
      />
      <input
        aria-label="Notas do set"
        className={styles.notesInput}
        placeholder="Notas"
        type="text"
        {...register("notes")}
      />
      {errors.duration_seconds ? <small>{errors.duration_seconds.message}</small> : null}
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? submittingLabel : submitLabel}
      </button>
    </form>
  );
}
