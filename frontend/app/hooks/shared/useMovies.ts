import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, handleApiError } from "~/utils/shared/api";
import type { Movie, MovieFilter, Show, ShowFilter } from "~/utils/shared/types";

export function useMovies(filters?: MovieFilter) {
  return useQuery({
    queryKey: ["movies", filters],
    queryFn: async (): Promise<Movie[]> => {
      const params = new URLSearchParams();
      if (filters?.genre) params.append("genre", filters.genre);
      if (filters?.language) params.append("language", filters.language);
      if (filters?.rating) params.append("rating", filters.rating);
      if (filters?.search) params.append("search", filters.search);

      const response = await api.get<Movie[]>(`/api/catalog/movies?${params.toString()}`);
      return response.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useMovie(movieId: string | undefined) {
  return useQuery({
    queryKey: ["movies", movieId],
    queryFn: async (): Promise<Movie> => {
      const response = await api.get<Movie>(`/api/catalog/movies/${movieId}`);
      return response.data;
    },
    enabled: !!movieId,
    staleTime: 5 * 60 * 1000,
  });
}

export function useShows(filters?: ShowFilter) {
  return useQuery({
    queryKey: ["shows", filters],
    queryFn: async (): Promise<Show[]> => {
      const params = new URLSearchParams();
      if (filters?.movieId) params.append("movieId", filters.movieId);
      if (filters?.city) params.append("city", filters.city);
      if (filters?.date) params.append("date", filters.date);
      if (filters?.theaterId) params.append("theaterId", filters.theaterId);

      const response = await api.get<Show[]>(`/api/catalog/shows?${params.toString()}`);
      return response.data;
    },
    staleTime: 2 * 60 * 1000,
  });
}

export function useShow(showId: string | undefined) {
  return useQuery({
    queryKey: ["shows", showId],
    queryFn: async (): Promise<Show> => {
      const response = await api.get<Show>(`/api/catalog/shows/${showId}`);
      return response.data;
    },
    enabled: !!showId,
    staleTime: 2 * 60 * 1000,
  });
}

export function useShowSeats(showId: string | undefined) {
  return useQuery({
    queryKey: ["shows", showId, "seats"],
    queryFn: async () => {
      const response = await api.get(`/api/catalog/shows/${showId}/seats`);
      return response.data;
    },
    enabled: !!showId,
    refetchInterval: 30000,
  });
}

export function useCreateMovie() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (movieData: Partial<Movie>): Promise<Movie> => {
      const response = await api.post<Movie>("/api/catalog/movies", movieData);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["movies"] });
    },
    onError: (error) => {
      const apiError = handleApiError(error);
      throw apiError;
    },
  });
}

export function useUpdateMovie() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Movie> }): Promise<Movie> => {
      const response = await api.put<Movie>(`/api/catalog/movies/${id}`, data);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["movies"] });
      queryClient.invalidateQueries({ queryKey: ["movies", data.id] });
    },
    onError: (error) => {
      const apiError = handleApiError(error);
      throw apiError;
    },
  });
}

export function useDeleteMovie() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string): Promise<void> => {
      await api.delete(`/api/catalog/movies/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["movies"] });
    },
    onError: (error) => {
      const apiError = handleApiError(error);
      throw apiError;
    },
  });
}
