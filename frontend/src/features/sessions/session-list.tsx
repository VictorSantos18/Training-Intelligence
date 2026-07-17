"use client";

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

export function SessionList({
  isLoading,
  selectedSessionId,
  sessions,
  skillNameById,
  onSelect,
}: SessionListProps) {
  if (isLoading) {
    return <p className={styles.empty}>Carregando sessoes...</p>;
  }

  if (sessions.length === 0) {
    return (
      <div className={styles.emptyState}>
        <h4>Nenhuma sessao encontrada.</h4>
        <p>Crie uma sessao ou ajuste os filtros para consultar outros status.</p>
      </div>
    );
  }

  return (
    <div className={styles.list}>
      {sessions.map((session) => {
        const skillLabel = session.skill_id
          ? skillNameById[session.skill_id] ?? "Skill nao encontrada"
          : "Sessao geral";
        const isSelected = selectedSessionId === session.id;

        return (
          <button
            className={isSelected ? styles.cardSelected : styles.card}
            key={session.id}
            type="button"
            onClick={() => onSelect(session)}
          >
            <span className={styles.status}>{sessionStatusLabels[session.status]}</span>
            <strong>{skillLabel}</strong>
            <span>{new Date(session.started_at).toLocaleString("pt-BR")}</span>
          </button>
        );
      })}
    </div>
  );
}
