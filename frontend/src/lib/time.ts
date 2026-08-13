export function formatRestTimeInput(value: string) {
  if (value.includes(":")) {
    const [minutes = "", seconds = ""] = value.split(":");
    return `${minutes.replace(/\D/g, "").slice(0, 3)}:${seconds.replace(/\D/g, "").slice(0, 2)}`;
  }

  const digits = value.replace(/\D/g, "").slice(0, 5);
  if (digits.length <= 2) {
    return digits;
  }

  return `${digits.slice(0, -2)}:${digits.slice(-2)}`;
}

export function normalizeRestTimeInput(value: string) {
  const formattedValue = formatRestTimeInput(value);
  if (!formattedValue) {
    return "";
  }

  const [minutesValue, secondsValue = ""] = formattedValue.split(":");
  const minutes = Number(minutesValue || "0");
  const seconds = Number(secondsValue.padStart(2, "0"));

  if (!Number.isFinite(minutes) || !Number.isFinite(seconds)) {
    return "";
  }

  return `${Math.min(minutes, 600)}:${String(Math.min(seconds, 59)).padStart(2, "0")}`;
}

export function parseRestTimeToSeconds(value: string) {
  const normalizedValue = normalizeRestTimeInput(value);
  if (!normalizedValue) {
    return null;
  }

  const [minutes, seconds] = normalizedValue.split(":").map(Number);
  return minutes * 60 + seconds;
}

export function formatSecondsToRestTime(restSeconds: number | null) {
  if (restSeconds === null) {
    return "";
  }

  const minutes = Math.floor(restSeconds / 60);
  const seconds = String(restSeconds % 60).padStart(2, "0");
  return `${minutes}:${seconds}`;
}
