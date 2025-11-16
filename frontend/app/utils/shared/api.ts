import axios, { AxiosError, AxiosRequestConfig } from "axios";
import { API_BASE_URL, AUTH_TOKEN_KEY, REFRESH_TOKEN_KEY } from "./constants";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
        if (!refreshToken) {
          throw new Error("No refresh token available");
        }

        const response = await axios.post(`${API_BASE_URL}/api/users/refresh`, {
          refreshToken,
        });

        const { accessToken } = response.data;
        localStorage.setItem(AUTH_TOKEN_KEY, accessToken);

        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${accessToken}`;
        }

        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem(AUTH_TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        window.location.href = "/auth/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export interface ApiError {
  message: string;
  status: number;
  errors?: Record<string, string[]>;
}

export function handleApiError(error: unknown): ApiError {
  if (axios.isAxiosError(error)) {
    return {
      message: error.response?.data?.message || error.message,
      status: error.response?.status || 500,
      errors: error.response?.data?.errors,
    };
  }

  if (error instanceof Error) {
    return {
      message: error.message,
      status: 500,
    };
  }

  return {
    message: "An unexpected error occurred",
    status: 500,
  };
}

export async function getAuthToken(): Promise<string | null> {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

export async function setAuthToken(token: string): Promise<void> {
  localStorage.setItem(AUTH_TOKEN_KEY, token);
}

export async function removeAuthToken(): Promise<void> {
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}
