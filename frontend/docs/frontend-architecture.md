# Frontend Architecture

NurseKonnect follows a strict one-way frontend data flow:

```text
UI Layer
->
Hooks Layer
->
Services Layer
->
API Layer
->
Backend
```

## API Layer

The API layer lives in `src/api/`. It owns Axios, endpoint URLs, request/response typing, JWT attachment, refresh retry, and error normalization. Refresh failures clear in-memory tokens and notify the auth store.

Files:

- `auth.api.ts`
- `patient.api.ts`
- `nurse.api.ts`
- `request.api.ts`
- `tracking.api.ts`
- `visit.api.ts`
- `rating.api.ts`
- `notification.api.ts`
- `admin.api.ts`
- `client.ts`

## Service Layer

The service layer lives in `src/services/`. Services contain domain workflow decisions and call API modules. Services do not import React and do not render UI.

## Hooks Layer

Reusable hooks live in `src/hooks/`. TanStack Query hooks map backend endpoints to query and mutation operations. They own cache keys, invalidation, mutation state, and refetch behavior.

Endpoint hook coverage:

- Auth: `useRegister`, `useVerifyOtp`, `useResendOtp`
- Patients: `usePatientProfile`, `useUpdatePatientProfile`, `useEmergencyContacts`, `useCreateEmergencyContact`, `useUpdateEmergencyContact`, `useDeleteEmergencyContact`, `useDependents`, `useCreateDependent`, `useUpdateDependent`, `useDeleteDependent`, `useMedicalInformation`
- Nurses: `useNearbyNurses`, `useNurseProfile`, `useUpdateNurseProfile`, `useNckLicenseStatusUrl`, `useSpecializations`, `useProfileSpecializations`, `useReplaceProfileSpecializations`, `useCredentials`, `useUploadCredential`, `useAvailability`, `useCreateAvailability`, `useUpdateAvailability`, `useDeleteAvailability`, `useChangeAvailability`
- Requests: `useRequests`, `useRequest`, `useCreateRequest`, `useAcceptRequest`, `useStartJourney`, `useMarkArrived`, `useStartVisit`, `useCompleteRequest`, `useCancelRequest`
- Tracking: `useUpdateLocation`, `useSubmitTrackingLocation`
- Visits: `useVisitNotes`, `useVisitNote`, `useCreateVisitNote`, `useUpdateVisitNote`
- Ratings: `useRatings`, `useSubmitRating`
- Notifications: `useNotifications`, `useMarkNotificationRead`, `useMarkAllNotificationsRead`
- Admin: `useVerifyNurse`, `useReviewCredential`, `useRecalculateReputation`

## Stores

Global state uses React Context only.

- `auth-store.tsx`: current user, role, permissions, login, logout, refresh session.
- `notification-store.tsx`: notifications, unread count, mark read, mark all read.
- `ui-store.tsx`: sidebar state, light theme, loading state.

## Routing

Routes are lazy-loaded with React `Suspense` to split page code into production chunks. `ProtectedRoute` guards authenticated pages, and `RoleBasedRoute` restricts role-specific surfaces such as nearby nurse discovery.

## Feature Modules

Each feature under `src/features/` contains:

- `components/`
- `hooks/`
- `services/`
- `types/`

Feature modules re-export real app hooks, service classes, and domain types. Components are presentational only.

## Privacy

Protected healthcare data is fetched through role-aware routes and backend object permissions. Patient medical/profile calls are not made from nurse/admin profile screens. Sensitive medical information uses short-lived query caching and is never persisted to browser storage.
