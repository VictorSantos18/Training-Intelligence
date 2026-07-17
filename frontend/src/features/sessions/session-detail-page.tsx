"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import { ProtectedView } from "@/components/layout/protected-view";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import {
  cancelTrainingSession,
  finishTrainingSession,
  getTrainingSession,
  listSkills,
} from "@/lib/api";
import type { Skill, TrainingSession, TrainingSessionFinishFormValues } from "@/types";

import { SessionExecutionPanel } from "./session-execution-panel";
import { SessionFinishForm } from "./session-finish-form";
import { buildFinishSessionPayload, sessionStatusLabels } from "./session-formatters";
import styles from "./session-detail-page.module.css";

type SessionDetailPageProps = {
  sessionId: string;
};

type SessionDetailContentProps = {
  accessToken: string;
  sessionId: string;
};

function SessionDetailContent({ accessToken, sessionId }: SessionDetailContentProps) {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [session, setSession] = useState<TrainingSession | null>(null);
  const [sessionToCancel, setSessionToCancel] = useState<TrainingSession | null>(null);
  const [sessionToFinish, setSessionToFinish] = useState<TrainingSession | null>(null);
  const [isCancelling, setIsCancelling] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadSession = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [skillsData, sessionData] = await Promise.all([
        listSkills(accessToken),
        getTrainingSession(accessToken, sessionId),
      ]);
      setSkills(skillsData);
      setSession(sessionData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel carregar a sessao.");
    } finally {
      setIsLoading(false);
    }
  }, [accessToken, sessionId]);

  useEffect(() => {
    void loadSession();
  }, [loadSession]);

  const skillNameById = useMemo(() => {
    return skills.reduce<Record<string, string>>((acc, skill) => {
      acc[skill.id] = skill.name;
      return acc;
    }, {});
  }, [skills]);

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
      setSession(finishedSession);
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
      setSession(cancelledSession);
      setSessionToCancel(null);
      setFeedback("Sessao cancelada.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel cancelar a sessao.");
    } finally {
      setIsCancelling(false);
    }
  }

  if (isLoading) {
    return <p className={styles.loading}>Carregando sessao...</p>;
  }

  if (!session) {
    return (
      <section className={styles.empty}>
        <h2>Sessao nao encontrada</h2>
        <p>{error ?? "Volte para a lista e escolha outra sessao."}</p>
        <Link href="/sessions">Voltar para sessoes</Link>
      </section>
    );
  }

  const skillLabel = session.skill_id
    ? skillNameById[session.skill_id] ?? "Skill nao encontrada"
    : "Sessao geral";
  const isSessionOpen = session.status === "IN_PROGRESS";

  return (
    <section className={styles.page}>
      <header className={styles.header}>
        <div>
          <Link className={styles.backLink} href="/sessions">
            Voltar para sessoes
          </Link>
          <p className={styles.eyebrow}>
            {isSessionOpen ? "Treino em execucao" : "Historico do treino"}
          </p>
          <h2>{skillLabel}</h2>
          <p>{new Date(session.started_at).toLocaleString("pt-BR")}</p>
        </div>

        {isSessionOpen ? (
          <div className={styles.headerActions}>
            <button type="button" onClick={() => setSessionToFinish(session)}>
              Finalizar
            </button>
            <button className={styles.danger} type="button" onClick={() => setSessionToCancel(session)}>
              Cancelar
            </button>
          </div>
        ) : null}
      </header>

      {feedback ? <p className={styles.success}>{feedback}</p> : null}
      {error ? <p className={styles.error}>{error}</p> : null}

      <section className={styles.summary}>
        <article>
          <span>Status</span>
          <strong>{sessionStatusLabels[session.status]}</strong>
        </article>
        <article>
          <span>Energia</span>
          <strong>{session.energy_before ?? "-"}</strong>
        </article>
        <article>
          <span>Sono</span>
          <strong>{session.sleep_hours ?? "-"}</strong>
        </article>
        <article>
          <span>Termino</span>
          <strong>
            {session.finished_at ? new Date(session.finished_at).toLocaleString("pt-BR") : "-"}
          </strong>
        </article>
      </section>

      {session.notes_after ? (
        <section className={styles.notes}>
          <span>Notas finais</span>
          <p>{session.notes_after}</p>
        </section>
      ) : null}

      <SessionExecutionPanel accessToken={accessToken} session={session} />

      {sessionToFinish ? (
        <SessionFinishForm
          session={sessionToFinish}
          onCancel={() => setSessionToFinish(null)}
          onSubmit={handleFinishSession}
        />
      ) : null}

      <ConfirmDialog
        confirmLabel="Cancelar sessao"
        description="A sessao sera marcada como cancelada. O registro permanece no historico."
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

export function SessionDetailPage({ sessionId }: SessionDetailPageProps) {
  return (
    <ProtectedView errorTitle="Nao foi possivel abrir esta sessao">
      {(session) => <SessionDetailContent accessToken={session.accessToken} sessionId={sessionId} />}
    </ProtectedView>
  );
}
