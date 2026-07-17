"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { getCurrentUser } from "@/lib/api";
import { getSupabaseClient, isSupabaseConfigured } from "@/lib/supabase";
import type { AuthSessionState, AuthenticatedSession } from "@/types";

type AuthenticatedSessionResult = {
  sessionState: AuthSessionState;
  session: AuthenticatedSession | null;
  error: string | null;
};

export function useAuthenticatedSession(): AuthenticatedSessionResult {
  const router = useRouter();
  const [sessionState, setSessionState] = useState<AuthSessionState>("checking");
  const [session, setSession] = useState<AuthenticatedSession | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadSession() {
      if (!isSupabaseConfigured()) {
        setError("Supabase nao esta configurado no frontend.");
        setSessionState("unauthenticated");
        return;
      }

      const supabase = getSupabaseClient();
      const { data } = await supabase.auth.getSession();

      if (!data.session) {
        router.replace("/login");
        return;
      }

      try {
        const currentUser = await getCurrentUser(data.session.access_token);
        if (!isMounted) {
          return;
        }
        setSession({
          user: currentUser,
          accessToken: data.session.access_token,
        });
        setSessionState("authenticated");
      } catch (err) {
        if (!isMounted) {
          return;
        }
        setError(err instanceof Error ? err.message : "Falha ao validar usuario.");
        setSessionState("unauthenticated");
      }
    }

    void loadSession();

    return () => {
      isMounted = false;
    };
  }, [router]);

  return { sessionState, session, error };
}
