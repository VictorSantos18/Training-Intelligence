"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import type { BodyRegion, PainRecordFormValues, TrainingSet } from "@/types";

import styles from "./pain-record-form.module.css";

const painSchema = z
  .object({
    training_set_id: z.string().optional().default(""),
    body_region_id: z.string().min(1, "Escolha a região."),
    side: z.enum(["LEFT", "RIGHT", "BILATERAL", "NOT_APPLICABLE"]),
    moment: z.enum(["PRE_SESSION", "DURING_SET", "POST_SESSION", "CHECKIN_24H", "CHECKIN_48H"]),
    intensity: z.string().min(1, "Informe a intensidade."),
    description: z.string().optional().default(""),
    notes: z.string().optional().default(""),
  })
  .refine((values) => values.moment !== "DURING_SET" || values.training_set_id !== "", {
    message: "Dor durante set precisa de um set.",
    path: ["training_set_id"],
  });

type PainRecordFormProps = {
  bodyRegions: BodyRegion[];
  canChooseSet?: boolean;
  initialValues?: PainRecordFormValues;
  resetOnSubmit?: boolean;
  sets: TrainingSet[];
  submitLabel?: string;
  submittingLabel?: string;
  onSubmit: (values: PainRecordFormValues) => Promise<void>;
};

const emptyValues: PainRecordFormValues = {
  training_set_id: "",
  body_region_id: "",
  side: "NOT_APPLICABLE",
  moment: "POST_SESSION",
  intensity: "",
  description: "",
  notes: "",
};

function getDefaultValues(initialValues?: PainRecordFormValues) {
  return initialValues ?? emptyValues;
}

export function PainRecordForm({
  bodyRegions,
  canChooseSet = true,
  initialValues,
  resetOnSubmit = true,
  sets,
  submitLabel = "Registrar dor",
  submittingLabel = "Registrando...",
  onSubmit,
}: PainRecordFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<PainRecordFormValues>({
    resolver: zodResolver(painSchema),
    defaultValues: getDefaultValues(initialValues),
  });
  const disabledSetValue = initialValues?.training_set_id ?? "";

  useEffect(() => {
    reset(getDefaultValues(initialValues));
  }, [initialValues, reset]);

  async function submit(values: PainRecordFormValues) {
    await onSubmit(values);
    if (resetOnSubmit) {
      reset(emptyValues);
    }
  }

  return (
    <form className={styles.form} onSubmit={handleSubmit(submit)}>
      <label>
        <span>Momento</span>
        <select {...register("moment")}>
          <option value="PRE_SESSION">Antes</option>
          <option value="DURING_SET">Durante set</option>
          <option value="POST_SESSION">Depois</option>
          <option value="CHECKIN_24H">Check-in 24h</option>
          <option value="CHECKIN_48H">Check-in 48h</option>
        </select>
      </label>

      <label>
        <span>Set</span>
        {canChooseSet ? (
          <select {...register("training_set_id")}>
            <option value="">Sem set específico</option>
            {sets.map((set) => (
              <option key={set.id} value={set.id}>
                Set {set.set_number}
              </option>
            ))}
          </select>
        ) : (
          <>
            <input type="hidden" {...register("training_set_id")} />
            <select disabled value={disabledSetValue} onChange={() => undefined}>
              <option value="">Sem set específico</option>
              {sets.map((set) => (
                <option key={set.id} value={set.id}>
                  Set {set.set_number}
                </option>
              ))}
            </select>
          </>
        )}
        {errors.training_set_id ? <small>{errors.training_set_id.message}</small> : null}
      </label>

      <label>
        <span>Região</span>
        <select {...register("body_region_id")}>
          <option value="">Selecione</option>
          {bodyRegions.map((region) => (
            <option key={region.id} value={region.id}>
              {region.name}
            </option>
          ))}
        </select>
        {errors.body_region_id ? <small>{errors.body_region_id.message}</small> : null}
      </label>

      <label>
        <span>Lado</span>
        <select {...register("side")}>
          <option value="NOT_APPLICABLE">Não aplicável</option>
          <option value="LEFT">Esquerdo</option>
          <option value="RIGHT">Direito</option>
          <option value="BILATERAL">Bilateral</option>
        </select>
      </label>

      <label>
        <span>Intensidade</span>
        <input max="10" min="0" type="number" {...register("intensity")} />
        {errors.intensity ? <small>{errors.intensity.message}</small> : null}
      </label>

      <label>
        <span>Descrição</span>
        <input
          placeholder="Ex: pontada, tensão, desconforto..."
          type="text"
          {...register("description")}
        />
      </label>

      <label>
        <span>Notas</span>
        <textarea rows={3} {...register("notes")} />
      </label>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? submittingLabel : submitLabel}
      </button>
    </form>
  );
}
