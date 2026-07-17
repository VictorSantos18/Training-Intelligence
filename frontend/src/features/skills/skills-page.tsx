"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { ProtectedView } from "@/components/layout/protected-view";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { createSkill, deleteSkill, listSkills, updateSkill } from "@/lib/api";
import type { Skill, SkillFormValues, SkillStatus } from "@/types";

import { SkillForm } from "./skill-form";
import { SkillList } from "./skill-list";
import styles from "./skills-page.module.css";

const statusLabels: Record<SkillStatus, string> = {
  ACTIVE: "Ativas",
  PAUSED: "Pausadas",
  ACHIEVED: "Conquistadas",
};

function buildSkillPayload(values: SkillFormValues) {
  return {
    name: values.name.trim(),
    description: values.description.trim() || null,
    status: values.status,
  };
}

type SkillsContentProps = {
  accessToken: string;
};

function SkillsContent({ accessToken }: SkillsContentProps) {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [skillToDelete, setSkillToDelete] = useState<Skill | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadSkills = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await listSkills(accessToken);
      setSkills(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível carregar skills.");
    } finally {
      setIsLoading(false);
    }
  }, [accessToken]);

  useEffect(() => {
    void loadSkills();
  }, [loadSkills]);

  const statusCounts = useMemo(() => {
    return skills.reduce<Record<SkillStatus, number>>(
      (acc, skill) => {
        acc[skill.status] += 1;
        return acc;
      },
      { ACTIVE: 0, PAUSED: 0, ACHIEVED: 0 },
    );
  }, [skills]);

  async function handleCreateSkill(values: SkillFormValues) {
    setFeedback(null);
    setError(null);
    try {
      const createdSkill = await createSkill(accessToken, buildSkillPayload(values));
      setSkills((currentSkills) => [createdSkill, ...currentSkills]);
      setFeedback("Skill criada com sucesso.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível criar a skill.");
    }
  }

  async function handleUpdateSkill(skillId: string, values: SkillFormValues) {
    setFeedback(null);
    setError(null);
    try {
      const updatedSkill = await updateSkill(accessToken, skillId, buildSkillPayload(values));
      setSkills((currentSkills) =>
        currentSkills.map((skill) => (skill.id === skillId ? updatedSkill : skill)),
      );
      setFeedback("Skill atualizada.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível atualizar a skill.");
    }
  }

  async function handleStatusChange(skill: Skill, status: SkillStatus) {
    setFeedback(null);
    setError(null);
    try {
      const updatedSkill = await updateSkill(accessToken, skill.id, { status });
      setSkills((currentSkills) =>
        currentSkills.map((currentSkill) =>
          currentSkill.id === skill.id ? updatedSkill : currentSkill,
        ),
      );
      setFeedback("Status atualizado.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível alterar o status.");
    }
  }

  async function confirmDeleteSkill() {
    if (!skillToDelete) {
      return;
    }

    setFeedback(null);
    setError(null);
    setIsDeleting(true);
    try {
      await deleteSkill(accessToken, skillToDelete.id);
      setSkills((currentSkills) =>
        currentSkills.filter((currentSkill) => currentSkill.id !== skillToDelete.id),
      );
      setSkillToDelete(null);
      setFeedback("Skill excluida.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível excluir a skill.");
    } finally {
      setIsDeleting(false);
    }
  }

  return (
    <section className={styles.page}>
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Skills</p>
          <h2>Habilidades que guiam seu treino.</h2>
          <p>
            Cadastre objetivos como Front Lever e Iron Cross, acompanhe status e mantenha
            uma base limpa para associar exercícios e sessões.
          </p>
        </div>
        <button className={styles.refresh} type="button" onClick={loadSkills}>
          Atualizar
        </button>
      </header>

      <section className={styles.summary} aria-label="Resumo de skills">
        {(Object.keys(statusLabels) as SkillStatus[]).map((status) => (
          <article className={styles.summaryItem} key={status}>
            <span>{statusLabels[status]}</span>
            <strong>{statusCounts[status]}</strong>
          </article>
        ))}
      </section>

      <div className={styles.content}>
        <aside className={styles.formPanel}>
          <div className={styles.panelHeader}>
            <h3>Nova skill</h3>
            <p>Use nomes claros. Eles serão usados nos filtros e nos exercícios.</p>
          </div>
          <SkillForm submitLabel="Criar skill" onSubmit={handleCreateSkill} />
        </aside>

        <section className={styles.listPanel}>
          <div className={styles.panelHeader}>
            <h3>Skills cadastradas</h3>
            <p>{isLoading ? "Carregando..." : `${skills.length} registro(s)`}</p>
          </div>

          {feedback ? <p className={styles.success}>{feedback}</p> : null}
          {error ? <p className={styles.error}>{error}</p> : null}

          <SkillList
            isLoading={isLoading}
            skills={skills}
            onDelete={setSkillToDelete}
            onStatusChange={handleStatusChange}
            onUpdate={handleUpdateSkill}
          />
        </section>
      </div>

      <ConfirmDialog
        confirmLabel="Excluir skill"
        description={
          skillToDelete
            ? `A skill "${skillToDelete.name}" será removida. Essa ação deve ser usada apenas para registros de teste ou criados por engano.`
            : ""
        }
        isOpen={skillToDelete !== null}
        isProcessing={isDeleting}
        title="Confirmar exclusão"
        tone="danger"
        onCancel={() => setSkillToDelete(null)}
        onConfirm={() => void confirmDeleteSkill()}
      />
    </section>
  );
}

export function SkillsPage() {
  return (
    <ProtectedView errorTitle="Não foi possível abrir suas skills">
      {(session) => <SkillsContent accessToken={session.accessToken} />}
    </ProtectedView>
  );
}
