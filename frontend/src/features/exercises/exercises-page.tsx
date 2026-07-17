"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { ProtectedView } from "@/components/layout/protected-view";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import {
  createExercise,
  deactivateExercise,
  listExercises,
  listSkills,
  updateExercise,
} from "@/lib/api";
import type {
  Exercise,
  ExerciseCategory,
  ExerciseFormValues,
  ExerciseMeasurementType,
  Skill,
} from "@/types";

import { ExerciseForm } from "./exercise-form";
import { ExerciseList } from "./exercise-list";
import styles from "./exercises-page.module.css";

type ExercisesContentProps = {
  accessToken: string;
};

type ActiveFilter = "active" | "inactive" | "all";

const categoryLabels: Record<ExerciseCategory, string> = {
  HOLD: "Hold",
  PRESS: "Press",
  PULL: "Pull",
  RAISE: "Raise",
  NEGATIVE: "Negative",
  ACCESSORY: "Accessory",
};

const measurementLabels: Record<ExerciseMeasurementType, string> = {
  REPS: "Repeticoes",
  SECONDS: "Segundos",
  DISTANCE: "Distancia",
  CUSTOM: "Custom",
};

function buildExercisePayload(values: ExerciseFormValues) {
  return {
    skill_id: values.skill_id || null,
    name: values.name.trim(),
    category: values.category,
    measurement_type: values.measurement_type,
  };
}

function getActiveFilterValue(filter: ActiveFilter) {
  if (filter === "active") {
    return true;
  }
  if (filter === "inactive") {
    return false;
  }
  return undefined;
}

