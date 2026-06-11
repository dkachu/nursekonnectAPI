import { z } from "zod";

const envSchema = z.object({
  VITE_API_URL: z.string().url(),
  VITE_APP_NAME: z.string().min(1),
  VITE_MAP_PROVIDER: z.enum(["openstreetmap"]),
  MODE: z.string(),
});

const rawEnv = {
  VITE_API_URL: import.meta.env.VITE_API_URL,
  VITE_APP_NAME: import.meta.env.VITE_APP_NAME,
  VITE_MAP_PROVIDER: import.meta.env.VITE_MAP_PROVIDER,
  MODE: import.meta.env.MODE,
};

const parsedEnv = envSchema.safeParse(rawEnv);

if (!parsedEnv.success) {
  const message = parsedEnv.error.issues
    .map((issue) => `${issue.path.join(".")}: ${issue.message}`)
    .join("; ");
  throw new Error(`Invalid NurseKonnect frontend environment: ${message}`);
}

export const appConfig = {
  apiUrl: parsedEnv.data.VITE_API_URL,
  appName: parsedEnv.data.VITE_APP_NAME,
  mapProvider: parsedEnv.data.VITE_MAP_PROVIDER,
  mode: parsedEnv.data.MODE,
} as const;
