"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { ProtectedView } from "@/components/layout/protected-view";
import {
  generateAnalysisReport,
  getAnalysisReport,
  listAnalysisReports,
  listSkills,
  updateAnalysisReport,
} from "@/lib/api";
import type {
  AnalysisReport,
  AnalysisReportFormValues,
  AnalysisReportListItem,
  Skill,
} from "@/types";

import { AnalysisReportDetail } from "./analysis-report-detail";
import { AnalysisReportForm } from "./analysis-report-form";
import { AnalysisReportList } from "./analysis-report-list";
import styles from "./analytics-page.module.css";

type AnalyticsContentProps = {
  accessToken: string;
};

function toDateInputValue(date: Date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function getInitialFormValues(): AnalysisReportFormValues {
  const end = new Date();
  const start = new Date();
  start.setDate(end.getDate() - 6);

  return {
    period_start: toDateInputValue(start),
    period_end: toDateInputValue(end),
    skill_id: "",
    title: "",
  };
}

function getFriendlyError(message: string) {
  if (message === "No completed sessions found for this period") {
    return "Nenhuma sessão finalizada encontrada para esse período.";
  }
  if (message === "Skill not found") {
    return "Skill não encontrada.";
  }
  return message;
}

function getErrorMessage(error: unknown) {
  return error instanceof Error ? getFriendlyError(error.message) : "Erro inesperado.";
}

function AnalyticsContent({ accessToken }: AnalyticsContentProps) {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [reports, setReports] = useState<AnalysisReportListItem[]>([]);
  const [selectedReport, setSelectedReport] = useState<AnalysisReport | null>(null);
  const [formValues, setFormValues] = useState<AnalysisReportFormValues>(getInitialFormValues);
  const [analysisText, setAnalysisText] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    const [skillsResult, reportsResult] = await Promise.allSettled([
      listSkills(accessToken),
      listAnalysisReports(accessToken),
    ]);
    const errors: string[] = [];

    if (skillsResult.status === "fulfilled") {
      setSkills(skillsResult.value);
    } else {
      setSkills([]);
      errors.push(`Não foi possível carregar skills: ${getErrorMessage(skillsResult.reason)}`);
    }

    if (reportsResult.status === "fulfilled") {
      setReports(reportsResult.value);
    } else {
      setReports([]);
      errors.push(`Não foi possível carregar histórico: ${getErrorMessage(reportsResult.reason)}`);
    }

    setError(errors.length > 0 ? errors.join(" ") : null);
    setIsLoading(false);
  }, [accessToken]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const selectedSkillName = useMemo(() => {
    if (!formValues.skill_id) {
      return "Todas as skills";
    }
    return skills.find((skill) => skill.id === formValues.skill_id)?.name ?? "Skill selecionada";
  }, [formValues.skill_id, skills]);

  const isSharingSupported = typeof navigator !== "undefined" && "share" in navigator;

  async function handleGenerateReport() {
    setIsGenerating(true);
    setFeedback(null);
    setError(null);

    try {
      const report = await generateAnalysisReport(accessToken, {
        period_start: formValues.period_start,
        period_end: formValues.period_end,
        skill_id: formValues.skill_id || null,
        title: formValues.title.trim() || null,
      });
      setSelectedReport(report);
      setAnalysisText(report.external_analysis ?? "");
      setReports((currentReports) => [
        {
          id: report.id,
          skill_id: report.skill_id,
          title: report.title,
          period_start: report.period_start,
          period_end: report.period_end,
          status: report.status,
          created_at: report.created_at,
          updated_at: report.updated_at,
        },
        ...currentReports.filter((item) => item.id !== report.id),
      ]);
      setFeedback("Relatório gerado e salvo no histórico.");
    } catch (err) {
      setError(err instanceof Error ? getFriendlyError(err.message) : "Não foi possível gerar o relatório.");
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleSelectReport(reportId: string) {
    setFeedback(null);
    setError(null);

    try {
      const report = await getAnalysisReport(accessToken, reportId);
      setSelectedReport(report);
      setAnalysisText(report.external_analysis ?? "");
    } catch (err) {
      setError(err instanceof Error ? getFriendlyError(err.message) : "Não foi possível abrir a análise.");
    }
  }

  async function handleCopyPrompt() {
    if (!selectedReport) {
      return;
    }

    try {
      await navigator.clipboard.writeText(selectedReport.generated_prompt);
      setFeedback("Prompt copiado.");
    } catch {
      setError("Não foi possível copiar o prompt neste navegador.");
    }
  }

  async function handleSharePrompt() {
    if (!selectedReport || !isSharingSupported) {
      return;
    }

    try {
      await navigator.share({
        title: selectedReport.title,
        text: selectedReport.generated_prompt,
      });
      setFeedback("Prompt compartilhado.");
    } catch {
      setError("Não foi possível compartilhar o prompt.");
    }
  }

  async function handleSaveAnalysis() {
    if (!selectedReport) {
      return;
    }

    setIsSaving(true);
    setFeedback(null);
    setError(null);

    try {
      const report = await updateAnalysisReport(accessToken, selectedReport.id, {
        external_analysis: analysisText.trim() || null,
      });
      setSelectedReport(report);
      setAnalysisText(report.external_analysis ?? "");
      setReports((currentReports) =>
        currentReports.map((item) =>
          item.id === report.id
            ? {
                ...item,
                status: report.status,
                updated_at: report.updated_at,
              }
            : item,
        ),
      );
      setFeedback("Resposta salva no histórico.");
    } catch (err) {
      setError(err instanceof Error ? getFriendlyError(err.message) : "Não foi possível salvar a resposta.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <section className={styles.page}>
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Análises</p>
          <h2>Relatórios para interpretar seus treinos.</h2>
          <p>
            Escolha um período, gere um prompt estruturado para o ChatGPT e salve a
            resposta no histórico para consultar quando quiser.
          </p>
        </div>
        <button className={styles.refresh} type="button" onClick={loadData}>
          Atualizar
        </button>
      </header>

      {error ? <p className={styles.error}>{error}</p> : null}

      <section className={styles.content}>
        <aside className={styles.sideColumn}>
          <section className={styles.panel}>
            <div className={styles.panelHeader}>
              <h3>Nova análise</h3>
              <p>{selectedSkillName}, considerando somente sessões finalizadas.</p>
            </div>
            <AnalysisReportForm
              isSubmitting={isGenerating}
              skills={skills}
              values={formValues}
              onChange={setFormValues}
              onSubmit={handleGenerateReport}
            />
          </section>

          <section className={styles.panel}>
            <div className={styles.panelHeader}>
              <h3>Histórico</h3>
              <p>{isLoading ? "Carregando..." : `${reports.length} análise(s)`}</p>
            </div>
            <AnalysisReportList
              isLoading={isLoading}
              reports={reports}
              selectedReportId={selectedReport?.id ?? null}
              onSelect={handleSelectReport}
            />
          </section>
        </aside>

        <section className={styles.detailPanel}>
          <AnalysisReportDetail
            analysisText={analysisText}
            feedback={feedback}
            isSaving={isSaving}
            isSharingSupported={isSharingSupported}
            report={selectedReport}
            onAnalysisTextChange={setAnalysisText}
            onCopyPrompt={handleCopyPrompt}
            onSaveAnalysis={handleSaveAnalysis}
            onSharePrompt={handleSharePrompt}
          />
        </section>
      </section>
    </section>
  );
}

export function AnalyticsPage() {
  return (
    <ProtectedView errorTitle="Não foi possível abrir suas análises">
      {(session) => <AnalyticsContent accessToken={session.accessToken} />}
    </ProtectedView>
  );
}
