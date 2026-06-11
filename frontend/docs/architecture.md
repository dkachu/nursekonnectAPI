# Frontend Architecture

NurseKonnect uses a route-oriented React architecture.

- `src/app`: application providers and route entry.
- `src/api`: Axios client and endpoint registry.
- `src/auth`: authentication context and auth API calls.
- `src/components`: reusable brand, layout, state, and UI primitives.
- `src/layouts`: public and authenticated page shells.
- `src/pages`: route composition.
- `src/features`: domain-specific feature modules.

The UI uses Geist Sans globally, healthcare blue as the primary color, white backgrounds, and neutral gray surfaces. Motion libraries and CSS animations are intentionally excluded.
