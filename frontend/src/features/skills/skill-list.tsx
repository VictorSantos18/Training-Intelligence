"use client";

import { useState } from "react";

import type { Skill, SkillFormValues, SkillStatus } from "@/types";

import { SkillForm } from "./skill-form";
import styles from "./skill-list.module.css";

type SkillListProps = {
  isLoading: boolean;
  skills: Skill[];
  onDelete: (skill: Skill) => void;
  onStatusChange: (skill: Skill, status: SkillStatus) => Promise<void>;
  onUpdate: (skillId: string, values: SkillFormValues) => Promise<void>;
};

const statusLabels: Record<SkillStatus, string> = {
  ACTIVE: "Ativa",
  PAUSED: "Pausada",
  ACHIEVED: "Conquistada",
};

export function SkillList({
  isLoading,
  skills,
  onDelete,
  onStatusChange,
  onUpdate,
}: SkillListProps) {
  const [editingSkillId, setEditingSkillId] = useState<string | null>(null);

  if (isLoading) {
    return <p className={styles.empty}>Carregando skills...</p>;
  }

  if (skills.length === 0) {
    return (
      <div className={styles.emptyState}>
        <h4>Nenhuma skill cadastrada ainda.</h4>
        <p>Crie sua primeira habilidade para organizar exercícios e sessões.</p>
      </div>
    );
  }

  return (
    <div className={styles.list}>
      {skills.map((skill) => {
        const isEditing = editingSkillId === skill.id;

        return (
          <article className={styles.card} key={skill.id}>
            {isEditing ? (
              <SkillForm
                initialSkill={skill}
                submitLabel="Salvar alterações"
                onCancel={() => setEditingSkillId(null)}
                onSubmit={async (values) => {
                  await onUpdate(skill.id, values);
                  setEditingSkillId(null);
                }}
              />
            ) : (
              <>
                <div className={styles.cardHeader}>
                  <div>
                    <span className={styles.status}>{statusLabels[skill.status]}</span>
                    <h4>{skill.name}</h4>
                  </div>
                  <select
                    className={styles.statusSelect}
                    value={skill.status}
                    aria-label={`Alterar status de ${skill.name}`}
                    onChange={(event) =>
                      void onStatusChange(skill, event.target.value as SkillStatus)
                    }
                  >
                    <option value="ACTIVE">Ativa</option>
                    <option value="PAUSED">Pausada</option>
                    <option value="ACHIEVED">Conquistada</option>
                  </select>
                </div>

                <p className={styles.description}>
                  {skill.description || "Sem descrição cadastrada."}
                </p>

                <div className={styles.meta}>
                  <span>Criada em {new Date(skill.created_at).toLocaleDateString("pt-BR")}</span>
                  <span>Atualizada em {new Date(skill.updated_at).toLocaleDateString("pt-BR")}</span>
                </div>

                <div className={styles.actions}>
                  <button type="button" onClick={() => setEditingSkillId(skill.id)}>
                    Editar
                  </button>
                  <button
                    className={styles.danger}
                    type="button"
                    onClick={() => onDelete(skill)}
                  >
                    Excluir
                  </button>
                </div>
              </>
            )}
          </article>
        );
      })}
    </div>
  );
}
