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
  started_at: z.string().min(1, "Informe o inicio da sessao."),
  body_weight_kg: z.string().optional().default(""),
  sleep_hours: z
    .string()
    .refine((value) => value === "" || (Number(value) >= 0 && Number(value) <= 24), {
      message: "Use um valor entre 0 e 24.",
    }),
  sleep_quality: zeroToTenString,
  energy_before: zeroToTenString,
  motivation_before: zeroToTenString,
  fatigue_before: zeroToTenString,
  notes_before: z.string().optional().default(""),
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
      body_weight_kg: "",
      sleep_hours: "",
      sleep_quality: "",
      energy_before: "",
      motivation_before: "",
      fatigue_before: "",
      notes_before: "",
    },
  });

  async function submit(values: TrainingSessionFormValues) {
    await onSubmit(values);
    reset({
      skill_id: "",
      started_at: toDatetimeLocalValue(),
      body_weight_kg: "",
      sleep_hours: "",
      sleep_quality: "",
      energy_before: "",
      motivation_before: "",
      fatigue_before: "",
      notes_before: "",
    });
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit(submit)}>
      <label className={styles.field}>
        <span>Skill</span>
        <select className={styles.input} {...register("skill_id")}>
          <option value="">Sessao geral</option>
          {skills.map((skill) => (
            <option key={skill.id} value={skill.id}>
              {skill.name}
            </option>
          ))}
        </select>
      </label>

      <label className={styles.field}>
        <span>Inicio</span>
        <input className={styles.input} type="datetime-local" {...register("started_at")} />
        {errors.started_at ? (
          <small className={styles.error}>{errors.started_at.message}</small>
        ) : null}
      </label>

      <div className={styles.grid}>
        <label className={styles.field}>
          <span>Peso kg</span>
          <input className={styles.input} min="0" step="0.01" type="number" {...register("body_weight_kg")} />
        </label>

        <label className={styles.field}>
          <span>Sono h</span>
          <input className={styles.input} min="0" max="24" step="0.25" type="number" {...register("sleep_hours")} />
          {errors.sleep_hours ? (
            <small className={styles.error}>{errors.sleep_hours.message}</small>
          ) : null}
        </label>
      </div>

      <div className={styles.grid}>
        <label className={styles.field}>
          <span>Qualidade sono</span>
          <input className={styles.input} min="0" max="10" type="number" {...register("sleep_quality")} />
          {errors.sleep_quality ? (
            <small className={styles.error}>{errors.sleep_quality.message}</small>
          ) : null}
        </label>

        <label className={styles.field}>
          <span>Energia</span>
          <input className={styles.input} min="0" max="10" type="number" {...register("energy_before")} />
          {errors.energy_before ? (
            <small className={styles.error}>{errors.energy_before.message}</small>
          ) : null}
        </label>
      </div>

      <div className={styles.grid}>
        <label className={styles.field}>
          <span>Motivacao</span>
          <input className={styles.input} min="0" max="10" type="number" {...register("motivation_before")} />
          {errors.motivation_before ? (
            <small className={styles.error}>{errors.motivation_before.message}</small>
          ) : null}
        </label>

        <label className={styles.field}>
          <span>Fadiga</span>
          <input className={styles.input} min="0" max="10" type="number" {...register("fatigue_before")} />
          {errors.fatigue_before ? (
            <small className={styles.error}>{errors.fatigue_before.message}</small>
          ) : null}
        </label>
      </div>

      <label className={styles.field}>
        <span>Notas antes</span>
        <textarea
          className={styles.textarea}
          placeholder="Contexto, desconfortos, foco do treino..."
          rows={4}
          {...register("notes_before")}
        />
      </label>

      <button className={styles.submit} type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Criando..." : "Criar sessao"}
      </button>
    </form>
  );
}
