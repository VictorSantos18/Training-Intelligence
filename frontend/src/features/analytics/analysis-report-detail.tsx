"use client";

import type { AnalysisReport } from "@/types";

import styles from "./analysis-report-detail.module.css";

type AnalysisReportDetailProps = {
  report: AnalysisReport | null;
  analysisText: string;
  feedback: string | null;
  isSaving: boolean;
  isSharingSupported: boolean;
  onAnalysisTextChange: (value: string) => void;
  onCopyPrompt: () => void;
  onSharePrompt: () => void;
  onSaveAnalysis: () => void;
};

function formatMetric(value: number | null, suffix = "") {
  if (value === null) {
    return "-";
  }
  return `${value.toLocaleString("pt-BR")}${suffix}`;
}

function formatPeriod(report: AnalysisReport) {
  const start = new Date(`${report.period_start}T00:00:00`);
  const end = new Date(`${report.period_end}T00:00:00`);
  return `${start.toLocaleDateString("pt-BR")} - ${end.toLocaleDateString("pt-BR")}`;
}

export function AnalysisReportDetail({
  report,
  analysisText,
  feedback,
  isSaving,
  isSharingSupported,
  onAnalysisTextChange,
  onCopyPrompt,
  onSharePrompt,
  onSaveAnalysis,
}: AnalysisReportDetailProps) {
  if (!report) {
    return (
      <div className={styles.empty}>
        <h3>Relatório selecionado</h3>
        <p>Gere uma nova análise ou selecione um item do histórico.</p>
      </div>
    );
  }

  return (
    <article className={styles.detail}>
      <header className={styles.header}>
        <div>
          <span>{formatPeriod(report)}</span>
          <h3>{report.title}</h3>
        </div>
        <em>{report.status === "ANALYSIS_SAVED" ? "Análise salva" : "Prompt gerado"}</em>
      </header>

      <section className={styles.metrics} aria-label="Resumo da análise">
        <div>
          <span>Sessões</span>
          <strong>{report.summary_snapshot.total_sessions}</strong>
        </div>
        <div>
          <span>Séries</span>
          <strong>{report.summary_snapshot.total_sets}</strong>
        </div>
        <div>
          <span>RPE médio</span>
          <strong>{formatMetric(report.summary_snapshot.average_rpe)}</strong>
        </div>
        <div>
          <span>Dor máxima</span>
          <strong>{formatMetric(report.summary_snapshot.max_pain_intensity, "/10")}</strong>
        </div>
      </section>

      <section className={styles.promptBlock}>
        <div className={styles.blockHeader}>
          <div>
            <h4>Prompt para ChatGPT</h4>
            <p>Use este texto para pedir a análise fora do app.</p>
          </div>
          <div className={styles.actions}>
            {isSharingSupported ? (
              <button type="button" onClick={onSharePrompt}>
                Compartilhar
              </button>
            ) : null}
            <button type="button" onClick={onCopyPrompt}>
              Copiar
            </button>
          </div>
        </div>
        <textarea readOnly value={report.generated_prompt} />
      </section>

      <section className={styles.analysisBlock}>
        <div className={styles.blockHeader}>
          <div>
            <h4>Resposta do ChatGPT</h4>
            <p>Cole aqui a análise recebida para manter o histórico completo.</p>
          </div>
          <button disabled={isSaving} type="button" onClick={onSaveAnalysis}>
            {isSaving ? "Salvando..." : "Salvar resposta"}
          </button>
        </div>
        <textarea
          placeholder="Cole aqui a análise gerada pelo ChatGPT."
          value={analysisText}
          onChange={(event) => onAnalysisTextChange(event.target.value)}
        />
      </section>

      {feedback ? <p className={styles.feedback}>{feedback}</p> : null}
    </article>
  );
}
