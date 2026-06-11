import { apiClient } from "@/api/client";
import type { Rating, RatingPayload } from "@/types";

export const ratingApi = {
  async listRatings(): Promise<Rating[]> {
    const response = await apiClient.get<Rating[]>("/api/ratings/");
    return response.data;
  },
  async createRating(payload: RatingPayload): Promise<Rating> {
    const response = await apiClient.post<Rating>("/api/ratings/", payload);
    return response.data;
  },
};
