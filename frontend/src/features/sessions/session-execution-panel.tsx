"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import {
  createPainRecord,
  createSessionExercise,
  createTrainingSet,
  deletePainRecord,
  deleteSessionExercise,
  deleteTrainingSet,
  listBodyRegions,
  listExercises,
  listPainRecords,
  listSessionExercises,
  listTrainingSets,
  updatePainRecord,
  updateSessionExercise,
  updateTrainingSet,
} from "@/lib/api";
import type {
  BodyRegion,
  Exercise,
  PainRecord,
  PainRecordCreatePayload,
  PainRecordFormValues,
  PainRecordUpdatePayload,
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
  onRequestCancelSession: (session: TrainingSession) => void;
  onRequestFinishSession: (session: TrainingSession) => void;
};

type DeleteTarget =
  | { type: "sessionExercise"; sessionExercise: SessionExercise }
  | { type: "trainingSet"; sessionExerciseId: string; set: TrainingSet }
  | { type: "painRecord"; painRecord: PainRecord };

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
    result: values.result,
    technical_quality: values.technical_quality || null,
    rest_seconds: numberOrNull(values.rest_seconds),
    notes: emptyToNull(values.notes),
  };
}

function buildPainRecordCreatePayload(
  sessionId: string,
  values: PainRecordFormValues,
): PainRecordCreatePayload {
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

function buildPainRecordUpdatePayload(values: PainRecordFormValues): PainRecordUpdatePayload {
  return {
    body_region_id: values.body_region_id,
    side: values.side,
    moment: values.moment,
    intensity: Number(values.intensity),
    description: emptyToNull(values.description),
    notes: emptyToNull(values.notes),
  };
}

function getPainRecordFormValues(record: PainRecord): PainRecordFormValues {
  return {
    training_set_id: record.training_set_id ?? "",
    body_region_id: record.body_region_id,
    side: record.side,
    moment: record.moment,
    intensity: String(record.intensity),
    description: record.description ?? "",
    notes: record.notes ?? "",
  };
}

const painMomentLabels = {
  PRE_SESSION: "Pré-sessão",
  DURING_SET: "Durante o set",
  POST_SESSION: "Pós-sessão",
  CHECKIN_24H: "Check-in 24h",
  CHECKIN_48H: "Check-in 48h",
};

const painSideLabels = {
  LEFT: "Esquerdo",
  RIGHT: "Direito",
  BILATERAL: "Bilateral",
  NOT_APPLICABLE: "Não aplicável",
};

function getDeleteTitle(deleteTarget: DeleteTarget | null) {
  if (deleteTarget?.type === "sessionExercise") {
    return "Remover exercício da sessão";
  }
  if (deleteTarget?.type === "trainingSet") {
    return "Excluir set";
  }
  return "Excluir registro de dor";
}

function getDeleteDescription(deleteTarget: DeleteTarget | null) {
  if (deleteTarget?.type === "sessionExercise") {
    return "O exercício será removido desta sessão e os sets vinculados também serão excluídos.";
  }
  if (deleteTarget?.type === "trainingSet") {
    return "O set será excluído. Registros de dor vinculados a ele permanecerão na sessão sem set específico.";
  }
  return "O registro de dor será removido do treino.";
}

function getDeleteConfirmLabel(deleteTarget: DeleteTarget | null) {
  if (deleteTarget?.type === "sessionExercise") {
    return "Remover exercício";
  }
  if (deleteTarget?.type === "trainingSet") {
    return "Excluir set";
  }
  return "Excluir dor";
}

export function SessionExecutionPanel({
  accessToken,
  session,
  onRequestCancelSession,
  onRequestFinishSession,
}: SessionExecutionPanelProps) {
  const [availableExercises, setAvailableExercises] = useState<Exercise[]>([]);
  const [bodyRegions, setBodyRegions] = useState<BodyRegion[]>([]);
  const [sessionExercises, setSessionExercises] = useState<SessionExercise[]>([]);
  const [setsBySessionExercise, setSetsBySessionExercise] = useState<Record<string, TrainingSet[]>>(
    {},
  );
  const [painRecords, setPainRecords] = useState<PainRecord[]>([]);
  const [deleteTarget, setDeleteTarget] = useState<DeleteTarget | null>(null);
  const [editingPainRecordId, setEditingPainRecordId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
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
      setEditingPainRecordId(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível carregar o treino.");
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
    return sessionExercises.flatMap(
      (sessionExercise) => setsBySessionExercise[sessionExercise.id] ?? [],
    );
  }, [sessionExercises, setsBySessionExercise]);

  const setLabelById = useMemo(() => {
    return sessionExercises.reduce<Record<string, string>>((acc, sessionExercise) => {
      const exerciseName = exerciseNameById[sessionExercise.exercise_id] ?? "Exercício";
      const sets = setsBySessionExercise[sessionExercise.id] ?? [];

      sets.forEach((set) => {
        acc[set.id] = `${exerciseName} - set ${set.set_number}`;
      });

      return acc;
    }, {});
  }, [exerciseNameById, sessionExercises, setsBySessionExercise]);

  const totalSuccessfulSets = useMemo(() => {
    return allSets.filter((set) => set.result === "SUCCESS").length;
  }, [allSets]);

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
      setFeedback("Exercício adicionado ao treino.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível adicionar exercício.");
    }
  }

  async function handleUpdateSessionExercise(
    sessionExerciseId: string,
    values: SessionExerciseFormValues,
  ) {
    setFeedback(null);
    setError(null);

    try {
      const updatedSessionExercise = await updateSessionExercise(accessToken, sessionExerciseId, {
        execution_order: Number(values.execution_order),
        notes: emptyToNull(values.notes),
      });
      setSessionExercises((current) =>
        current
          .map((sessionExercise) =>
            sessionExercise.id === updatedSessionExercise.id
              ? updatedSessionExercise
              : sessionExercise,
          )
          .sort((a, b) => a.execution_order - b.execution_order),
      );
      setFeedback("Exercício atualizado.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível atualizar exercício.");
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
      setError(err instanceof Error ? err.message : "Não foi possível registrar o set.");
    }
  }

  async function handleUpdateTrainingSet(
    sessionExerciseId: string,
    setId: string,
    values: TrainingSetFormValues,
  ) {
    setFeedback(null);
    setError(null);

    try {
      const updatedSet = await updateTrainingSet(accessToken, setId, buildTrainingSetPayload(values));
      setSetsBySessionExercise((current) => ({
        ...current,
        [sessionExerciseId]: (current[sessionExerciseId] ?? [])
          .map((set) => (set.id === updatedSet.id ? updatedSet : set))
          .sort((a, b) => a.set_number - b.set_number),
      }));
      setFeedback("Set atualizado.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível atualizar o set.");
    }
  }

  async function handleCreatePainRecord(values: PainRecordFormValues) {
    setFeedback(null);
    setError(null);

    try {
      const createdPainRecord = await createPainRecord(
        accessToken,
        buildPainRecordCreatePayload(session.id, values),
      );
      setPainRecords((current) => [createdPainRecord, ...current]);
      setFeedback("Dor registrada.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível registrar dor.");
    }
  }

  async function handleUpdatePainRecord(painRecordId: string, values: PainRecordFormValues) {
    setFeedback(null);
    setError(null);

    try {
      const updatedPainRecord = await updatePainRecord(
        accessToken,
        painRecordId,
        buildPainRecordUpdatePayload(values),
      );
      setPainRecords((current) =>
        current.map((record) => (record.id === updatedPainRecord.id ? updatedPainRecord : record)),
      );
      setEditingPainRecordId(null);
      setFeedback("Registro de dor atualizado.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível atualizar dor.");
    }
  }

  async function confirmDeleteTarget() {
    if (!deleteTarget) {
      return;
    }

    setFeedback(null);
    setError(null);
    setIsDeleting(true);

    try {
      if (deleteTarget.type === "sessionExercise") {
        const deletedSetIds = new Set(
          (setsBySessionExercise[deleteTarget.sessionExercise.id] ?? []).map((set) => set.id),
        );

        await deleteSessionExercise(accessToken, deleteTarget.sessionExercise.id);
        setSessionExercises((current) =>
          current.filter((item) => item.id !== deleteTarget.sessionExercise.id),
        );
        setSetsBySessionExercise((current) => {
          const next = { ...current };
          delete next[deleteTarget.sessionExercise.id];
          return next;
        });
        setPainRecords((current) =>
          current.map((record) =>
            record.training_set_id && deletedSetIds.has(record.training_set_id)
              ? { ...record, training_set_id: null }
              : record,
          ),
        );
        setFeedback("Exercício removido da sessão.");
      }

      if (deleteTarget.type === "trainingSet") {
        await deleteTrainingSet(accessToken, deleteTarget.set.id);
        setSetsBySessionExercise((current) => ({
          ...current,
          [deleteTarget.sessionExerciseId]: (current[deleteTarget.sessionExerciseId] ?? []).filter(
            (set) => set.id !== deleteTarget.set.id,
          ),
        }));
        setPainRecords((current) =>
          current.map((record) =>
            record.training_set_id === deleteTarget.set.id
              ? { ...record, training_set_id: null }
              : record,
          ),
        );
        setFeedback("Set excluído.");
      }

      if (deleteTarget.type === "painRecord") {
        await deletePainRecord(accessToken, deleteTarget.painRecord.id);
        setPainRecords((current) =>
          current.filter((record) => record.id !== deleteTarget.painRecord.id),
        );
        setFeedback("Registro de dor excluído.");
      }

      setDeleteTarget(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível excluir o registro.");
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <section className={styles.panel}>
      <header className={styles.header}>
        <div>
          <h3>{isSessionOpen ? "Treino em execução" : "Resumo do treino"}</h3>
          <p>
            {isSessionOpen
              ? "Monte a sessão, registre sets e acompanhe desconfortos."
              : "Revise exercícios, sets registrados e sinais de dor desta sessão."}
          </p>
        </div>
        <div className={styles.headerActions}>
          {isSessionOpen ? (
            <>
              <button
                className={styles.primaryAction}
                type="button"
                onClick={() => onRequestFinishSession(session)}
              >
                Finalizar
              </button>
              <button
                className={styles.dangerAction}
                type="button"
                onClick={() => onRequestCancelSession(session)}
              >
                Cancelar
              </button>
            </>
          ) : null}
          <button type="button" onClick={loadExecution}>
            Atualizar
          </button>
        </div>
      </header>

      {feedback ? <p className={styles.success}>{feedback}</p> : null}
      {error ? <p className={styles.error}>{error}</p> : null}

      {isLoading ? (
        <p className={styles.empty}>Carregando dados do treino...</p>
      ) : (
        <div className={isSessionOpen ? styles.grid : styles.historyGrid}>
          <div className={styles.column}>
            {!isSessionOpen ? (
              <section className={styles.historyStats} aria-label="Resumo do treino finalizado">
                <article>
                  <span>Exercícios</span>
                  <strong>{sessionExercises.length}</strong>
                </article>
                <article>
                  <span>Sets</span>
                  <strong>{allSets.length}</strong>
                </article>
                <article>
                  <span>Sucessos</span>
                  <strong>{totalSuccessfulSets}</strong>
                </article>
                <article>
                  <span>Dores</span>
                  <strong>{painRecords.length}</strong>
                </article>
              </section>
            ) : null}

            <div className={styles.sectionHeader}>
              <h4>Exercícios da sessão</h4>
              {!isSessionOpen ? <span>Somente leitura</span> : null}
            </div>

            {isSessionOpen ? (
              <ExecutionExerciseForm
                exercises={selectableExercises}
                nextOrder={sessionExercises.length + 1}
                onSubmit={handleCreateSessionExercise}
              />
            ) : null}

            <ExecutionExerciseList
              exerciseNameById={exerciseNameById}
              isSessionOpen={isSessionOpen}
              sessionExercises={sessionExercises}
              setsBySessionExercise={setsBySessionExercise}
              onCreateSet={handleCreateTrainingSet}
              onDeleteSessionExercise={(sessionExercise) =>
                setDeleteTarget({ type: "sessionExercise", sessionExercise })
              }
              onDeleteSet={(sessionExerciseId, set) =>
                setDeleteTarget({ type: "trainingSet", sessionExerciseId, set })
              }
              onUpdateSessionExercise={handleUpdateSessionExercise}
              onUpdateSet={handleUpdateTrainingSet}
            />
          </div>

          <div className={styles.column}>
            <div className={styles.sectionHeader}>
              <h4>Dor e desconforto</h4>
              {!isSessionOpen ? <span>Histórico</span> : null}
            </div>
            {isSessionOpen ? (
              <PainRecordForm
                bodyRegions={bodyRegions}
                setLabelById={setLabelById}
                sets={allSets}
                onSubmit={handleCreatePainRecord}
              />
            ) : null}

            <div className={styles.painList}>
              {painRecords.length === 0 ? (
                <p className={styles.empty}>Nenhum registro de dor nesta sessão.</p>
              ) : (
                painRecords.map((record) => {
                  const isEditingPainRecord = editingPainRecordId === record.id;

                  return (
                    <article className={styles.painCard} key={record.id}>
                      <strong>{bodyRegionNameById[record.body_region_id] ?? "Região"}</strong>
                      <span>
                        {painMomentLabels[record.moment]} - {painSideLabels[record.side]} -
                        intensidade {record.intensity}/10
                      </span>
                      {record.description ? <p>{record.description}</p> : null}
                      {record.notes ? <p>{record.notes}</p> : null}

                      {isSessionOpen ? (
                        <div className={styles.painActions}>
                          <button
                            type="button"
                            onClick={() =>
                              setEditingPainRecordId(isEditingPainRecord ? null : record.id)
                            }
                          >
                            {isEditingPainRecord ? "Fechar edição" : "Editar dor"}
                          </button>
                          <button
                            className={styles.danger}
                            type="button"
                            onClick={() => setDeleteTarget({ type: "painRecord", painRecord: record })}
                          >
                            Excluir dor
                          </button>
                        </div>
                      ) : null}

                      {isEditingPainRecord ? (
                        <PainRecordForm
                          bodyRegions={bodyRegions}
                          canChooseSet={false}
                          initialValues={getPainRecordFormValues(record)}
                          resetOnSubmit={false}
                          setLabelById={setLabelById}
                          sets={allSets}
                          submitLabel="Salvar dor"
                          submittingLabel="Salvando..."
                          onSubmit={(values) => handleUpdatePainRecord(record.id, values)}
                        />
                      ) : null}
                    </article>
                  );
                })
              )}
            </div>
          </div>
        </div>
      )}

      <ConfirmDialog
        confirmLabel={getDeleteConfirmLabel(deleteTarget)}
        description={getDeleteDescription(deleteTarget)}
        isOpen={deleteTarget !== null}
        isProcessing={isDeleting}
        title={getDeleteTitle(deleteTarget)}
        tone="danger"
        onCancel={() => setDeleteTarget(null)}
        onConfirm={() => void confirmDeleteTarget()}
      />
    </section>
  );
}
