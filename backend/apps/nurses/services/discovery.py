"""Nearby nurse discovery services."""

from __future__ import annotations

import json
import math
import urllib.parse
import urllib.request
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django.conf import settings
from django.contrib.gis.geos import Point

from apps.nurses.models import NurseProfile
from apps.patients.models import PatientProfile
from apps.tracking.selectors import LocationSelector
from apps.tracking.services.location_updates import LocationFreshnessService


@dataclass(frozen=True)
class RouteEstimate:
    """Road-network distance and travel time from OSRM."""

    distance_km: float
    estimated_travel_time: int


@dataclass(frozen=True)
class NearbyNurseResult:
    """Ranked nearby nurse discovery result."""

    nurse: NurseProfile
    distance_km: float
    estimated_travel_time: int
    specialization_match: bool


class OSRMRouteError(ValueError):
    """Raised when OSRM cannot return a valid route estimate."""


class OSRMRouteService:
    """Fetch road-network route estimates from OSRM."""

    def route(self, *, origin: Point, destination: Point) -> RouteEstimate:
        """Return OSRM road distance and estimated travel time in minutes."""
        url = self._route_url(origin=origin, destination=destination)
        request = urllib.request.Request(url, headers={"Accept": "application/json"})

        try:
            with urllib.request.urlopen(  # noqa: S310 - URL is configured service endpoint.
                request,
                timeout=settings.OSRM_REQUEST_TIMEOUT_SECONDS,
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (OSError, TimeoutError, json.JSONDecodeError) as error:
            raise OSRMRouteError("OSRM route lookup failed.") from error

        return self._parse_route(payload)

    def _route_url(self, *, origin: Point, destination: Point) -> str:
        """Build an OSRM route API URL using longitude,latitude coordinate order."""
        base_url = str(settings.OSRM_BASE_URL).rstrip("/")
        coordinates = f"{origin.x:.6f},{origin.y:.6f};" f"{destination.x:.6f},{destination.y:.6f}"
        query = urllib.parse.urlencode({"overview": "false"})
        return f"{base_url}/route/v1/driving/{coordinates}?{query}"

    def _parse_route(self, payload: dict[str, Any]) -> RouteEstimate:
        """Parse the first OSRM route into the public estimate shape."""
        routes = payload.get("routes")
        if not routes:
            raise OSRMRouteError("OSRM returned no route.")

        route = routes[0]
        try:
            distance_m = float(route["distance"])
            duration_seconds = float(route["duration"])
        except (KeyError, TypeError, ValueError) as error:
            raise OSRMRouteError("OSRM route response is invalid.") from error

        return RouteEstimate(
            distance_km=round(distance_m / 1000, 1),
            estimated_travel_time=max(1, math.ceil(duration_seconds / 60)),
        )


class NearbyNurseDiscoveryService:
    """Discover and rank eligible nurses near a patient's fresh GPS location."""

    def __init__(
        self,
        *,
        route_service: OSRMRouteService | None = None,
        location_selector: LocationSelector | None = None,
    ) -> None:
        self.route_service = route_service or OSRMRouteService()
        self.location_selector = location_selector or LocationSelector()

    def discover(
        self,
        *,
        patient: PatientProfile,
        specialization_code: str | None = None,
        limit: int = 20,
    ) -> list[NearbyNurseResult]:
        """Return OSRM-ranked nearby nurses that satisfy platform eligibility rules."""
        if patient.current_location is None:
            raise ValueError("Fresh patient GPS location is required before discovering nurses.")

        if LocationFreshnessService().is_stale(patient.last_location_update):
            raise ValueError("Fresh patient GPS location is required before discovering nurses.")

        origin = patient.current_location
        radius_km = settings.NEARBY_NURSE_RADIUS_KM
        candidates = list(
            self.location_selector.candidate_nurses_within_radius(
                origin=origin,
                radius_km=radius_km,
            )[: settings.NEARBY_NURSE_CANDIDATE_LIMIT]
        )

        results: list[NearbyNurseResult] = []
        for nurse in candidates:
            if nurse.current_location is None:
                continue
            try:
                estimate = self.route_service.route(
                    origin=origin,
                    destination=nurse.current_location,
                )
            except OSRMRouteError:
                continue

            if estimate.distance_km > radius_km:
                continue

            results.append(
                NearbyNurseResult(
                    nurse=nurse,
                    distance_km=estimate.distance_km,
                    estimated_travel_time=estimate.estimated_travel_time,
                    specialization_match=self._matches_specialization(
                        nurse=nurse,
                        specialization_code=specialization_code,
                    ),
                )
            )

        return sorted(results, key=self._ranking_key)[:limit]

    def _matches_specialization(
        self,
        *,
        nurse: NurseProfile,
        specialization_code: str | None,
    ) -> bool:
        """Return whether a nurse has the requested specialization code."""
        if not specialization_code:
            return False
        return any(
            specialization.code == specialization_code
            for specialization in nurse.specializations.all()
        )

    def _ranking_key(self, result: NearbyNurseResult) -> tuple[float, Decimal, int, bool]:
        """Rank by distance, reputation, response speed, then specialization match."""
        response_speed = (
            result.nurse.average_response_seconds
            if result.nurse.average_response_seconds > 0
            else 999999
        )
        return (
            result.distance_km,
            -result.nurse.reputation_score,
            response_speed,
            not result.specialization_match,
        )
