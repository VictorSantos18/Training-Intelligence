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
