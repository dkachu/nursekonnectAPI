import { getApiErrorMessage } from "@/api/client";

export function getUserErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return getApiErrorMessage(error);
}
