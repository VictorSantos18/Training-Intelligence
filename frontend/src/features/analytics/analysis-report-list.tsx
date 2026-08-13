"use client";

import type { AnalysisReportListItem } from "@/types";

import styles from "./analysis-report-list.module.css";

type AnalysisReportListProps = {
  reports: AnalysisReportListItem[];
  selectedReportId: string | null;
  isLoading: boolean;
  onSelect: (reportId: string) => void;
};

const statusLabels: Record<AnalysisReportListItem["status"], string> = {
  PROMPT_GENERATED: "Prompt gerado",
  ANALYSIS_SAVED: "Análise salva",
};

function formatPeriod(report: AnalysisReportListItem) {
  const start = new Date(`${report.period_start}T00:00:00`);
  const end = new Date(`${report.period_end}T00:00:00`);
  return `${start.toLocaleDateString("pt-BR")} - ${end.toLocaleDateString("pt-BR")}`;
}

export function AnalysisReportList({
  reports,
  selectedReportId,
  isLoading,
  onSelect,
}: AnalysisReportListProps) {
  if (isLoading) {
    return <p className={styles.empty}>Carregando histórico...</p>;
  }

  if (reports.length === 0) {
    return <p className={styles.empty}>Nenhuma análise gerada ainda.</p>;
  }

  return (
    <div className={styles.list}>
      {reports.map((report) => {
        const isSelected = report.id === selectedReportId;

        return (
          <button
            className={isSelected ? styles.itemActive : styles.item}
            key={report.id}
            type="button"
            onClick={() => onSelect(report.id)}
          >
            <span>{formatPeriod(report)}</span>
            <strong>{report.title}</strong>
            <em>{statusLabels[report.status]}</em>
          </button>
        );
      })}
    </div>
  );
}
