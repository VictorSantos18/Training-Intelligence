"use client";

import type { FormEvent } from "react";

import type { AnalysisReportFormValues, Skill } from "@/types";

import styles from "./analysis-report-form.module.css";

type AnalysisReportFormProps = {
  skills: Skill[];
  values: AnalysisReportFormValues;
  isSubmitting: boolean;
  onChange: (values: AnalysisReportFormValues) => void;
  onSubmit: () => void;
};

export function AnalysisReportForm({
  skills,
  values,
  isSubmitting,
  onChange,
  onSubmit,
}: AnalysisReportFormProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <label>
        <span>Início</span>
        <input
          required
          type="date"
          value={values.period_start}
          onChange={(event) => onChange({ ...values, period_start: event.target.value })}
        />
      </label>

      <label>
        <span>Fim</span>
        <input
          required
          type="date"
          value={values.period_end}
          onChange={(event) => onChange({ ...values, period_end: event.target.value })}
        />
      </label>

      <label>
        <span>Skill</span>
        <select
          value={values.skill_id}
          onChange={(event) => onChange({ ...values, skill_id: event.target.value })}
        >
          <option value="">Todas</option>
          {skills.map((skill) => (
            <option key={skill.id} value={skill.id}>
              {skill.name}
            </option>
          ))}
        </select>
      </label>

      <label>
        <span>Título</span>
        <input
          maxLength={160}
          placeholder="Opcional"
          type="text"
          value={values.title}
          onChange={(event) => onChange({ ...values, title: event.target.value })}
        />
      </label>

      <button disabled={isSubmitting} type="submit">
        {isSubmitting ? "Gerando..." : "Gerar relatório"}
      </button>
    </form>
  );
}
