import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, handleApiError } from "~/utils/shared/api";
import type { Booking, BookingRequest } from "~/utils/shared/types";

export function useBooking(bookingId: string | undefined) {
  return useQuery({
    queryKey: ["bookings", bookingId],
    queryFn: async (): Promise<Booking> => {
      const response = await api.get<Booking>(`/api/bookings/${bookingId}`);
      return response.data;
    },
    enabled: !!bookingId,
  });
}

export function useUserBookings(userId: string | undefined) {
  return useQuery({
    queryKey: ["bookings", "user", userId],
    queryFn: async (): Promise<Booking[]> => {
      const response = await api.get<Booking[]>(`/api/bookings/user/${userId}`);
      return response.data;
    },
    enabled: !!userId,
    staleTime: 60 * 1000,
  });
}

export function useLockSeats() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: { showId: string; seatIds: string[] }): Promise<{ lockId: string; expiresAt: string }> => {
      const response = await api.post("/api/bookings/lock-seats", data);
      return response.data;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["shows", variables.showId, "seats"] });
    },
    onError: (error) => {
      const apiError = handleApiError(error);
      throw apiError;
    },
  });
}

export function useCreateBooking() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (bookingData: BookingRequest): Promise<Booking> => {
      const response = await api.post<Booking>("/api/bookings/confirm", bookingData);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["bookings"] });
      queryClient.invalidateQueries({ queryKey: ["shows", data.showId, "seats"] });
    },
    onError: (error) => {
      const apiError = handleApiError(error);
      throw apiError;
    },
  });
}

export function useCancelBooking() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (bookingId: string): Promise<void> => {
      await api.delete(`/api/bookings/${bookingId}`);
    },
    onSuccess: (data, bookingId) => {
      queryClient.invalidateQueries({ queryKey: ["bookings"] });
      queryClient.invalidateQueries({ queryKey: ["bookings", bookingId] });
    },
    onError: (error) => {
      const apiError = handleApiError(error);
      throw apiError;
    },
  });
}
