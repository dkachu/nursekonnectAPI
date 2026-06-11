import { useCallback, useMemo, useState, type ReactNode } from "react";
import { UIStoreContext, type UIStoreValue } from "@/stores/ui-store-context";

export function UIStoreProvider({ children }: { children: ReactNode }): ReactNode {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const toggleSidebar = useCallback((): void => {
    setSidebarOpen((open) => !open);
  }, []);

  const value = useMemo<UIStoreValue>(
    () => ({
      sidebarOpen,
      theme: "light",
      loading,
      setSidebarOpen,
      toggleSidebar,
      setLoading,
    }),
    [loading, sidebarOpen, toggleSidebar],
  );

  return <UIStoreContext.Provider value={value}>{children}</UIStoreContext.Provider>;
}
