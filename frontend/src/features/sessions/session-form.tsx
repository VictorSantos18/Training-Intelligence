"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import type { Skill, TrainingSessionFormValues } from "@/types";

import { toDatetimeLocalValue } from "./session-formatters";
import styles from "./session-form.module.css";

const zeroToTenString = z
  .string()
  .refine((value) => value === "" || (Number(value) >= 0 && Number(value) <= 10), {
    message: "Use um valor de 0 a 10.",
  });

const sessionFormSchema = z.object({
  skill_id: z.string().optional().default(""),
  started_at: z.string().min(1, "Informe o início da sessão."),
  sleep_hours: z
    .string()
    .refine((value) => value === "" || (Number(value) >= 0 && Number(value) <= 24), {
      message: "Use um valor entre 0 e 24.",
    }),
  energy_before: zeroToTenString,
});

type SessionFormProps = {
  skills: Skill[];
  onSubmit: (values: TrainingSessionFormValues) => Promise<void>;
};

export function SessionForm({ skills, onSubmit }: SessionFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<TrainingSessionFormValues>({
    resolver: zodResolver(sessionFormSchema),
    defaultValues: {
      skill_id: "",
      started_at: toDatetimeLocalValue(),
      sleep_hours: "",
      energy_before: "",
    },
  });

  async function submit(values: TrainingSessionFormValues) {
    await onSubmit(values);
    reset({
      skill_id: "",
      started_at: toDatetimeLocalValue(),
      sleep_hours: "",
      energy_before: "",
    });
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit(submit)}>
      <label className={styles.field}>
        <span>Skill</span>
        <select className={styles.input} {...register("skill_id")}>
          <option value="">Sessão geral</option>
          {skills.map((skill) => (
            <option key={skill.id} value={skill.id}>
              {skill.name}
            </option>
          ))}
        </select>
      </label>

      <label className={styles.field}>
        <span>Início</span>
        <input className={styles.input} type="datetime-local" {...register("started_at")} />
        {errors.started_at ? (
          <small className={styles.error}>{errors.started_at.message}</small>
        ) : null}
      </label>

      <div className={styles.grid}>
        <label className={styles.field}>
          <span>Sono h</span>
          <input
            className={styles.input}
            max="24"
            min="0"
            step="0.25"
            type="number"
            {...register("sleep_hours")}
          />
          {errors.sleep_hours ? (
            <small className={styles.error}>{errors.sleep_hours.message}</small>
          ) : null}
        </label>

        <label className={styles.field}>
          <span>Energia</span>
          <input
            className={styles.input}
            max="10"
            min="0"
            type="number"
            {...register("energy_before")}
          />
          {errors.energy_before ? (
            <small className={styles.error}>{errors.energy_before.message}</small>
          ) : null}
        </label>
      </div>

      <button className={styles.submit} type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Criando..." : "Criar sessão"}
      </button>
    </form>
  );
}
