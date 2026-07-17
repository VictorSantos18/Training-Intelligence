"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import {
  createPainRecord,
  createSessionExercise,
  createTrainingSet,
  listBodyRegions,
  listExercises,
  listPainRecords,
  listSessionExercises,
  listTrainingSets,
} from "@/lib/api";
import type {
  BodyRegion,
  Exercise,
  PainRecord,
  PainRecordFormValues,
  SessionExercise,
  SessionExerciseFormValues,
  TrainingSession,
  TrainingSet,
  TrainingSetFormValues,
} from "@/types";

import { ExecutionExerciseForm } from "./session-execution/execution-exercise-form";
import { ExecutionExerciseList } from "./session-execution/execution-exercise-list";
import { PainRecordForm } from "./session-execution/pain-record-form";
import styles from "./session-execution-panel.module.css";

type SessionExecutionPanelProps = {
  accessToken: string;
  session: TrainingSession;
};

function emptyToNull(value: string) {
  const trimmedValue = value.trim();
  return trimmedValue ? trimmedValue : null;
}

function numberOrNull(value: string) {
  const trimmedValue = value.trim();
  return trimmedValue ? Number(trimmedValue) : null;
}

function decimalOrNull(value: string) {
  const trimmedValue = value.trim();
  return trimmedValue ? trimmedValue : null;
}

function buildTrainingSetPayload(values: TrainingSetFormValues) {
  return {
    set_number: Number(values.set_number),
    repetitions: numberOrNull(values.repetitions),
    duration_seconds: decimalOrNull(values.duration_seconds),
    assistance_level: decimalOrNull(values.assistance_level),
    rpe: decimalOrNull(values.rpe),
    pain_during: numberOrNull(values.pain_during),
    result: values.result,
    technical_quality: values.technical_quality || null,
    rest_seconds: numberOrNull(values.rest_seconds),
    notes: emptyToNull(values.notes),
  };
}

function buildPainRecordPayload(sessionId: string, values: PainRecordFormValues) {
  return {
    training_session_id: sessionId,
    training_set_id: values.training_set_id || null,
    body_region_id: values.body_region_id,
    side: values.side,
    moment: values.moment,
    intensity: Number(values.intensity),
    description: emptyToNull(values.description),
    notes: emptyToNull(values.notes),
  };
}

