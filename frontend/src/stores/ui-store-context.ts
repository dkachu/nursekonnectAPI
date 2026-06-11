import { createContext } from "react";

export type ThemeMode = "light";

export interface UIStoreValue {
  sidebarOpen: boolean;
  theme: ThemeMode;
  loading: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
  setLoading: (loading: boolean) => void;
}

export const UIStoreContext = createContext<UIStoreValue | null>(null);
