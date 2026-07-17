"use client";

import Link from "next/link";

import type { TrainingSession } from "@/types";

import { sessionStatusLabels } from "./session-formatters";
import styles from "./session-list.module.css";

type SessionListProps = {
  isLoading: boolean;
  selectedSessionId: string | null;
  sessions: TrainingSession[];
  skillNameById: Record<string, string>;
  onSelect: (session: TrainingSession) => void;
};

function formatSessionPeriod(session: TrainingSession) {
  const startedAt = new Date(session.started_at);

  if (session.status !== "COMPLETED" || !session.finished_at) {
    return startedAt.toLocaleString("pt-BR");
  }

  const finishedAt = new Date(session.finished_at);
  const date = startedAt.toLocaleDateString("pt-BR");
  const startTime = startedAt.toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });
  const finishTime = finishedAt.toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });

  return `${date}, ${startTime} - ${finishTime}`;
}

export function SessionList({
  isLoading,
  selectedSessionId,
  sessions,
  skillNameById,
  onSelect,
}: SessionListProps) {
  if (isLoading) {
    return <p className={styles.empty}>Carregando sessões...</p>;
  }

  if (sessions.length === 0) {
    return (
      <div className={styles.emptyState}>
        <h4>Nenhuma sessão encontrada.</h4>
        <p>Crie uma sessão ou ajuste os filtros para consultar outros status.</p>
      </div>
    );
  }

  return (
    <div className={styles.list}>
      {sessions.map((session) => {
        const skillLabel = session.skill_id
          ? skillNameById[session.skill_id] ?? "Skill não encontrada"
          : "Sessão geral";
        const isSelected = selectedSessionId === session.id;

        return (
          <article className={isSelected ? styles.cardSelected : styles.card} key={session.id}>
            <button className={styles.selectButton} type="button" onClick={() => onSelect(session)}>
              <span className={styles.status}>{sessionStatusLabels[session.status]}</span>
              <strong>{skillLabel}</strong>
              <span>{formatSessionPeriod(session)}</span>
              {session.status === "COMPLETED" && session.notes_after ? (
                <span className={styles.sessionNote}>{session.notes_after}</span>
              ) : null}
            </button>

            {isSelected ? (
              <Link className={styles.moreLink} href={`/sessions/${session.id}`}>
                Ver mais
              </Link>
            ) : null}
          </article>
        );
      })}
    </div>
  );
}
