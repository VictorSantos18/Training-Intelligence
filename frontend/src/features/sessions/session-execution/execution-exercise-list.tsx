"use client";

import { useState } from "react";

import type {
  SessionExercise,
  SessionExerciseFormValues,
  TrainingSet,
  TrainingSetFormValues,
} from "@/types";

import { SessionExerciseEditForm } from "./session-exercise-edit-form";
import { TrainingSetForm } from "./training-set-form";
import styles from "./execution-exercise-list.module.css";

type ExecutionExerciseListProps = {
  exerciseNameById: Record<string, string>;
  isSessionOpen: boolean;
  sessionExercises: SessionExercise[];
  setsBySessionExercise: Record<string, TrainingSet[]>;
  onCreateSet: (sessionExerciseId: string, values: TrainingSetFormValues) => Promise<void>;
  onDeleteSessionExercise: (sessionExercise: SessionExercise) => void;
  onDeleteSet: (sessionExerciseId: string, set: TrainingSet) => void;
  onUpdateSessionExercise: (
    sessionExerciseId: string,
    values: SessionExerciseFormValues,
  ) => Promise<void>;
  onUpdateSet: (
    sessionExerciseId: string,
    setId: string,
    values: TrainingSetFormValues,
  ) => Promise<void>;
};

const resultLabels = {
  SUCCESS: "Sucesso",
  PARTIAL: "Parcial",
  FAILED: "Falha",
  SKIPPED: "Pulada",
};

function getSessionExerciseFormValues(sessionExercise: SessionExercise): SessionExerciseFormValues {
  return {
    exercise_id: sessionExercise.exercise_id,
    execution_order: String(sessionExercise.execution_order),
    notes: sessionExercise.notes ?? "",
  };
}

function getTrainingSetFormValues(set: TrainingSet): TrainingSetFormValues {
  return {
    set_number: String(set.set_number),
    repetitions: set.repetitions === null ? "" : String(set.repetitions),
    duration_seconds: set.duration_seconds ?? "",
    assistance_level: set.assistance_level ?? "",
    rpe: set.rpe ?? "",
    pain_during: set.pain_during === null ? "" : String(set.pain_during),
    result: set.result,
    technical_quality: set.technical_quality ?? "",
    rest_seconds: set.rest_seconds === null ? "" : String(set.rest_seconds),
    notes: set.notes ?? "",
  };
}

export function ExecutionExerciseList({
  exerciseNameById,
  isSessionOpen,
  sessionExercises,
  setsBySessionExercise,
  onCreateSet,
  onDeleteSessionExercise,
  onDeleteSet,
  onUpdateSessionExercise,
  onUpdateSet,
}: ExecutionExerciseListProps) {
  const [editingSessionExerciseId, setEditingSessionExerciseId] = useState<string | null>(null);
  const [editingSetId, setEditingSetId] = useState<string | null>(null);

  if (sessionExercises.length === 0) {
    return <p className={styles.empty}>Nenhum exercício adicionado nesta sessão.</p>;
  }

  return (
    <div className={styles.list}>
      {sessionExercises.map((sessionExercise) => {
        const sets = setsBySessionExercise[sessionExercise.id] ?? [];
        const isEditingSessionExercise = editingSessionExerciseId === sessionExercise.id;

        return (
          <article className={styles.card} key={sessionExercise.id}>
            <header className={styles.header}>
              <span>#{sessionExercise.execution_order}</span>
              <div>
                <h5>{exerciseNameById[sessionExercise.exercise_id] ?? "Exercício"}</h5>
                {sessionExercise.notes ? <p>{sessionExercise.notes}</p> : null}
              </div>

              {isSessionOpen ? (
                <div className={styles.actions}>
                  <button
                    type="button"
                    onClick={() =>
                      setEditingSessionExerciseId(
                        isEditingSessionExercise ? null : sessionExercise.id,
                      )
                    }
                  >
                    {isEditingSessionExercise ? "Fechar" : "Editar"}
                  </button>
                  <button
                    className={styles.danger}
                    type="button"
                    onClick={() => onDeleteSessionExercise(sessionExercise)}
                  >
                    Excluir
                  </button>
                </div>
              ) : null}
            </header>

            {isEditingSessionExercise ? (
              <SessionExerciseEditForm
                initialValues={getSessionExerciseFormValues(sessionExercise)}
                onCancel={() => setEditingSessionExerciseId(null)}
                onSubmit={async (values) => {
                  await onUpdateSessionExercise(sessionExercise.id, values);
                  setEditingSessionExerciseId(null);
                }}
              />
            ) : null}

            <div className={styles.sets}>
              {sets.length === 0 ? (
                <p className={styles.emptyInline}>Nenhum set registrado.</p>
              ) : (
                sets.map((set) => {
                  const isEditingSet = editingSetId === set.id;

                  return (
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

                      {isSessionOpen ? (
                        <div className={styles.inlineActions}>
                          <button
                            type="button"
                            onClick={() => setEditingSetId(isEditingSet ? null : set.id)}
                          >
                            {isEditingSet ? "Fechar edição" : "Editar set"}
                          </button>
                          <button
                            className={styles.danger}
                            type="button"
                            onClick={() => onDeleteSet(sessionExercise.id, set)}
                          >
                            Excluir set
                          </button>
                        </div>
                      ) : null}

                      {isEditingSet ? (
                        <TrainingSetForm
                          initialValues={getTrainingSetFormValues(set)}
                          nextSetNumber={set.set_number}
                          resetOnSubmit={false}
                          submitLabel="Salvar set"
                          onSubmit={async (values) => {
                            await onUpdateSet(sessionExercise.id, set.id, values);
                            setEditingSetId(null);
                          }}
                        />
                      ) : null}
                    </article>
                  );
                })
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
