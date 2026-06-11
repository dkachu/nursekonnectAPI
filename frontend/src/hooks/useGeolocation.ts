import { useCallback, useState } from "react";
import type { Coordinates } from "@/types";

interface GeolocationState {
  coordinates: Coordinates | null;
  error: string | null;
  loading: boolean;
  requestLocation: () => Promise<Coordinates>;
}

export function useGeolocation(): GeolocationState {
  const [coordinates, setCoordinates] = useState<Coordinates | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const requestLocation = useCallback(async (): Promise<Coordinates> => {
    setLoading(true);
    setError(null);

    return new Promise<Coordinates>((resolve, reject) => {
      if (!navigator.geolocation) {
        const message = "Geolocation is not supported by this browser.";
        setError(message);
        setLoading(false);
        reject(new Error(message));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          const nextCoordinates = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          };
          setCoordinates(nextCoordinates);
          setLoading(false);
          resolve(nextCoordinates);
        },
        (positionError) => {
          setError(positionError.message);
          setLoading(false);
          reject(new Error(positionError.message));
        },
        { enableHighAccuracy: true, timeout: 15_000, maximumAge: 0 },
      );
    });
  }, []);

  return { coordinates, error, loading, requestLocation };
}
