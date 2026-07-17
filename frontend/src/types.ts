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
