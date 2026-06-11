import { useRoutes } from "react-router-dom";
import type { ReactNode } from "react";
import { appRoutes } from "@/routes/routes";

export function App(): ReactNode {
  return useRoutes(appRoutes);
}
