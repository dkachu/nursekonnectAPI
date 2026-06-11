import axios, { AxiosError, type AxiosInstance, type InternalAxiosRequestConfig } from "axios";
import { appConfig } from "@/config/env";
import type { ApiErrorPayload } from "@/types/api";
import type { RefreshResponse } from "@/types/auth";

let accessToken: string | null = null;
let refreshPromise: Promise<string | null> | null = null;
let unauthorizedHandler: (() => void) | null = null;

export const apiClient: AxiosInstance = axios.create({
  baseURL: appConfig.apiUrl,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

export function setAuthTokens(tokens: { access: string } | null): void {
  accessToken = tokens?.access ?? null;
}

export function getAccessToken(): string | null {
  return accessToken;
}

export function setUnauthorizedHandler(handler: (() => void) | null): void {
  unauthorizedHandler = handler;
}

function attachAuthorization(config: InternalAxiosRequestConfig): InternalAxiosRequestConfig {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
}

async function refreshAccessToken(): Promise<string | null> {
  const response = await axios.post<RefreshResponse>(
    `${appConfig.apiUrl}/api/auth/refresh/`,
    {},
    { withCredentials: true },
  );

  const nextAccess = response.data.access;
  accessToken = nextAccess;
  return nextAccess;
}

apiClient.interceptors.request.use(attachAuthorization);

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiErrorPayload>) => {
    const originalRequest = error.config as
      | (InternalAxiosRequestConfig & { _retry?: boolean })
      | undefined;

    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;
      refreshPromise ??= refreshAccessToken().finally(() => {
        refreshPromise = null;
      });
      const nextAccess = await refreshPromise.catch(() => null);

      if (nextAccess) {
        originalRequest.headers.Authorization = `Bearer ${nextAccess}`;
        return apiClient(originalRequest);
      }

      setAuthTokens(null);
      unauthorizedHandler?.();
    }

    return Promise.reject(error);
  },
);

export function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError<ApiErrorPayload>(error)) {
    return (
      error.response?.data.detail ??
      error.response?.data.message ??
      "The request could not be completed."
    );
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "An unexpected error occurred.";
}
