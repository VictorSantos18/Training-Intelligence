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

export function getDefaultFinishedAtValue(startedAt: string) {
  const now = new Date();
  const startedAtDate = new Date(startedAt);
  const minimumFinishedAt = new Date(startedAtDate.getTime() + 60_000);

  return toDatetimeLocalValue(now > minimumFinishedAt ? now : minimumFinishedAt);
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
    sleep_hours: numericStringOrNull(values.sleep_hours),
    energy_before: integerOrNull(values.energy_before),
  };
}

export function buildFinishSessionPayload(
  values: TrainingSessionFinishFormValues,
): TrainingSessionFinishPayload {
  return {
    finished_at: new Date(values.finished_at).toISOString(),
    notes_after: emptyToNull(values.notes_after),
  };
}
