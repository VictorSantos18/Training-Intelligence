"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import type { Skill, SkillFormValues, SkillStatus } from "@/types";

import styles from "./skill-form.module.css";

const skillStatuses: Array<{ value: SkillStatus; label: string }> = [
  { value: "ACTIVE", label: "Ativa" },
  { value: "PAUSED", label: "Pausada" },
  { value: "ACHIEVED", label: "Conquistada" },
];

const skillFormSchema = z.object({
  name: z.string().trim().min(1, "Informe o nome da skill.").max(120),
  description: z.string().max(1000).optional().default(""),
  status: z.enum(["ACTIVE", "PAUSED", "ACHIEVED"]),
});

type SkillFormProps = {
  initialSkill?: Skill;
  submitLabel: string;
  onCancel?: () => void;
  onSubmit: (values: SkillFormValues) => Promise<void>;
};

function getDefaultValues(skill?: Skill): SkillFormValues {
  return {
    name: skill?.name ?? "",
    description: skill?.description ?? "",
    status: skill?.status ?? "ACTIVE",
  };
}

export function SkillForm({ initialSkill, submitLabel, onCancel, onSubmit }: SkillFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<SkillFormValues>({
    resolver: zodResolver(skillFormSchema),
    defaultValues: getDefaultValues(initialSkill),
  });

  useEffect(() => {
    reset(getDefaultValues(initialSkill));
  }, [initialSkill, reset]);

  async function submit(values: SkillFormValues) {
    await onSubmit(values);
    if (!initialSkill) {
      reset(getDefaultValues());
    }
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit(submit)}>
      <label className={styles.field}>
        <span>Nome</span>
        <input
          className={styles.input}
          placeholder="Front Lever"
          type="text"
          {...register("name")}
        />
        {errors.name ? <small className={styles.error}>{errors.name.message}</small> : null}
      </label>

      <label className={styles.field}>
        <span>Descrição</span>
        <textarea
          className={styles.textarea}
          placeholder="Objetivo tecnico, foco atual ou contexto."
          rows={4}
          {...register("description")}
        />
        {errors.description ? (
          <small className={styles.error}>{errors.description.message}</small>
        ) : null}
      </label>

      <label className={styles.field}>
        <span>Status</span>
        <select className={styles.select} {...register("status")}>
          {skillStatuses.map((status) => (
            <option key={status.value} value={status.value}>
              {status.label}
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
