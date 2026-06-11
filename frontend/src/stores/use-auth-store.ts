import { useContext } from "react";
import { AuthStoreContext, type AuthStoreValue } from "@/stores/auth-store-context";

export function useAuthStore(): AuthStoreValue {
  const value = useContext(AuthStoreContext);
  if (!value) {
    throw new Error("useAuthStore must be used within AuthStoreProvider");
  }
  return value;
}
