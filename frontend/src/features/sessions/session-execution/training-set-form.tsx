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
    rest_time: z.string().optional().default(""),
    notes: z.string().optional().default(""),
  })
  .refine((values) => values.rpe === "" || (Number(values.rpe) >= 0 && Number(values.rpe) <= 10), {
    message: "RPE precisa ser entre 0 e 10.",
    path: ["rpe"],
  })
  .refine((values) => values.rest_time === "" || /^\d{1,3}:[0-5]\d$/.test(values.rest_time), {
    message: "Use o formato mm:ss, por exemplo 2:30.",
    path: ["rest_time"],
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
    rest_time: initialValues?.rest_time ?? "",
    notes: initialValues?.notes ?? "",
  };
}

function clampNumberString(value: string, max: number) {
  if (value === "") {
    return "";
  }

  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) {
    return "";
  }

  return String(Math.min(max, Math.max(0, numericValue)));
}

function formatRestTimeInput(value: string) {
  if (value.includes(":")) {
    const [minutes = "", seconds = ""] = value.split(":");
    return `${minutes.replace(/\D/g, "").slice(0, 3)}:${seconds.replace(/\D/g, "").slice(0, 2)}`;
  }

  const digits = value.replace(/\D/g, "").slice(0, 5);
  if (digits.length <= 2) {
    return digits;
  }

  return `${digits.slice(0, -2)}:${digits.slice(-2)}`;
}

function normalizeRestTime(value: string) {
  const formattedValue = formatRestTimeInput(value);
  if (!formattedValue) {
    return "";
  }

  const [minutesValue, secondsValue = ""] = formattedValue.split(":");
  const minutes = Number(minutesValue || "0");
  const seconds = Number(secondsValue.padStart(2, "0"));

  if (!Number.isFinite(minutes) || !Number.isFinite(seconds)) {
    return "";
  }

  return `${Math.min(minutes, 600)}:${String(Math.min(seconds, 59)).padStart(2, "0")}`;
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
    setValue,
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
        {...register("rpe", {
          onChange: (event) => {
            setValue("rpe", clampNumberString(event.target.value, 10), {
              shouldValidate: true,
            });
          },
        })}
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
        aria-label="Tempo de descanso"
        inputMode="numeric"
        placeholder="Descanso"
        type="text"
        {...register("rest_time", {
          onBlur: (event) => {
            setValue("rest_time", normalizeRestTime(event.target.value), {
              shouldValidate: true,
            });
          },
          onChange: (event) => {
            setValue("rest_time", formatRestTimeInput(event.target.value));
          },
        })}
      />
      {errors.rpe ? <small>{errors.rpe.message}</small> : null}
      {errors.rest_time ? <small>{errors.rest_time.message}</small> : null}
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
