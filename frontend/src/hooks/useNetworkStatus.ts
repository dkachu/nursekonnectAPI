import { useEffect, useState } from "react";

interface NetworkStatus {
  online: boolean;
  slowConnection: boolean;
}

interface NavigatorConnection {
  effectiveType?: string;
  saveData?: boolean;
}

export function useNetworkStatus(): NetworkStatus {
  const [online, setOnline] = useState(() => navigator.onLine);
  const [slowConnection] = useState(() => {
    const connection = (navigator as Navigator & { connection?: NavigatorConnection }).connection;
    return Boolean(
      connection?.saveData || ["slow-2g", "2g"].includes(connection?.effectiveType ?? ""),
    );
  });

  useEffect(() => {
    const updateOnline = (): void => setOnline(true);
    const updateOffline = (): void => setOnline(false);

    window.addEventListener("online", updateOnline);
    window.addEventListener("offline", updateOffline);
    return () => {
      window.removeEventListener("online", updateOnline);
      window.removeEventListener("offline", updateOffline);
    };
  }, []);

  return { online, slowConnection };
}
