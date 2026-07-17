"use client";

import { useState } from "react";

import type {
  Exercise,
  ExerciseCategory,
  ExerciseFormValues,
  ExerciseMeasurementType,
  Skill,
} from "@/types";

import { ExerciseForm } from "./exercise-form";
import styles from "./exercise-list.module.css";

type ExerciseListProps = {
  categoryLabels: Record<ExerciseCategory, string>;
  exercises: Exercise[];
  isLoading: boolean;
  measurementLabels: Record<ExerciseMeasurementType, string>;
  skillNameById: Record<string, string>;
  skills: Skill[];
  onDeactivate: (exercise: Exercise) => void;
  onReactivate: (exercise: Exercise) => Promise<void>;
  onUpdate: (exerciseId: string, values: ExerciseFormValues) => Promise<void>;
};

export function ExerciseList({
  categoryLabels,
  exercises,
  isLoading,
  measurementLabels,
  skillNameById,
  skills,
  onDeactivate,
  onReactivate,
  onUpdate,
}: ExerciseListProps) {
  const [editingExerciseId, setEditingExerciseId] = useState<string | null>(null);

  if (isLoading) {
    return <p className={styles.empty}>Carregando exercicios...</p>;
  }

  if (exercises.length === 0) {
    return (
      <div className={styles.emptyState}>
        <h4>Nenhum exercicio encontrado.</h4>
        <p>Crie um exercicio ou ajuste os filtros para consultar registros inativos.</p>
      </div>
    );
  }

  return (
    <div className={styles.list}>
      {exercises.map((exercise) => {
        const isEditing = editingExerciseId === exercise.id;
        const skillLabel = exercise.skill_id
          ? skillNameById[exercise.skill_id] ?? "Skill nao encontrada"
          : "Acessorio geral";

        return (
          <article className={styles.card} key={exercise.id}>
            {isEditing ? (
              <ExerciseForm
                categoryLabels={categoryLabels}
                initialExercise={exercise}
                measurementLabels={measurementLabels}
                skills={skills}
                submitLabel="Salvar alteracoes"
                onCancel={() => setEditingExerciseId(null)}
                onSubmit={async (values) => {
                  await onUpdate(exercise.id, values);
                  setEditingExerciseId(null);
                }}
              />
            ) : (
              <>
                <div className={styles.cardHeader}>
                  <div>
                    <div className={styles.badges}>
                      <span>{categoryLabels[exercise.category]}</span>
                      <span>{measurementLabels[exercise.measurement_type]}</span>
                      <span className={exercise.is_active ? styles.active : styles.inactive}>
                        {exercise.is_active ? "Ativo" : "Inativo"}
                      </span>
                    </div>
                    <h4>{exercise.name}</h4>
                  </div>
                  <p className={styles.skillLabel}>{skillLabel}</p>
                </div>

                <div className={styles.meta}>
                  <span>Criado em {new Date(exercise.created_at).toLocaleDateString("pt-BR")}</span>
                  <span>
                    Atualizado em {new Date(exercise.updated_at).toLocaleDateString("pt-BR")}
                  </span>
                </div>

                <div className={styles.actions}>
                  <button type="button" onClick={() => setEditingExerciseId(exercise.id)}>
                    Editar
                  </button>
                  {exercise.is_active ? (
                    <button
                      className={styles.danger}
                      type="button"
                      onClick={() => onDeactivate(exercise)}
                    >
                      Desativar
                    </button>
                  ) : (
                    <button type="button" onClick={() => void onReactivate(exercise)}>
                      Reativar
                    </button>
                  )}
                </div>
              </>
            )}
          </article>
        );
      })}
    </div>
  );
}
