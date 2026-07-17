"use client";

import { useEffect } from "react";

import styles from "./confirm-dialog.module.css";

type ConfirmDialogTone = "danger" | "default";

type ConfirmDialogProps = {
  cancelLabel?: string;
  confirmLabel: string;
  description: string;
  isOpen: boolean;
  isProcessing?: boolean;
  title: string;
  tone?: ConfirmDialogTone;
  onCancel: () => void;
  onConfirm: () => void;
};

export function ConfirmDialog({
  cancelLabel = "Cancelar",
  confirmLabel,
  description,
  isOpen,
  isProcessing = false,
  title,
  tone = "default",
  onCancel,
  onConfirm,
}: ConfirmDialogProps) {
  useEffect(() => {
    if (!isOpen) {
      return;
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        onCancel();
      }
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onCancel]);

  if (!isOpen) {
    return null;
  }

  return (
    <div className={styles.backdrop} role="presentation" onMouseDown={onCancel}>
      <section
        aria-describedby="confirm-dialog-description"
        aria-labelledby="confirm-dialog-title"
        aria-modal="true"
        className={styles.dialog}
        role="dialog"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className={styles.header}>
          <span className={tone === "danger" ? styles.dangerMark : styles.defaultMark} />
          <div>
            <h2 id="confirm-dialog-title">{title}</h2>
            <p id="confirm-dialog-description">{description}</p>
          </div>
        </div>

        <div className={styles.actions}>
          <button className={styles.cancel} type="button" onClick={onCancel}>
            {cancelLabel}
          </button>
          <button
            className={tone === "danger" ? styles.confirmDanger : styles.confirm}
            type="button"
            disabled={isProcessing}
            onClick={onConfirm}
          >
            {isProcessing ? "Processando..." : confirmLabel}
          </button>
        </div>
      </section>
    </div>
  );
}
