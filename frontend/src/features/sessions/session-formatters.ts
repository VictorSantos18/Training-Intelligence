import type {
  TrainingSessionCreatePayload,
  TrainingSessionFinishPayload,
  TrainingSessionFinishFormValues,
  TrainingSessionFormValues,
  TrainingSessionStatus,
} from "@/types";

export const sessionStatusLabels: Record<TrainingSessionStatus, string> = {
  IN_PROGRESS: "Em andamento",
  COMPLETED: "Finalizada",
  CANCELLED: "Cancelada",
};

export function toDatetimeLocalValue(date = new Date()) {
  const offsetMs = date.getTimezoneOffset() * 60_000;
  return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16);
}

function emptyToNull(value: string) {
  const trimmedValue = value.trim();
  return trimmedValue ? trimmedValue : null;
}

function numericStringOrNull(value: string) {
  const trimmedValue = value.trim();
  return trimmedValue ? trimmedValue : null;
}

function integerOrNull(value: string) {
  const trimmedValue = value.trim();
  return trimmedValue ? Number(trimmedValue) : null;
}

export function buildCreateSessionPayload(
  values: TrainingSessionFormValues,
): TrainingSessionCreatePayload {
  return {
    skill_id: values.skill_id || null,
    started_at: new Date(values.started_at).toISOString(),
    body_weight_kg: numericStringOrNull(values.body_weight_kg),
    sleep_hours: numericStringOrNull(values.sleep_hours),
    sleep_quality: integerOrNull(values.sleep_quality),
    energy_before: integerOrNull(values.energy_before),
    motivation_before: integerOrNull(values.motivation_before),
    fatigue_before: integerOrNull(values.fatigue_before),
    notes_before: emptyToNull(values.notes_before),
  };
}

export function buildFinishSessionPayload(
  values: TrainingSessionFinishFormValues,
): TrainingSessionFinishPayload {
  return {
    finished_at: new Date().toISOString(),
    fatigue_after: integerOrNull(values.fatigue_after),
    performance_rating: integerOrNull(values.performance_rating),
    notes_after: emptyToNull(values.notes_after),
  };
}
