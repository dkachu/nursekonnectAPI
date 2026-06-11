/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  readonly VITE_APP_NAME: string;
  readonly VITE_MAP_PROVIDER: "openstreetmap";
}

declare module "*.svg" {
  const src: string;
  export default src;
}
