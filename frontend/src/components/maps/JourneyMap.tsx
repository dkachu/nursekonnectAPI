import "leaflet/dist/leaflet.css";

import L from "leaflet";
import { useEffect, useMemo, useRef, type ReactNode } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Coordinates } from "@/types";

interface JourneyMapProps {
  patientLocation: Coordinates | null;
  nurseLocation: Coordinates | null;
  routeCoordinates?: Coordinates[];
  etaMinutes?: number | null;
}

function toLatLng(coordinates: Coordinates): L.LatLngExpression {
  return [coordinates.latitude, coordinates.longitude];
}

function createMarkerIcon(label: string, variant: "patient" | "nurse"): L.DivIcon {
  return L.divIcon({
    className: "",
    html: `<div class="nk-map-marker nk-map-marker-${variant}" aria-hidden="true">${label}</div>`,
    iconSize: [34, 34],
    iconAnchor: [17, 17],
  });
}

export function JourneyMap({
  patientLocation,
  nurseLocation,
  routeCoordinates = [],
  etaMinutes = null,
}: JourneyMapProps): ReactNode {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const layersRef = useRef<L.LayerGroup | null>(null);

  const routePoints = useMemo<L.LatLngExpression[]>(
    () => routeCoordinates.map(toLatLng),
    [routeCoordinates],
  );

  useEffect(() => {
    if (!containerRef.current || mapRef.current) {
      return;
    }

    const map = L.map(containerRef.current, {
      center: [-1.286389, 36.817223],
      zoom: 12,
      zoomControl: true,
      attributionControl: true,
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map);

    const layers = L.layerGroup().addTo(map);
    mapRef.current = map;
    layersRef.current = layers;

    return () => {
      map.remove();
      mapRef.current = null;
      layersRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    const layers = layersRef.current;

    if (!map || !layers) {
      return;
    }

    layers.clearLayers();
    const bounds = L.latLngBounds([]);

    if (patientLocation) {
      const point = toLatLng(patientLocation);
      L.marker(point, { icon: createMarkerIcon("P", "patient") })
        .bindTooltip("Patient location")
        .addTo(layers);
      bounds.extend(point);
    }

    if (nurseLocation) {
      const point = toLatLng(nurseLocation);
      L.marker(point, { icon: createMarkerIcon("N", "nurse") })
        .bindTooltip("Nurse location")
        .addTo(layers);
      bounds.extend(point);
    }

    if (routePoints.length > 1) {
      L.polyline(routePoints, {
        color: "#0f6cbd",
        opacity: 0.9,
        weight: 5,
      }).addTo(layers);
      routePoints.forEach((point) => bounds.extend(point));
    } else if (patientLocation && nurseLocation) {
      const fallbackRoute = [toLatLng(nurseLocation), toLatLng(patientLocation)];
      L.polyline(fallbackRoute, {
        color: "#0f6cbd",
        dashArray: "6 8",
        opacity: 0.75,
        weight: 4,
      }).addTo(layers);
    }

    if (bounds.isValid()) {
      map.fitBounds(bounds.pad(0.25), { maxZoom: 15 });
    }
  }, [nurseLocation, patientLocation, routePoints]);

  const hasAnyLocation = Boolean(patientLocation || nurseLocation);

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
          <CardTitle>Live Journey Map</CardTitle>
          <p className="text-sm text-muted-foreground">
            {etaMinutes ? `${etaMinutes} min ETA` : "ETA appears after route data is available"}
          </p>
        </div>
      </CardHeader>
      <CardContent>
        <div className="relative overflow-hidden rounded-md border border-border">
          <div ref={containerRef} className="h-[360px] w-full bg-muted" />
          {!hasAnyLocation ? (
            <div className="absolute inset-0 grid place-items-center bg-background/90 px-6 text-center text-sm text-muted-foreground">
              GPS tracking appears here once patient or nurse location is available.
            </div>
          ) : null}
        </div>
        <div className="mt-3 flex flex-wrap gap-3 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-[#0f6cbd]" />
            Patient
          </span>
          <span className="inline-flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full bg-[#127c56]" />
            Nurse
          </span>
          <span>Map data from OpenStreetMap.</span>
        </div>
      </CardContent>
    </Card>
  );
}
