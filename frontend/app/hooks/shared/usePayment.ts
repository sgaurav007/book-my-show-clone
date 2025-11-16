import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, handleApiError } from "~/utils/shared/api";
import type { Payment, PaymentRequest } from "~/utils/shared/types";

export function usePayment(paymentId: string | undefined) {
  return useQuery({
    queryKey: ["payments", paymentId],
    queryFn: async (): Promise<Payment> => {
      const response = await api.get<Payment>(`/api/payments/${paymentId}`);
      return response.data;
    },
    enabled: !!paymentId,
  });
}

export function useInitiatePayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (paymentData: PaymentRequest): Promise<Payment> => {
      const response = await api.post<Payment>("/api/payments/initiate", paymentData);
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      queryClient.invalidateQueries({ queryKey: ["bookings", data.bookingId] });
    },
    onError: (error) => {
      const apiError = handleApiError(error);
      throw apiError;
    },
  });
}

export function useProcessRefund() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (paymentId: string): Promise<Payment> => {
      const response = await api.post<Payment>(`/api/payments/refund`, { paymentId });
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["payments"] });
      queryClient.invalidateQueries({ queryKey: ["payments", data.id] });
      queryClient.invalidateQueries({ queryKey: ["bookings", data.bookingId] });
    },
    onError: (error) => {
      const apiError = handleApiError(error);
      throw apiError;
    },
  });
}