function ExercisesContent({ accessToken }: ExercisesContentProps) {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [selectedSkillId, setSelectedSkillId] = useState("");
  const [activeFilter, setActiveFilter] = useState<ActiveFilter>("active");
  const [isLoading, setIsLoading] = useState(true);
  const [exerciseToDeactivate, setExerciseToDeactivate] = useState<Exercise | null>(null);
  const [isDeactivating, setIsDeactivating] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [skillsData, exercisesData] = await Promise.all([
        listSkills(accessToken),
        listExercises(accessToken, {
          skillId: selectedSkillId || undefined,
          isActive: getActiveFilterValue(activeFilter),
        }),
      ]);
      setSkills(skillsData);
      setExercises(exercisesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel carregar exercicios.");
    } finally {
      setIsLoading(false);
    }
  }, [accessToken, activeFilter, selectedSkillId]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const skillNameById = useMemo(() => {
    return skills.reduce<Record<string, string>>((acc, skill) => {
      acc[skill.id] = skill.name;
      return acc;
    }, {});
  }, [skills]);

  const activeCount = exercises.filter((exercise) => exercise.is_active).length;
  const inactiveCount = exercises.length - activeCount;

  async function handleCreateExercise(values: ExerciseFormValues) {
    setFeedback(null);
    setError(null);

    try {
      const createdExercise = await createExercise(accessToken, buildExercisePayload(values));
      setExercises((currentExercises) => [createdExercise, ...currentExercises]);
      setFeedback("Exercicio criado com sucesso.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel criar o exercicio.");
    }
  }

  async function handleUpdateExercise(exerciseId: string, values: ExerciseFormValues) {
    setFeedback(null);
    setError(null);

    try {
      const updatedExercise = await updateExercise(
        accessToken,
        exerciseId,
        buildExercisePayload(values),
      );
      setExercises((currentExercises) =>
        currentExercises.map((exercise) =>
          exercise.id === exerciseId ? updatedExercise : exercise,
        ),
      );
      setFeedback("Exercicio atualizado.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel atualizar o exercicio.");
    }
  }

  async function confirmDeactivateExercise() {
    if (!exerciseToDeactivate) {
      return;
    }

    setFeedback(null);
    setError(null);
    setIsDeactivating(true);

    try {
      const deactivatedExercise = await deactivateExercise(accessToken, exerciseToDeactivate.id);
      setExercises((currentExercises) =>
        currentExercises.map((currentExercise) =>
          currentExercise.id === exerciseToDeactivate.id ? deactivatedExercise : currentExercise,
        ),
      );
      setExerciseToDeactivate(null);
      setFeedback("Exercicio desativado.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel desativar o exercicio.");
    } finally {
      setIsDeactivating(false);
    }
  }

  async function handleReactivateExercise(exercise: Exercise) {
    setFeedback(null);
    setError(null);

    try {
      const reactivatedExercise = await updateExercise(accessToken, exercise.id, {
        is_active: true,
      });
      setExercises((currentExercises) =>
        currentExercises.map((currentExercise) =>
          currentExercise.id === exercise.id ? reactivatedExercise : currentExercise,
        ),
      );
      setFeedback("Exercicio reativado.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Nao foi possivel reativar o exercicio.");
    }
  }

  return (
    <section className={styles.page}>
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Exercicios</p>
          <h2>Movimentos que alimentam suas sessoes.</h2>
          <p>
            Cadastre holds, presses, pulls, raises, negativas e acessorios. Cada exercicio
            pode ficar ligado a uma skill ou funcionar como apoio geral.
          </p>
        </div>
        <button className={styles.refresh} type="button" onClick={loadData}>
          Atualizar
        </button>
      </header>

      <section className={styles.summary} aria-label="Resumo de exercicios">
        <article className={styles.summaryItem}>
          <span>Visiveis no filtro</span>
          <strong>{exercises.length}</strong>
        </article>
        <article className={styles.summaryItem}>
          <span>Ativos</span>
          <strong>{activeCount}</strong>
        </article>
        <article className={styles.summaryItem}>
          <span>Inativos</span>
          <strong>{inactiveCount}</strong>
        </article>
      </section>

      <div className={styles.content}>
        <aside className={styles.formPanel}>
          <div className={styles.panelHeader}>
            <h3>Novo exercicio</h3>
            <p>Escolha a metrica principal com cuidado; ela define como a execucao sera registrada.</p>
          </div>
          <ExerciseForm
            categoryLabels={categoryLabels}
            measurementLabels={measurementLabels}
            skills={skills}
            submitLabel="Criar exercicio"
            onSubmit={handleCreateExercise}
          />
        </aside>

        <section className={styles.listPanel}>
          <div className={styles.panelHeader}>
            <h3>Exercicios cadastrados</h3>
            <p>{isLoading ? "Carregando..." : `${exercises.length} registro(s)`}</p>
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
                value={activeFilter}
                onChange={(event) => setActiveFilter(event.target.value as ActiveFilter)}
              >
                <option value="active">Ativos</option>
                <option value="inactive">Inativos</option>
                <option value="all">Todos</option>
              </select>
            </label>
          </div>

          {feedback ? <p className={styles.success}>{feedback}</p> : null}
          {error ? <p className={styles.error}>{error}</p> : null}

          <ExerciseList
            categoryLabels={categoryLabels}
            exercises={exercises}
            isLoading={isLoading}
            measurementLabels={measurementLabels}
            skillNameById={skillNameById}
            skills={skills}
            onDeactivate={setExerciseToDeactivate}
            onReactivate={handleReactivateExercise}
            onUpdate={handleUpdateExercise}
          />
        </section>
      </div>

      <ConfirmDialog
        confirmLabel="Desativar exercicio"
        description={
          exerciseToDeactivate
            ? `O exercicio "${exerciseToDeactivate.name}" deixara de aparecer nos fluxos ativos, mas o historico existente sera preservado.`
            : ""
        }
        isOpen={exerciseToDeactivate !== null}
        isProcessing={isDeactivating}
        title="Confirmar desativacao"
        tone="danger"
        onCancel={() => setExerciseToDeactivate(null)}
        onConfirm={() => void confirmDeactivateExercise()}
      />
    </section>
  );
}

export function ExercisesPage() {
  return (
    <ProtectedView errorTitle="Nao foi possivel abrir seus exercicios">
      {(session) => <ExercisesContent accessToken={session.accessToken} />}
    </ProtectedView>
  );
}
