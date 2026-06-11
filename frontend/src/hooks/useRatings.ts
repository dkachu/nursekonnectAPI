import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ratingService } from "@/services/rating.service";
import type { Rating, RatingPayload } from "@/types";

export function useRatings() {
  return useQuery({ queryKey: ["ratings"], queryFn: () => ratingService.getRatings() });
}

export function useSubmitRating() {
  const queryClient = useQueryClient();
  return useMutation<Rating, Error, RatingPayload>({
    mutationFn: (payload) => ratingService.submitRating(payload),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["ratings"] }),
  });
}
