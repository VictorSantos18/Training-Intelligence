"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import { ProtectedView } from "@/components/layout/protected-view";
import { getAnalyticsOverview } from "@/lib/api";
import type { AnalyticsOverview, TrainingSessionStatus } from "@/types";

import styles from "./dashboard-home.module.css";

type DashboardContentProps = {
  accessToken: string;
};

const sessionStatusLabels: Record<TrainingSessionStatus, string> = {
  IN_PROGRESS: "Em andamento",
  COMPLETED: "Finalizada",
  CANCELLED: "Cancelada",
};

function formatMetric(value: number | null, suffix = "") {
  if (value === null) {
    return "-";
  }
  return `${value.toLocaleString("pt-BR")}${suffix}`;
}

function formatSessionPeriod(session: AnalyticsOverview["recent_sessions"][number]) {
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

function getMaxValue(values: number[]) {
  return Math.max(...values, 1);
}

function EmptyList({ message }: { message: string }) {
  return <p className={styles.empty}>{message}</p>;
}

function DashboardContent({ accessToken }: DashboardContentProps) {
  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadOverview = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      setOverview(await getAnalyticsOverview(accessToken));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível carregar o dashboard.");
    } finally {
      setIsLoading(false);
    }
  }, [accessToken]);

  useEffect(() => {
    void loadOverview();
  }, [loadOverview]);

  const maxSessionsBySkill = useMemo(() => {
    return getMaxValue(overview?.sessions_by_skill.map((item) => item.session_count) ?? []);
  }, [overview]);

  const maxExerciseSets = useMemo(() => {
    return getMaxValue(overview?.top_exercises.map((item) => item.set_count) ?? []);
  }, [overview]);

  const maxPainRecords = useMemo(() => {
    return getMaxValue(overview?.pain_by_region.map((item) => item.record_count) ?? []);
  }, [overview]);

  return (
    <section className={styles.page}>
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Dashboard</p>
          <h2>Resumo dos seus treinos.</h2>
          <p>
            Acompanhe sessões, volume registrado, exercícios mais usados e sinais de dor
            a partir dos dados que você já está coletando.
          </p>
        </div>
        <button className={styles.refresh} type="button" onClick={loadOverview}>
          Atualizar
        </button>
      </header>

      {isLoading ? <p className={styles.state}>Carregando dashboard...</p> : null}
      {error ? <p className={styles.error}>{error}</p> : null}

      {overview ? (
        <>
          <section className={styles.metrics} aria-label="Métricas principais">
            <article className={styles.metric}>
              <span>Sessões</span>
              <strong>{overview.stats.total_sessions}</strong>
              <p>{overview.stats.completed_sessions} finalizada(s)</p>
            </article>
            <article className={styles.metric}>
              <span>Sets</span>
              <strong>{overview.stats.total_sets}</strong>
              <p>Volume total registrado.</p>
            </article>
            <article className={styles.metric}>
              <span>Energia média</span>
              <strong>{formatMetric(overview.stats.average_energy_before)}</strong>
              <p>Escala de 0 a 10 antes do treino.</p>
            </article>
            <article className={styles.metric}>
              <span>Sono médio</span>
              <strong>{formatMetric(overview.stats.average_sleep_hours, "h")}</strong>
              <p>Horas informadas antes das sessões.</p>
            </article>
          </section>

          <div className={styles.content}>
            <section className={styles.panel}>
              <div className={styles.panelHeader}>
                <h3>Sessões por skill</h3>
                <p>Distribuição dos treinos registrados.</p>
              </div>

              {overview.sessions_by_skill.length === 0 ? (
                <EmptyList message="Nenhuma sessão registrada ainda." />
              ) : (
                <div className={styles.barList}>
                  {overview.sessions_by_skill.map((item) => (
                    <article className={styles.barItem} key={item.skill_id ?? "general"}>
                      <div>
                        <strong>{item.skill_name}</strong>
                        <span>
                          {item.completed_count}/{item.session_count} finalizadas
                        </span>
                      </div>
                      <div className={styles.barTrack}>
                        <span
                          style={{ width: `${(item.session_count / maxSessionsBySkill) * 100}%` }}
                        />
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </section>

            <section className={styles.panel}>
              <div className={styles.panelHeader}>
                <h3>Últimos treinos</h3>
                <p>Acesso rápido ao histórico recente.</p>
              </div>

              {overview.recent_sessions.length === 0 ? (
                <EmptyList message="Crie uma sessão para ela aparecer aqui." />
              ) : (
                <div className={styles.sessionList}>
                  {overview.recent_sessions.map((session) => (
                    <Link
                      className={styles.sessionItem}
                      href={`/sessions/${session.id}`}
                      key={session.id}
                    >
                      <div>
                        <strong>{session.skill_name}</strong>
                        <span>{formatSessionPeriod(session)}</span>
                      </div>
                      <em>{sessionStatusLabels[session.status]}</em>
                    </Link>
                  ))}
                </div>
              )}
            </section>

            <section className={styles.panel}>
              <div className={styles.panelHeader}>
                <h3>Exercícios em destaque</h3>
                <p>Ordenado por quantidade de sets.</p>
              </div>

              {overview.top_exercises.length === 0 ? (
                <EmptyList message="Registre sets para ver exercícios em destaque." />
              ) : (
                <div className={styles.barList}>
                  {overview.top_exercises.map((exercise) => (
                    <article className={styles.barItem} key={exercise.exercise_id}>
                      <div>
                        <strong>{exercise.exercise_name}</strong>
                        <span>
                          {exercise.set_count} sets, {exercise.success_count} sucesso(s)
                        </span>
                      </div>
                      <div className={styles.barTrack}>
                        <span style={{ width: `${(exercise.set_count / maxExerciseSets) * 100}%` }} />
                      </div>
                      <small>
                        {exercise.total_repetitions} reps |{" "}
                        {formatMetric(exercise.total_duration_seconds, "s")}
                      </small>
                    </article>
                  ))}
                </div>
              )}
            </section>

            <section className={styles.panel}>
              <div className={styles.panelHeader}>
                <h3>Dor por região</h3>
                <p>Regiões com mais registros de desconforto.</p>
              </div>

              {overview.pain_by_region.length === 0 ? (
                <EmptyList message="Nenhum registro de dor ainda." />
              ) : (
                <div className={styles.barList}>
                  {overview.pain_by_region.map((region) => (
                    <article className={styles.barItem} key={region.body_region_id}>
                      <div>
                        <strong>{region.body_region_name}</strong>
                        <span>
                          média {region.average_intensity}/10, pico {region.max_intensity}/10
                        </span>
                      </div>
                      <div className={styles.barTrackDanger}>
                        <span style={{ width: `${(region.record_count / maxPainRecords) * 100}%` }} />
                      </div>
                      <small>{region.record_count} registro(s)</small>
                    </article>
                  ))}
                </div>
              )}
            </section>
          </div>
        </>
      ) : null}
    </section>
  );
}

export function DashboardHome() {
  return (
    <ProtectedView errorTitle="Não foi possível abrir o painel">
      {(session) => <DashboardContent accessToken={session.accessToken} />}
    </ProtectedView>
  );
}
