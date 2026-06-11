import { ratingApi } from "@/api/rating.api";
import type { Rating, RatingPayload } from "@/types";

export class RatingService {
  getRatings(): Promise<Rating[]> {
    return ratingApi.listRatings();
  }

  submitRating(payload: RatingPayload): Promise<Rating> {
    return ratingApi.createRating(payload);
  }
}

export const ratingService = new RatingService();
