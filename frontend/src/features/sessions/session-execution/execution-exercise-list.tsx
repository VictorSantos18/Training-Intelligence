"use client";

import type { SessionExercise, TrainingSet, TrainingSetFormValues } from "@/types";

import { TrainingSetForm } from "./training-set-form";
import styles from "./execution-exercise-list.module.css";

type ExecutionExerciseListProps = {
  exerciseNameById: Record<string, string>;
  isSessionOpen: boolean;
  sessionExercises: SessionExercise[];
  setsBySessionExercise: Record<string, TrainingSet[]>;
  onCreateSet: (sessionExerciseId: string, values: TrainingSetFormValues) => Promise<void>;
};

const resultLabels = {
  SUCCESS: "Sucesso",
  PARTIAL: "Parcial",
  FAILED: "Falha",
  SKIPPED: "Pulada",
};

export function ExecutionExerciseList({
  exerciseNameById,
  isSessionOpen,
  sessionExercises,
  setsBySessionExercise,
  onCreateSet,
}: ExecutionExerciseListProps) {
  if (sessionExercises.length === 0) {
    return <p className={styles.empty}>Nenhum exercicio adicionado nesta sessao.</p>;
  }

  return (
    <div className={styles.list}>
      {sessionExercises.map((sessionExercise) => {
        const sets = setsBySessionExercise[sessionExercise.id] ?? [];

        return (
          <article className={styles.card} key={sessionExercise.id}>
            <header className={styles.header}>
              <span>#{sessionExercise.execution_order}</span>
              <div>
                <h5>{exerciseNameById[sessionExercise.exercise_id] ?? "Exercicio"}</h5>
                {sessionExercise.notes ? <p>{sessionExercise.notes}</p> : null}
              </div>
            </header>

            <div className={styles.sets}>
              {sets.length === 0 ? (
                <p className={styles.emptyInline}>Nenhum set registrado.</p>
              ) : (
                sets.map((set) => (
                  <article className={styles.setCard} key={set.id}>
                    <div className={styles.setRow}>
                      <strong>Set {set.set_number}</strong>
                      <span>{resultLabels[set.result]}</span>
                      <span>
                        {set.repetitions ?? "-"} reps / {set.duration_seconds ?? "-"}s
                      </span>
                      <span>RPE {set.rpe ?? "-"}</span>
                    </div>
                    {set.notes ? <p className={styles.setNotes}>{set.notes}</p> : null}
                  </article>
                ))
              )}
            </div>

            {isSessionOpen ? (
              <TrainingSetForm
                nextSetNumber={sets.length + 1}
                onSubmit={(values) => onCreateSet(sessionExercise.id, values)}
              />
            ) : null}
          </article>
        );
      })}
    </div>
  );
}
