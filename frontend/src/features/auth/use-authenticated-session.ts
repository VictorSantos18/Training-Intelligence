"use client";

import { useContext } from "react";

import { AuthSessionContext } from "@/features/auth/auth-provider";
import type { AuthSessionState, AuthenticatedSession } from "@/types";

type AuthenticatedSessionResult = {
  sessionState: AuthSessionState;
  session: AuthenticatedSession | null;
  error: string | null;
};

export function useAuthenticatedSession(): AuthenticatedSessionResult {
  const context = useContext(AuthSessionContext);

  if (!context) {
    throw new Error("useAuthenticatedSession must be used inside AuthProvider.");
  }

  return context;
}
