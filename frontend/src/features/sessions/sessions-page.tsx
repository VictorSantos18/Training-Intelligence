"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { ProtectedView } from "@/components/layout/protected-view";
import {
  createTrainingSession,
  listSkills,
  listTrainingSessions,
} from "@/lib/api";
import type {
  Skill,
  TrainingSession,
  TrainingSessionFormValues,
  TrainingSessionStatus,
} from "@/types";

import { SessionForm } from "./session-form";
import { buildCreateSessionPayload, sessionStatusLabels } from "./session-formatters";
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
      setError(err instanceof Error ? err.message : "Não foi possível carregar sessões.");
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
      setFeedback("Sessão criada.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível criar a sessão.");
    }
  }

  return (
    <section className={styles.page}>
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Sessões</p>
          <h2>Registro base dos seus treinos.</h2>
          <p>
            Crie sessões, acompanhe energia e sono, e feche o ciclo do treino com suas
            notas finais.
          </p>
        </div>
        <button className={styles.refresh} type="button" onClick={loadData}>
          Atualizar
        </button>
      </header>

      <section className={styles.summary} aria-label="Resumo de sessões">
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
            <h3>Nova sessão</h3>
            <p>Registre apenas o contexto essencial antes do treino.</p>
          </div>
          <SessionForm skills={skills} onSubmit={handleCreateSession} />
        </aside>

        <section className={styles.listPanel}>
          <div className={styles.panelHeader}>
            <h3>Sessões registradas</h3>
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
      </div>
    </section>
  );
}

export function SessionsPage() {
  return (
    <ProtectedView errorTitle="Não foi possível abrir suas sessões">
      {(session) => <SessionsContent accessToken={session.accessToken} />}
    </ProtectedView>
  );
}
