import { useContext } from "react";
import { UIStoreContext, type UIStoreValue } from "@/stores/ui-store-context";

export function useUIStore(): UIStoreValue {
  const value = useContext(UIStoreContext);
  if (!value) {
    throw new Error("useUIStore must be used within UIStoreProvider");
  }
  return value;
}