export function SessionExecutionPanel({ accessToken, session }: SessionExecutionPanelProps) {
  const [availableExercises, setAvailableExercises] = useState<Exercise[]>([]);
  const [bodyRegions, setBodyRegions] = useState<BodyRegion[]>([]);
  const [sessionExercises, setSessionExercises] = useState<SessionExercise[]>([]);
  const [setsBySessionExercise, setSetsBySessionExercise] = useState<Record<string, TrainingSet[]>>(
    {},
  );
  const [painRecords, setPainRecords] = useState<PainRecord[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const isSessionOpen = session.status === "IN_PROGRESS";

  const loadExecution = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [exercisesData, regionsData, sessionExercisesData, painRecordsData] =
        await Promise.all([
          listExercises(accessToken, {
            isActive: true,
            skillId: session.skill_id ?? undefined,
          }),
          listBodyRegions(accessToken),
          listSessionExercises(accessToken, session.id),
          listPainRecords(accessToken, { trainingSessionId: session.id }),
        ]);

      const setPairs = await Promise.all(
        sessionExercisesData.map(async (sessionExercise) => {
          const sets = await listTrainingSets(accessToken, sessionExercise.id);
          return [sessionExercise.id, sets] as const;
        }),
      );

      setAvailableExercises(exercisesData);
      setBodyRegions(regionsData);
      setSessionExercises(sessionExercisesData);
      setPainRecords(painRecordsData);
      setSetsBySessionExercise(Object.fromEntries(setPairs));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel carregar o treino.");
    } finally {
      setIsLoading(false);
    }
  }, [accessToken, session.id, session.skill_id]);

  useEffect(() => {
    void loadExecution();
  }, [loadExecution]);

  const exerciseNameById = useMemo(() => {
    return availableExercises.reduce<Record<string, string>>((acc, exercise) => {
      acc[exercise.id] = exercise.name;
      return acc;
    }, {});
  }, [availableExercises]);

  const selectableExercises = useMemo(() => {
    return availableExercises.filter((exercise) => exercise.skill_id === session.skill_id);
  }, [availableExercises, session.skill_id]);

  const bodyRegionNameById = useMemo(() => {
    return bodyRegions.reduce<Record<string, string>>((acc, region) => {
      acc[region.id] = region.name;
      return acc;
    }, {});
  }, [bodyRegions]);

  const allSets = useMemo(() => {
    return Object.values(setsBySessionExercise).flat();
  }, [setsBySessionExercise]);

  async function handleCreateSessionExercise(values: SessionExerciseFormValues) {
    setFeedback(null);
    setError(null);

    try {
      const createdSessionExercise = await createSessionExercise(accessToken, session.id, {
        exercise_id: values.exercise_id,
        execution_order: Number(values.execution_order),
        notes: emptyToNull(values.notes),
      });
      setSessionExercises((current) => [...current, createdSessionExercise]);
      setSetsBySessionExercise((current) => ({
        ...current,
        [createdSessionExercise.id]: [],
      }));
      setFeedback("Exercicio adicionado ao treino.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel adicionar exercicio.");
    }
  }

  async function handleCreateTrainingSet(
    sessionExerciseId: string,
    values: TrainingSetFormValues,
  ) {
    setFeedback(null);
    setError(null);

    try {
      const createdSet = await createTrainingSet(
        accessToken,
        sessionExerciseId,
        buildTrainingSetPayload(values),
      );
      setSetsBySessionExercise((current) => ({
        ...current,
        [sessionExerciseId]: [...(current[sessionExerciseId] ?? []), createdSet],
      }));
      setFeedback("Set registrado.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel registrar o set.");
    }
  }

  async function handleCreatePainRecord(values: PainRecordFormValues) {
    setFeedback(null);
    setError(null);

    try {
      const createdPainRecord = await createPainRecord(
        accessToken,
        buildPainRecordPayload(session.id, values),
      );
      setPainRecords((current) => [createdPainRecord, ...current]);
      setFeedback("Dor registrada.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel registrar dor.");
    }
  }

  return (
    <section className={styles.panel}>
      <header className={styles.header}>
        <div>
          <h3>Treino em execucao</h3>
          <p>Monte a sessao, registre sets e acompanhe desconfortos.</p>
        </div>
        <button type="button" onClick={loadExecution}>
          Atualizar
        </button>
      </header>

      {feedback ? <p className={styles.success}>{feedback}</p> : null}
      {error ? <p className={styles.error}>{error}</p> : null}

      {isLoading ? (
        <p className={styles.empty}>Carregando dados do treino...</p>
      ) : (
        <div className={styles.grid}>
          <div className={styles.column}>
            <h4>Exercicios da sessao</h4>
            {isSessionOpen ? (
              <ExecutionExerciseForm
                exercises={selectableExercises}
                nextOrder={sessionExercises.length + 1}
                onSubmit={handleCreateSessionExercise}
              />
            ) : (
              <p className={styles.locked}>Sessao fechada. Edicao estrutural bloqueada.</p>
            )}

            <ExecutionExerciseList
              exerciseNameById={exerciseNameById}
              isSessionOpen={isSessionOpen}
              sessionExercises={sessionExercises}
              setsBySessionExercise={setsBySessionExercise}
              onCreateSet={handleCreateTrainingSet}
            />
          </div>

          <div className={styles.column}>
            <h4>Dor e desconforto</h4>
            <PainRecordForm
              bodyRegions={bodyRegions}
              sets={allSets}
              onSubmit={handleCreatePainRecord}
            />

            <div className={styles.painList}>
              {painRecords.length === 0 ? (
                <p className={styles.empty}>Nenhum registro de dor nesta sessao.</p>
              ) : (
                painRecords.map((record) => (
                  <article className={styles.painCard} key={record.id}>
                    <strong>{bodyRegionNameById[record.body_region_id] ?? "Regiao"}</strong>
                    <span>
                      {record.moment} - intensidade {record.intensity}/10
                    </span>
                    {record.notes ? <p>{record.notes}</p> : null}
                  </article>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
