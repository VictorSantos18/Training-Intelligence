"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { ProtectedView } from "@/components/layout/protected-view";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import {
  cancelTrainingSession,
  createTrainingSession,
  finishTrainingSession,
  listSkills,
  listTrainingSessions,
} from "@/lib/api";
import type {
  Skill,
  TrainingSession,
  TrainingSessionFinishFormValues,
  TrainingSessionFormValues,
  TrainingSessionStatus,
} from "@/types";

import { SessionFinishForm } from "./session-finish-form";
import { SessionForm } from "./session-form";
import {
  buildCreateSessionPayload,
  buildFinishSessionPayload,
  sessionStatusLabels,
} from "./session-formatters";
import { SessionList } from "./session-list";
import styles from "./sessions-page.module.css";

type SessionsContentProps = {
  accessToken: string;
};

type StatusFilter = TrainingSessionStatus | "ALL";

function getStatusFilterValue(status: StatusFilter) {
  return status === "ALL" ? undefined : status;
}

function SessionsContent({ accessToken }: SessionsContentProps) {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [sessions, setSessions] = useState<TrainingSession[]>([]);
  const [selectedSession, setSelectedSession] = useState<TrainingSession | null>(null);
  const [selectedSkillId, setSelectedSkillId] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("ALL");
  const [sessionToCancel, setSessionToCancel] = useState<TrainingSession | null>(null);
  const [sessionToFinish, setSessionToFinish] = useState<TrainingSession | null>(null);
  const [isCancelling, setIsCancelling] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [skillsData, sessionsData] = await Promise.all([
        listSkills(accessToken),
        listTrainingSessions(accessToken, {
          skillId: selectedSkillId || undefined,
          status: getStatusFilterValue(statusFilter),
        }),
      ]);
      setSkills(skillsData);
      setSessions(sessionsData);
      setSelectedSession((currentSelectedSession) => {
        if (!currentSelectedSession) {
          return sessionsData[0] ?? null;
        }
        return (
          sessionsData.find((session) => session.id === currentSelectedSession.id) ??
          sessionsData[0] ??
          null
        );
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel carregar sessoes.");
    } finally {
      setIsLoading(false);
    }
  }, [accessToken, selectedSkillId, statusFilter]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const skillNameById = useMemo(() => {
    return skills.reduce<Record<string, string>>((acc, skill) => {
      acc[skill.id] = skill.name;
      return acc;
    }, {});
  }, [skills]);

  const statusCounts = useMemo(() => {
    return sessions.reduce<Record<TrainingSessionStatus, number>>(
      (acc, session) => {
        acc[session.status] += 1;
        return acc;
      },
      { IN_PROGRESS: 0, COMPLETED: 0, CANCELLED: 0 },
    );
  }, [sessions]);

  function updateSessionInState(updatedSession: TrainingSession) {
    setSessions((currentSessions) =>
      currentSessions.map((session) =>
        session.id === updatedSession.id ? updatedSession : session,
      ),
    );
    setSelectedSession(updatedSession);
  }

  async function handleCreateSession(values: TrainingSessionFormValues) {
    setFeedback(null);
    setError(null);

    try {
      const createdSession = await createTrainingSession(
        accessToken,
        buildCreateSessionPayload(values),
      );
      setSessions((currentSessions) => [createdSession, ...currentSessions]);
      setSelectedSession(createdSession);
      setFeedback("Sessao criada.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel criar a sessao.");
    }
  }

  async function handleFinishSession(values: TrainingSessionFinishFormValues) {
    if (!sessionToFinish) {
      return;
    }

    setFeedback(null);
    setError(null);

    try {
      const finishedSession = await finishTrainingSession(
        accessToken,
        sessionToFinish.id,
        buildFinishSessionPayload(values),
      );
      updateSessionInState(finishedSession);
      setSessionToFinish(null);
      setFeedback("Sessao finalizada.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel finalizar a sessao.");
    }
  }

  async function confirmCancelSession() {
    if (!sessionToCancel) {
      return;
    }

    setFeedback(null);
    setError(null);
    setIsCancelling(true);

    try {
      const cancelledSession = await cancelTrainingSession(accessToken, sessionToCancel.id);
      updateSessionInState(cancelledSession);
      setSessionToCancel(null);
      setFeedback("Sessao cancelada.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel cancelar a sessao.");
    } finally {
      setIsCancelling(false);
    }
  }

  return (
    <section className={styles.page}>
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Sessoes</p>
          <h2>Registro base dos seus treinos.</h2>
          <p>
            Crie sessoes, acompanhe check-ins iniciais e feche o ciclo do treino com
            percepcao de fadiga e performance.
          </p>
        </div>
        <button className={styles.refresh} type="button" onClick={loadData}>
          Atualizar
        </button>
      </header>

      <section className={styles.summary} aria-label="Resumo de sessoes">
        {(Object.keys(sessionStatusLabels) as TrainingSessionStatus[]).map((status) => (
          <article className={styles.summaryItem} key={status}>
            <span>{sessionStatusLabels[status]}</span>
            <strong>{statusCounts[status]}</strong>
          </article>
        ))}
      </section>

      <div className={styles.content}>
        <aside className={styles.formPanel}>
          <div className={styles.panelHeader}>
            <h3>Nova sessao</h3>
            <p>Registre o contexto antes do treino para comparar desempenho depois.</p>
          </div>
          <SessionForm skills={skills} onSubmit={handleCreateSession} />
        </aside>

        <section className={styles.listPanel}>
          <div className={styles.panelHeader}>
            <h3>Sessoes registradas</h3>
            <p>{isLoading ? "Carregando..." : `${sessions.length} registro(s)`}</p>
          </div>

          <div className={styles.filters}>
            <label>
              <span>Skill</span>
              <select
                value={selectedSkillId}
                onChange={(event) => setSelectedSkillId(event.target.value)}
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
              <span>Status</span>
              <select
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value as StatusFilter)}
              >
                <option value="ALL">Todos</option>
                <option value="IN_PROGRESS">Em andamento</option>
                <option value="COMPLETED">Finalizadas</option>
                <option value="CANCELLED">Canceladas</option>
              </select>
            </label>
          </div>

          {feedback ? <p className={styles.success}>{feedback}</p> : null}
          {error ? <p className={styles.error}>{error}</p> : null}

          <SessionList
            isLoading={isLoading}
            selectedSessionId={selectedSession?.id ?? null}
            sessions={sessions}
            skillNameById={skillNameById}
            onSelect={setSelectedSession}
          />
        </section>

        <aside className={styles.detailPanel}>
          <div className={styles.panelHeader}>
            <h3>Detalhe</h3>
            <p>Visao inicial da sessao selecionada.</p>
          </div>

          {selectedSession ? (
            <div className={styles.detail}>
              <div>
                <span className={styles.status}>{sessionStatusLabels[selectedSession.status]}</span>
                <h4>
                  {selectedSession.skill_id
                    ? skillNameById[selectedSession.skill_id] ?? "Skill nao encontrada"
                    : "Sessao geral"}
                </h4>
                <p>{new Date(selectedSession.started_at).toLocaleString("pt-BR")}</p>
              </div>

              <dl className={styles.metrics}>
                <div>
                  <dt>Peso</dt>
                  <dd>{selectedSession.body_weight_kg ?? "-"}</dd>
                </div>
                <div>
                  <dt>Sono</dt>
                  <dd>{selectedSession.sleep_hours ?? "-"}</dd>
                </div>
                <div>
                  <dt>Energia</dt>
                  <dd>{selectedSession.energy_before ?? "-"}</dd>
                </div>
                <div>
                  <dt>Fadiga inicial</dt>
                  <dd>{selectedSession.fatigue_before ?? "-"}</dd>
                </div>
                <div>
                  <dt>Fadiga final</dt>
                  <dd>{selectedSession.fatigue_after ?? "-"}</dd>
                </div>
                <div>
                  <dt>Performance</dt>
                  <dd>{selectedSession.performance_rating ?? "-"}</dd>
                </div>
              </dl>

              {selectedSession.notes_before ? (
                <p className={styles.notes}>{selectedSession.notes_before}</p>
              ) : null}
              {selectedSession.notes_after ? (
                <p className={styles.notes}>{selectedSession.notes_after}</p>
              ) : null}

              {selectedSession.status === "IN_PROGRESS" ? (
                <div className={styles.detailActions}>
                  <button type="button" onClick={() => setSessionToFinish(selectedSession)}>
                    Finalizar
                  </button>
                  <button
                    className={styles.danger}
                    type="button"
                    onClick={() => setSessionToCancel(selectedSession)}
                  >
                    Cancelar
                  </button>
                </div>
              ) : null}
            </div>
          ) : (
            <p className={styles.emptyDetail}>Selecione uma sessao para ver os detalhes.</p>
          )}
        </aside>
      </div>

      {sessionToFinish ? (
        <SessionFinishForm
          session={sessionToFinish}
          onCancel={() => setSessionToFinish(null)}
          onSubmit={handleFinishSession}
        />
      ) : null}

      <ConfirmDialog
        confirmLabel="Cancelar sessao"
        description={
          sessionToCancel
            ? "A sessao sera marcada como cancelada. O registro permanece no historico."
            : ""
        }
        isOpen={sessionToCancel !== null}
        isProcessing={isCancelling}
        title="Confirmar cancelamento"
        tone="danger"
        onCancel={() => setSessionToCancel(null)}
        onConfirm={() => void confirmCancelSession()}
      />
    </section>
  );
}

export function SessionsPage() {
  return (
    <ProtectedView errorTitle="Nao foi possivel abrir suas sessoes">
      {(session) => <SessionsContent accessToken={session.accessToken} />}
    </ProtectedView>
  );
}
