import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, handleApiError } from "~/utils/shared/api";
import { AUTH_TOKEN_KEY, REFRESH_TOKEN_KEY, USER_KEY } from "~/utils/shared/constants";
import type { User, LoginRequest, LoginResponse, RegisterRequest } from "~/utils/shared/types";

export function useAuth() {
  const queryClient = useQueryClient();

  const { data: user, isLoading } = useQuery({
    queryKey: ["auth", "user"],
    queryFn: async (): Promise<User | null> => {
      const token = localStorage.getItem(AUTH_TOKEN_KEY);
      if (!token) {
        return null;
      }

      try {
        const response = await api.get<User>("/api/users/profile");
        return response.data;
      } catch (error) {
        localStorage.removeItem(AUTH_TOKEN_KEY);
        localStorage.removeItem(REFRESH_TOKEN_KEY);
        return null;
      }
    },
    staleTime: 5 * 60 * 1000,
  });

  const loginMutation = useMutation({
    mutationFn: async (credentials: LoginRequest): Promise<LoginResponse> => {
      const response = await api.post<LoginResponse>("/api/users/login", credentials);
      return response.data;
    },
    onSuccess: (data) => {
      localStorage.setItem(AUTH_TOKEN_KEY, data.accessToken);
      localStorage.setItem(REFRESH_TOKEN_KEY, data.refreshToken);
      localStorage.setItem(USER_KEY, JSON.stringify(data.user));
      queryClient.setQueryData(["auth", "user"], data.user);
    },
    onError: (error) => {
      const apiError = handleApiError(error);
      throw apiError;
    },
  });

  const registerMutation = useMutation({
    mutationFn: async (userData: RegisterRequest): Promise<LoginResponse> => {
      const response = await api.post<LoginResponse>("/api/users/register", userData);
      return response.data;
    },
    onSuccess: (data) => {
      localStorage.setItem(AUTH_TOKEN_KEY, data.accessToken);
      localStorage.setItem(REFRESH_TOKEN_KEY, data.refreshToken);
      localStorage.setItem(USER_KEY, JSON.stringify(data.user));
      queryClient.setQueryData(["auth", "user"], data.user);
    },
    onError: (error) => {
      const apiError = handleApiError(error);
      throw apiError;
    },
  });

  const logoutMutation = useMutation({
    mutationFn: async (): Promise<void> => {
      await api.post("/api/users/logout");
    },
    onSuccess: () => {
      localStorage.removeItem(AUTH_TOKEN_KEY);
      localStorage.removeItem(REFRESH_TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      queryClient.setQueryData(["auth", "user"], null);
      queryClient.clear();
    },
  });

  return {
    user,
    isLoading,
    isAuthenticated: !!user,
    login: loginMutation.mutate,
    loginAsync: loginMutation.mutateAsync,
    isLoggingIn: loginMutation.isPending,
    loginError: loginMutation.error,
    register: registerMutation.mutate,
    registerAsync: registerMutation.mutateAsync,
    isRegistering: registerMutation.isPending,
    registerError: registerMutation.error,
    logout: logoutMutation.mutate,
    isLoggingOut: logoutMutation.isPending,
  };
}
