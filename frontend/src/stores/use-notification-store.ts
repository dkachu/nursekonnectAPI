import { useContext } from "react";
import {
  NotificationStoreContext,
  type NotificationStoreValue,
} from "@/stores/notification-store-context";

export function useNotificationStore(): NotificationStoreValue {
  const value = useContext(NotificationStoreContext);
  if (!value) {
    throw new Error("useNotificationStore must be used within NotificationStoreProvider");
  }
  return value;
}
