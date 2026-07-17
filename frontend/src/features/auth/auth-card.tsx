"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { getSupabaseClient, isSupabaseConfigured } from "@/lib/supabase";
import type { AuthFormValues, AuthMode } from "@/types";

import styles from "./auth-card.module.css";

const authSchema = z.object({
  email: z.string().email("Informe um e-mail valido."),
  password: z.string().min(6, "A senha precisa ter pelo menos 6 caracteres."),
});

type AuthCardProps = {
  mode: AuthMode;
};

export function AuthCard({ mode }: AuthCardProps) {
  const router = useRouter();
  const [formMessage, setFormMessage] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const isSignup = mode === "signup";

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<AuthFormValues>({
    resolver: zodResolver(authSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  async function onSubmit(values: AuthFormValues) {
    setFormError(null);
    setFormMessage(null);

    if (!isSupabaseConfigured()) {
      setFormError("Configure NEXT_PUBLIC_SUPABASE_URL e NEXT_PUBLIC_SUPABASE_ANON_KEY.");
      return;
    }

    const supabase = getSupabaseClient();
    const result = isSignup
      ? await supabase.auth.signUp(values)
      : await supabase.auth.signInWithPassword(values);

    if (result.error) {
      setFormError(result.error.message);
      return;
    }

    if (isSignup && !result.data.session) {
      setFormMessage("Cadastro criado. Confirme seu e-mail antes de entrar.");
      return;
    }

    router.replace("/dashboard");
  }

  return (
    <section className={styles.card} aria-labelledby="auth-title">
      <div className={styles.header}>
        <p className={styles.eyebrow}>Training Intelligence</p>
        <h1 id="auth-title" className={styles.title}>
          {isSignup ? "Criar sua conta" : "Entrar na sua conta"}
        </h1>
        <p className={styles.description}>
          {isSignup
            ? "Comece seu histórico de treinos com uma base organizada desde o primeiro registro."
            : "Acesse seu histórico, registre sessões e acompanhe sinais de evolução com mais clareza."}
        </p>
      </div>

      <form className={styles.form} onSubmit={handleSubmit(onSubmit)}>
        <label className={styles.field}>
          <span>E-mail</span>
          <input
            className={styles.input}
            type="email"
            autoComplete="email"
            placeholder="seu@email.com"
            {...register("email")}
          />
          {errors.email ? <small className={styles.error}>{errors.email.message}</small> : null}
        </label>

        <label className={styles.field}>
          <span>Senha</span>
          <input
            className={styles.input}
            type="password"
            autoComplete={isSignup ? "new-password" : "current-password"}
            placeholder="Sua senha"
            {...register("password")}
          />
          {errors.password ? (
            <small className={styles.error}>{errors.password.message}</small>
          ) : null}
        </label>

        {formError ? <p className={styles.errorBox}>{formError}</p> : null}
        {formMessage ? <p className={styles.successBox}>{formMessage}</p> : null}

        <button className={styles.submit} type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Processando..." : isSignup ? "Criar conta" : "Entrar"}
        </button>
      </form>

      <p className={styles.switch}>
        {isSignup ? "Já tem uma conta?" : "Ainda não tem uma conta?"}{" "}
        <Link href={isSignup ? "/login" : "/signup"}>
          {isSignup ? "Entrar" : "Criar conta"}
        </Link>
      </p>
    </section>
  );
}
