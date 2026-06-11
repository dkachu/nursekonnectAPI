export interface ApiEndpoint {
  method: "GET" | "POST" | "PATCH" | "DELETE";
  path: string;
  domain: string;
  description: string;
  surface: string;
}

export interface ApiErrorPayload {
  detail?: string;
  message?: string;
  [key: string]: unknown;
}
