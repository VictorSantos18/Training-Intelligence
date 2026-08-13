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
  sleep_hours: string | null;
  energy_before: number | null;
  notes_after: string | null;
  status: TrainingSessionStatus;
  created_at: string;
  updated_at: string;
};

export type TrainingSessionFormValues = {
  skill_id: string;
  started_at: string;
  sleep_hours: string;
  energy_before: string;
};

export type TrainingSessionCreatePayload = {
  skill_id?: string | null;
  started_at: string;
  sleep_hours?: string | null;
  energy_before?: number | null;
};

export type TrainingSessionFinishFormValues = {
  finished_at: string;
  notes_after: string;
};

export type TrainingSessionFinishPayload = {
  finished_at?: string | null;
  notes_after?: string | null;
};

export type SessionExercise = {
  id: string;
  session_id: string;
  exercise_id: string;
  execution_order: number;
  notes: string | null;
  created_at: string;
};

export type SessionExerciseFormValues = {
  exercise_id: string;
  execution_order: string;
  notes: string;
};

export type SessionExerciseCreatePayload = {
  exercise_id: string;
  execution_order: number;
  notes?: string | null;
};

export type SessionExerciseUpdatePayload = {
  execution_order?: number;
  notes?: string | null;
};

export type TrainingSetResult = "SUCCESS" | "PARTIAL" | "FAILED" | "SKIPPED";

export type TechnicalQuality = "EXCELLENT" | "GOOD" | "ACCEPTABLE" | "POOR";

export type TrainingSet = {
  id: string;
  session_exercise_id: string;
  set_number: number;
  repetitions: number | null;
  duration_seconds: string | null;
  assistance_level: string | null;
  rpe: string | null;
  pain_during: number | null;
  result: TrainingSetResult;
  technical_quality: TechnicalQuality | null;
  rest_seconds: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type TrainingSetFormValues = {
  set_number: string;
  repetitions: string;
  duration_seconds: string;
  assistance_level: string;
  rpe: string;
  result: TrainingSetResult;
  technical_quality: "" | TechnicalQuality;
  rest_time: string;
  notes: string;
};

export type TrainingSetCreatePayload = {
  set_number: number;
  repetitions?: number | null;
  duration_seconds?: string | null;
  assistance_level?: string | null;
  rpe?: string | null;
  pain_during?: number | null;
  result: TrainingSetResult;
  technical_quality?: TechnicalQuality | null;
  rest_seconds?: number | null;
  notes?: string | null;
};

export type TrainingSetUpdatePayload = Partial<TrainingSetCreatePayload>;

export type BodyRegion = {
  id: string;
  code: string;
  name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type PainRecordMoment =
  | "PRE_SESSION"
  | "DURING_SET"
  | "POST_SESSION"
  | "CHECKIN_24H"
  | "CHECKIN_48H";

export type PainRecordSide = "LEFT" | "RIGHT" | "BILATERAL" | "NOT_APPLICABLE";

export type PainRecord = {
  id: string;
  training_session_id: string | null;
  training_set_id: string | null;
  body_region_id: string;
  occurred_at: string;
  side: PainRecordSide;
  moment: PainRecordMoment;
  intensity: number;
  description: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type PainRecordFormValues = {
  training_set_id: string;
  body_region_id: string;
  moment: PainRecordMoment;
  intensity: string;
  description: string;
  notes: string;
};

export type PainRecordCreatePayload = {
  training_session_id?: string | null;
  training_set_id?: string | null;
  body_region_id: string;
  side: PainRecordSide;
  moment: PainRecordMoment;
  intensity: number;
  description?: string | null;
  notes?: string | null;
};

export type PainRecordUpdatePayload = {
  body_region_id?: string;
  side?: PainRecordSide;
  moment?: PainRecordMoment;
  intensity?: number;
  description?: string | null;
  notes?: string | null;
};

export type AnalyticsStats = {
  total_sessions: number;
  completed_sessions: number;
  in_progress_sessions: number;
  cancelled_sessions: number;
  total_sets: number;
  pain_records: number;
  average_energy_before: number | null;
  average_sleep_hours: number | null;
};

export type SessionsBySkillItem = {
  skill_id: string | null;
  skill_name: string;
  session_count: number;
  completed_count: number;
};

export type RecentSessionItem = {
  id: string;
  skill_name: string;
  status: TrainingSessionStatus;
  started_at: string;
  finished_at: string | null;
};

export type TopExerciseItem = {
  exercise_id: string;
  exercise_name: string;
  set_count: number;
  success_count: number;
  total_repetitions: number;
  total_duration_seconds: number;
};

export type PainByRegionItem = {
  body_region_id: string;
  body_region_name: string;
  record_count: number;
  average_intensity: number;
  max_intensity: number;
};

export type AnalyticsOverview = {
  stats: AnalyticsStats;
  sessions_by_skill: SessionsBySkillItem[];
  recent_sessions: RecentSessionItem[];
  top_exercises: TopExerciseItem[];
  pain_by_region: PainByRegionItem[];
};

export type AnalysisReportStatus = "PROMPT_GENERATED" | "ANALYSIS_SAVED";

export type AnalysisReportSessionLink = {
  id: string;
  analysis_report_id: string;
  training_session_id: string;
  created_at: string;
};

export type AnalysisReportSummarySnapshot = {
  total_sessions: number;
  total_sets: number;
  total_repetitions: number;
  total_duration_seconds: number;
  average_rpe: number | null;
  average_energy_before: number | null;
  average_sleep_hours: number | null;
  max_pain_intensity: number | null;
  pain_records_count: number;
  skills: string[];
  sessions: unknown[];
};

export type AnalysisReport = {
  id: string;
  skill_id: string | null;
  title: string;
  period_start: string;
  period_end: string;
  filters: Record<string, unknown>;
  summary_snapshot: AnalysisReportSummarySnapshot;
  generated_prompt: string;
  external_analysis: string | null;
  status: AnalysisReportStatus;
  created_at: string;
  updated_at: string;
  sessions: AnalysisReportSessionLink[];
};

export type AnalysisReportListItem = Pick<
  AnalysisReport,
  | "id"
  | "skill_id"
  | "title"
  | "period_start"
  | "period_end"
  | "status"
  | "created_at"
  | "updated_at"
>;

export type AnalysisReportGeneratePayload = {
  period_start: string;
  period_end: string;
  skill_id?: string | null;
  title?: string | null;
};

export type AnalysisReportUpdatePayload = {
  title?: string;
  external_analysis?: string | null;
};

export type AnalysisReportFormValues = {
  period_start: string;
  period_end: string;
  skill_id: string;
  title: string;
};
