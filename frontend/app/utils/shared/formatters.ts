import { format, parseISO } from "date-fns";

export function formatCurrency(amount: number, currency: string = "INR"): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
  }).format(amount);
}

export function formatDate(date: string | Date, formatStr: string = "dd MMM yyyy"): string {
  const dateObj = typeof date === "string" ? parseISO(date) : date;
  return format(dateObj, formatStr);
}

export function formatTime(date: string | Date): string {
  const dateObj = typeof date === "string" ? parseISO(date) : date;
  return format(dateObj, "hh:mm a");
}

export function formatDateTime(date: string | Date): string {
  const dateObj = typeof date === "string" ? parseISO(date) : date;
  return format(dateObj, "dd MMM yyyy, hh:mm a");
}

export function formatDuration(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (hours === 0) {
    return `${mins}min`;
  }
  return mins === 0 ? `${hours}h` : `${hours}h ${mins}min`;
}

export function formatPhoneNumber(phone: string): string {
  const cleaned = phone.replace(/\D/g, "");
  const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
  if (match) {
    return `(${match[1]}) ${match[2]}-${match[3]}`;
  }
  return phone;
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength) + "...";
}

export function capitalizeFirstLetter(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
}

export function formatRating(rating: number): string {
  return rating.toFixed(1);
}
