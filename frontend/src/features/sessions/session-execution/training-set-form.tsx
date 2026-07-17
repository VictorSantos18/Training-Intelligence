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
    pain_during: z.string().optional().default(""),
    result: z.enum(["SUCCESS", "PARTIAL", "FAILED", "SKIPPED"]),
    technical_quality: z.enum(["", "EXCELLENT", "GOOD", "ACCEPTABLE", "POOR"]),
    rest_seconds: z.string().optional().default(""),
    notes: z.string().optional().default(""),
  })
  .refine(
    (values) =>
      values.result === "SKIPPED" || values.repetitions !== "" || values.duration_seconds !== "",
    {
      message: "Informe repeticoes ou duracao, salvo se o set foi pulado.",
      path: ["duration_seconds"],
    },
  );

type TrainingSetFormProps = {
  nextSetNumber: number;
  onSubmit: (values: TrainingSetFormValues) => Promise<void>;
};

export function TrainingSetForm({ nextSetNumber, onSubmit }: TrainingSetFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<TrainingSetFormValues>({
    resolver: zodResolver(setSchema),
    defaultValues: {
      set_number: String(nextSetNumber),
      repetitions: "",
      duration_seconds: "",
      assistance_level: "",
      rpe: "",
      pain_during: "",
      result: "SUCCESS",
      technical_quality: "",
      rest_seconds: "",
      notes: "",
    },
  });

  useEffect(() => {
    reset((values) => ({ ...values, set_number: String(nextSetNumber) }));
  }, [nextSetNumber, reset]);

  async function submit(values: TrainingSetFormValues) {
    await onSubmit(values);
    reset({
      set_number: String(nextSetNumber + 1),
      repetitions: "",
      duration_seconds: "",
      assistance_level: "",
      rpe: "",
      pain_during: "",
      result: "SUCCESS",
      technical_quality: "",
      rest_seconds: "",
      notes: "",
    });
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit(submit)}>
      <input aria-label="Numero do set" min="1" type="number" {...register("set_number")} />
      <input aria-label="Repeticoes" min="0" placeholder="Reps" type="number" {...register("repetitions")} />
      <input
        aria-label="Duracao em segundos"
        min="0"
        placeholder="Segundos"
        step="0.01"
        type="number"
        {...register("duration_seconds")}
      />
      <input aria-label="RPE" max="10" min="0" placeholder="RPE" step="0.1" type="number" {...register("rpe")} />
      <input
        aria-label="Dor durante"
        max="10"
        min="0"
        placeholder="Dor"
        type="number"
        {...register("pain_during")}
      />
      <select aria-label="Resultado" {...register("result")}>
        <option value="SUCCESS">Sucesso</option>
        <option value="PARTIAL">Parcial</option>
        <option value="FAILED">Falha</option>
        <option value="SKIPPED">Pulada</option>
      </select>
      <select aria-label="Qualidade tecnica" {...register("technical_quality")}>
        <option value="">Qualidade</option>
        <option value="EXCELLENT">Excelente</option>
        <option value="GOOD">Boa</option>
        <option value="ACCEPTABLE">Aceitavel</option>
        <option value="POOR">Ruim</option>
      </select>
      <input
        aria-label="Descanso em segundos"
        min="0"
        placeholder="Descanso"
        type="number"
        {...register("rest_seconds")}
      />
      <input aria-label="Notas do set" placeholder="Notas" type="text" {...register("notes")} />
      {errors.duration_seconds ? <small>{errors.duration_seconds.message}</small> : null}
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Salvando..." : "Registrar set"}
      </button>
    </form>
  );
}
