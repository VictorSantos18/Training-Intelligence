"use client";

import { createContext, useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";

import { ApiError, getCurrentUser } from "@/lib/api";
import { getSupabaseClient, isSupabaseConfigured } from "@/lib/supabase";
import type { AuthSessionState, AuthenticatedSession } from "@/types";

export type AuthSessionContextValue = {
  sessionState: AuthSessionState;
  session: AuthenticatedSession | null;
  error: string | null;
};

export const AuthSessionContext = createContext<AuthSessionContextValue | null>(null);

type AuthProviderProps = {
  children: ReactNode;
};

export function AuthProvider({ children }: AuthProviderProps) {
  const [sessionState, setSessionState] = useState<AuthSessionState>("checking");
  const [session, setSession] = useState<AuthenticatedSession | null>(null);
  const [error, setError] = useState<string | null>(null);
  const sessionRef = useRef<AuthenticatedSession | null>(null);

  const setAuthenticatedSession = useCallback((nextSession: AuthenticatedSession | null) => {
    sessionRef.current = nextSession;
    setSession(nextSession);
  }, []);

  const applySupabaseSession = useCallback(async (accessToken: string) => {
    try {
      const currentUser = await getCurrentUser(accessToken);
      setAuthenticatedSession({
        user: currentUser,
        accessToken,
      });
      setError(null);
      setSessionState("authenticated");
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        await getSupabaseClient().auth.signOut();
        setAuthenticatedSession(null);
        setError(null);
        setSessionState("unauthenticated");
        return;
      }

      setAuthenticatedSession(null);
      setError(err instanceof Error ? err.message : "Falha ao validar usuário.");
      setSessionState("unauthenticated");
    }
  }, [setAuthenticatedSession]);

  useEffect(() => {
    let isMounted = true;

    async function loadInitialSession() {
      if (!isSupabaseConfigured()) {
        if (!isMounted) {
          return;
        }
        setAuthenticatedSession(null);
        setError("Supabase não está configurado no frontend.");
        setSessionState("unauthenticated");
        return;
      }

      const supabase = getSupabaseClient();
      const { data } = await supabase.auth.getSession();

      if (!isMounted) {
        return;
      }

      if (!data.session) {
        setAuthenticatedSession(null);
        setError(null);
        setSessionState("unauthenticated");
        return;
      }

      await applySupabaseSession(data.session.access_token);
    }

    void loadInitialSession();

    return () => {
      isMounted = false;
    };
  }, [applySupabaseSession, setAuthenticatedSession]);

  useEffect(() => {
    if (!isSupabaseConfigured()) {
      return;
    }

    const supabase = getSupabaseClient();
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event, authSession) => {
      if (event === "INITIAL_SESSION") {
        return;
      }

      if (!authSession) {
        setAuthenticatedSession(null);
        setError(null);
        setSessionState("unauthenticated");
        return;
      }

      if (event === "TOKEN_REFRESHED") {
        setSession((currentSession) => {
          if (!currentSession) {
            return currentSession;
          }

          const nextSession = {
            ...currentSession,
            accessToken: authSession.access_token,
          };
          sessionRef.current = nextSession;
          return nextSession;
        });
        return;
      }

      if (sessionRef.current?.accessToken === authSession.access_token) {
        return;
      }

      if (!sessionRef.current) {
        setSessionState("checking");
      }
      void applySupabaseSession(authSession.access_token);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [applySupabaseSession, setAuthenticatedSession]);

  const value = useMemo(
    () => ({
      sessionState,
      session,
      error,
    }),
    [error, session, sessionState],
  );

  return <AuthSessionContext.Provider value={value}>{children}</AuthSessionContext.Provider>;
}
