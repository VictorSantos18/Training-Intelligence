export type AuthMode = "login" | "signup";

export type AuthFormValues = {
  email: string;
  password: string;
};

export type CurrentUser = {
  id: string;
  email: string | null;
  role: string | null;
};

export type ApiErrorPayload = {
  detail?: string;
};

export type AuthSessionState = "checking" | "authenticated" | "unauthenticated";

export type AuthenticatedSession = {
  user: CurrentUser;
  accessToken: string;
};

export type SkillStatus = "ACTIVE" | "PAUSED" | "ACHIEVED";

export type Skill = {
  id: string;
  name: string;
  description: string | null;
  status: SkillStatus;
  created_at: string;
  updated_at: string;
};

export type SkillFormValues = {
  name: string;
  description: string;
  status: SkillStatus;
};

export type SkillCreatePayload = {
  name: string;
  description?: string | null;
  status: SkillStatus;
};

export type SkillUpdatePayload = Partial<SkillCreatePayload>;

export type ExerciseCategory = "HOLD" | "PRESS" | "PULL" | "RAISE" | "NEGATIVE" | "ACCESSORY";

export type ExerciseMeasurementType = "REPS" | "SECONDS" | "DISTANCE" | "CUSTOM";

export type Exercise = {
  id: string;
  skill_id: string | null;
  name: string;
  category: ExerciseCategory;
  measurement_type: ExerciseMeasurementType;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type ExerciseFormValues = {
  skill_id: string;
  name: string;
  category: ExerciseCategory;
  measurement_type: ExerciseMeasurementType;
};

export type ExerciseCreatePayload = {
  skill_id?: string | null;
  name: string;
  category: ExerciseCategory;
  measurement_type: ExerciseMeasurementType;
};

export type ExerciseUpdatePayload = Partial<ExerciseCreatePayload> & {
  is_active?: boolean;
};

export type TrainingSessionStatus = "IN_PROGRESS" | "COMPLETED" | "CANCELLED";

export type TrainingSession = {
  id: string;
  skill_id: string | null;
  started_at: string;
  finished_at: string | null;
  body_weight_kg: string | null;
  sleep_hours: string | null;
  sleep_quality: number | null;
  energy_before: number | null;
  motivation_before: number | null;
  fatigue_before: number | null;
  fatigue_after: number | null;
  performance_rating: number | null;
  notes_before: string | null;
  notes_after: string | null;
  status: TrainingSessionStatus;
  created_at: string;
  updated_at: string;
};

export type TrainingSessionFormValues = {
  skill_id: string;
  started_at: string;
  body_weight_kg: string;
  sleep_hours: string;
  sleep_quality: string;
  energy_before: string;
  motivation_before: string;
  fatigue_before: string;
  notes_before: string;
};

export type TrainingSessionCreatePayload = {
  skill_id?: string | null;
  started_at: string;
  body_weight_kg?: string | null;
  sleep_hours?: string | null;
  sleep_quality?: number | null;
  energy_before?: number | null;
  motivation_before?: number | null;
  fatigue_before?: number | null;
  notes_before?: string | null;
};

export type TrainingSessionFinishFormValues = {
  fatigue_after: string;
  performance_rating: string;
  notes_after: string;
};

export type TrainingSessionFinishPayload = {
  finished_at?: string | null;
  fatigue_after?: number | null;
  performance_rating?: number | null;
  notes_after?: string | null;
};
