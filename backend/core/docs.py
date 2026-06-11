"""OpenAPI documentation views."""

from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.http import HttpRequest, HttpResponse


def openapi_schema(_request: HttpRequest) -> HttpResponse:
    """Serve the static OpenAPI schema artifact."""
    schema_path = next(
        path
        for path in [
            Path(settings.PROJECT_ROOT) / "OPENAPI.yaml",
            Path(settings.BASE_DIR) / "OPENAPI.yaml",
        ]
        if path.exists()
    )
    return HttpResponse(schema_path.read_text(encoding="utf-8"), content_type="application/yaml")


def swagger_ui(_request: HttpRequest) -> HttpResponse:
    """Serve Swagger UI for the OpenAPI schema."""
    html = """
<!doctype html>
<html lang="en">
  <head>
    <title>NurseKonnect API Swagger</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css">
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
    <script>
      window.onload = () => {
        window.ui = SwaggerUIBundle({ url: "/api/schema/", dom_id: "#swagger-ui" });
      };
    </script>
  </body>
</html>
"""
    return HttpResponse(html, content_type="text/html")


def redoc_ui(_request: HttpRequest) -> HttpResponse:
    """Serve ReDoc for the OpenAPI schema."""
    html = """
<!doctype html>
<html lang="en">
  <head>
    <title>NurseKonnect API ReDoc</title>
  </head>
  <body>
    <redoc spec-url="/api/schema/"></redoc>
    <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
  </body>
</html>
"""
    return HttpResponse(html, content_type="text/html")
