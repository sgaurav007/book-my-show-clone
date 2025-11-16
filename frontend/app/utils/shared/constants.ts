export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";
export const APP_NAME = import.meta.env.VITE_APP_NAME || "BookMyShow";

export const AUTH_TOKEN_KEY = "auth_token";
export const REFRESH_TOKEN_KEY = "refresh_token";
export const USER_KEY = "user_data";

export const SEAT_STATUS = {
  AVAILABLE: "AVAILABLE",
  BOOKED: "BOOKED",
  SELECTED: "SELECTED",
  LOCKED: "LOCKED",
} as const;

export const SEAT_TYPE = {
  NORMAL: "NORMAL",
  PREMIUM: "PREMIUM",
  VIP: "VIP",
} as const;

export const BOOKING_STATUS = {
  PENDING: "PENDING",
  CONFIRMED: "CONFIRMED",
  CANCELLED: "CANCELLED",
  EXPIRED: "EXPIRED",
} as const;

export const PAYMENT_STATUS = {
  PENDING: "PENDING",
  SUCCESS: "SUCCESS",
  FAILED: "FAILED",
  REFUNDED: "REFUNDED",
} as const;

export const PAYMENT_METHOD = {
  CREDIT_CARD: "CREDIT_CARD",
  DEBIT_CARD: "DEBIT_CARD",
  UPI: "UPI",
  NET_BANKING: "NET_BANKING",
  WALLET: "WALLET",
} as const;

export const MOVIE_GENRE = {
  ACTION: "ACTION",
  COMEDY: "COMEDY",
  DRAMA: "DRAMA",
  HORROR: "HORROR",
  ROMANCE: "ROMANCE",
  THRILLER: "THRILLER",
  SCI_FI: "SCI_FI",
  FANTASY: "FANTASY",
  DOCUMENTARY: "DOCUMENTARY",
  ANIMATION: "ANIMATION",
} as const;

export const MOVIE_LANGUAGE = {
  ENGLISH: "ENGLISH",
  HINDI: "HINDI",
  TAMIL: "TAMIL",
  TELUGU: "TELUGU",
  MALAYALAM: "MALAYALAM",
  KANNADA: "KANNADA",
  BENGALI: "BENGALI",
  MARATHI: "MARATHI",
} as const;

export const MOVIE_RATING = {
  U: "U",
  UA: "UA",
  A: "A",
  S: "S",
} as const;

export const USER_ROLE = {
  USER: "USER",
  ADMIN: "ADMIN",
  THEATER_OWNER: "THEATER_OWNER",
} as const;

export const SEAT_LOCK_DURATION = 15 * 60 * 1000; // 15 minutes in milliseconds
export const MAX_SEATS_PER_BOOKING = 10;

export const ROUTES = {
  HOME: "/",
  MOVIES: "/movies",
  MOVIE_DETAIL: "/movies/:movieId",
  THEATERS: "/theaters",
  BOOKING: "/booking/:showId",
  PAYMENT: "/payment",
  PAYMENT_SUCCESS: "/payment/success",
  PROFILE: "/profile",
  MY_BOOKINGS: "/profile/bookings",
  LOGIN: "/auth/login",
  REGISTER: "/auth/register",
  ADMIN_DASHBOARD: "/admin/dashboard",
  ADMIN_MOVIES: "/admin/movies",
  ADMIN_THEATERS: "/admin/theaters",
  ADMIN_SHOWS: "/admin/shows",
} as const;

export const SEAT_COLORS = {
  AVAILABLE: "#4CAF50", // Green
  BOOKED: "#F44336", // Red
  SELECTED: "#2196F3", // Blue
  LOCKED: "#FF9800", // Orange
} as const;
