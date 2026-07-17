import type {
  ApiErrorPayload,
  CurrentUser,
  Exercise,
  ExerciseCreatePayload,
  ExerciseUpdatePayload,
  Skill,
  SkillCreatePayload,
  SkillUpdatePayload,
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
    let message = "Nao foi possivel concluir a requisicao.";
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
