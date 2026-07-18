import type {
  AnalyticsOverview,
  ApiErrorPayload,
  BodyRegion,
  CurrentUser,
  Exercise,
  ExerciseCreatePayload,
  ExerciseUpdatePayload,
  PainRecord,
  PainRecordCreatePayload,
  PainRecordUpdatePayload,
  SessionExercise,
  SessionExerciseCreatePayload,
  SessionExerciseUpdatePayload,
  Skill,
  SkillCreatePayload,
  SkillUpdatePayload,
  TrainingSet,
  TrainingSetCreatePayload,
  TrainingSetUpdatePayload,
  TrainingSession,
  TrainingSessionCreatePayload,
  TrainingSessionFinishPayload,
  TrainingSessionStatus,
} from "@/types";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export function getApiUrl() {
  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
}

type ApiFetchOptions = RequestInit & {
  accessToken?: string;
};

export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const { accessToken, headers, ...requestOptions } = options;
  const response = await fetch(`${getApiUrl()}${path}`, {
    ...requestOptions,
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...headers,
    },
  });

  if (!response.ok) {
    let message = "Não foi possível concluir a requisição.";
    try {
      const payload = (await response.json()) as ApiErrorPayload;
      if (payload.detail) {
        message = payload.detail;
      }
    } catch {
      message = response.statusText || message;
    }
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function getCurrentUser(accessToken: string) {
  return apiFetch<CurrentUser>("/me", { accessToken });
}

export function getAnalyticsOverview(accessToken: string) {
  return apiFetch<AnalyticsOverview>("/analytics/overview", { accessToken });
}

export function listSkills(accessToken: string) {
  return apiFetch<Skill[]>("/skills", { accessToken });
}

export function createSkill(accessToken: string, payload: SkillCreatePayload) {
  return apiFetch<Skill>("/skills", {
    method: "POST",
    accessToken,
    body: JSON.stringify(payload),
  });
}

export function updateSkill(accessToken: string, skillId: string, payload: SkillUpdatePayload) {
  return apiFetch<Skill>(`/skills/${skillId}`, {
    method: "PATCH",
    accessToken,
    body: JSON.stringify(payload),
  });
}

export function deleteSkill(accessToken: string, skillId: string) {
  return apiFetch<void>(`/skills/${skillId}`, {
    method: "DELETE",
    accessToken,
  });
}

export function listExercises(
  accessToken: string,
  filters: { skillId?: string; isActive?: boolean } = {},
) {
  const params = new URLSearchParams();
  if (filters.skillId) {
    params.set("skill_id", filters.skillId);
  }
  if (filters.isActive !== undefined) {
    params.set("is_active", String(filters.isActive));
  }

  const query = params.toString();
  return apiFetch<Exercise[]>(`/exercises${query ? `?${query}` : ""}`, { accessToken });
}

export function createExercise(accessToken: string, payload: ExerciseCreatePayload) {
  return apiFetch<Exercise>("/exercises", {
    method: "POST",
    accessToken,
    body: JSON.stringify(payload),
  });
}

export function updateExercise(
  accessToken: string,
  exerciseId: string,
  payload: ExerciseUpdatePayload,
) {
  return apiFetch<Exercise>(`/exercises/${exerciseId}`, {
    method: "PATCH",
    accessToken,
    body: JSON.stringify(payload),
  });
}

export function deactivateExercise(accessToken: string, exerciseId: string) {
  return apiFetch<Exercise>(`/exercises/${exerciseId}`, {
    method: "DELETE",
    accessToken,
  });
}

export function listTrainingSessions(
  accessToken: string,
  filters: { skillId?: string; status?: TrainingSessionStatus } = {},
) {
  const params = new URLSearchParams();
  if (filters.skillId) {
    params.set("skill_id", filters.skillId);
  }
  if (filters.status) {
    params.set("status", filters.status);
  }

  const query = params.toString();
  return apiFetch<TrainingSession[]>(`/sessions${query ? `?${query}` : ""}`, {
    accessToken,
  });
}

export function getTrainingSession(accessToken: string, sessionId: string) {
  return apiFetch<TrainingSession>(`/sessions/${sessionId}`, { accessToken });
}

export function createTrainingSession(
  accessToken: string,
  payload: TrainingSessionCreatePayload,
) {
  return apiFetch<TrainingSession>("/sessions", {
    method: "POST",
    accessToken,
    body: JSON.stringify(payload),
  });
}

export function finishTrainingSession(
  accessToken: string,
  sessionId: string,
  payload: TrainingSessionFinishPayload,
) {
  return apiFetch<TrainingSession>(`/sessions/${sessionId}/finish`, {
    method: "POST",
    accessToken,
    body: JSON.stringify(payload),
  });
}

export function cancelTrainingSession(accessToken: string, sessionId: string) {
  return apiFetch<TrainingSession>(`/sessions/${sessionId}/cancel`, {
    method: "POST",
    accessToken,
  });
}

export function listSessionExercises(accessToken: string, sessionId: string) {
  return apiFetch<SessionExercise[]>(`/sessions/${sessionId}/exercises`, { accessToken });
}

export function createSessionExercise(
  accessToken: string,
  sessionId: string,
  payload: SessionExerciseCreatePayload,
) {
  return apiFetch<SessionExercise>(`/sessions/${sessionId}/exercises`, {
    method: "POST",
    accessToken,
    body: JSON.stringify(payload),
  });
}

export function updateSessionExercise(
  accessToken: string,
  sessionExerciseId: string,
  payload: SessionExerciseUpdatePayload,
) {
  return apiFetch<SessionExercise>(`/session-exercises/${sessionExerciseId}`, {
    method: "PATCH",
    accessToken,
    body: JSON.stringify(payload),
  });
}

export function deleteSessionExercise(accessToken: string, sessionExerciseId: string) {
  return apiFetch<void>(`/session-exercises/${sessionExerciseId}`, {
    method: "DELETE",
    accessToken,
  });
}

export function listTrainingSets(accessToken: string, sessionExerciseId: string) {
  return apiFetch<TrainingSet[]>(`/session-exercises/${sessionExerciseId}/sets`, {
    accessToken,
  });
}

export function createTrainingSet(
  accessToken: string,
  sessionExerciseId: string,
  payload: TrainingSetCreatePayload,
) {
  return apiFetch<TrainingSet>(`/session-exercises/${sessionExerciseId}/sets`, {
    method: "POST",
    accessToken,
    body: JSON.stringify(payload),
  });
}

export function updateTrainingSet(
  accessToken: string,
  setId: string,
  payload: TrainingSetUpdatePayload,
) {
  return apiFetch<TrainingSet>(`/sets/${setId}`, {
    method: "PATCH",
    accessToken,
    body: JSON.stringify(payload),
  });
}

export function deleteTrainingSet(accessToken: string, setId: string) {
  return apiFetch<void>(`/sets/${setId}`, {
    method: "DELETE",
    accessToken,
  });
}

export function listBodyRegions(accessToken: string) {
  return apiFetch<BodyRegion[]>("/body-regions", { accessToken });
}

export function listPainRecords(
  accessToken: string,
  filters: { trainingSessionId?: string; trainingSetId?: string } = {},
) {
  const params = new URLSearchParams();
  if (filters.trainingSessionId) {
    params.set("training_session_id", filters.trainingSessionId);
  }
  if (filters.trainingSetId) {
    params.set("training_set_id", filters.trainingSetId);
  }

  const query = params.toString();
  return apiFetch<PainRecord[]>(`/pain-records${query ? `?${query}` : ""}`, {
    accessToken,
  });
}

export function createPainRecord(accessToken: string, payload: PainRecordCreatePayload) {
  return apiFetch<PainRecord>("/pain-records", {
    method: "POST",
    accessToken,
    body: JSON.stringify(payload),
  });
}

export function updatePainRecord(
  accessToken: string,
  painRecordId: string,
  payload: PainRecordUpdatePayload,
) {
  return apiFetch<PainRecord>(`/pain-records/${painRecordId}`, {
    method: "PATCH",
    accessToken,
    body: JSON.stringify(payload),
  });
}

export function deletePainRecord(accessToken: string, painRecordId: string) {
  return apiFetch<void>(`/pain-records/${painRecordId}`, {
    method: "DELETE",
    accessToken,
  });
}
