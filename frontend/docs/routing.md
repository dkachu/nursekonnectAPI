# Routing

Public routes:

- `/`
- `/login`
- `/register/patient`
- `/register/nurse`
- `/verify`
- `/offline`
- `/500`

Protected routes:

- `/dashboard`
- `/nurses`
- `/requests`
- `/tracking`
- `/visits`
- `/ratings`
- `/notifications`
- `/profile`

`ProtectedRoute` handles authentication. `RoleBasedRoute` actively restricts `/nurses` to `PATIENT` and `ADMIN` users.

Routes are lazy-loaded with React `Suspense` so route code is split into separate production chunks.
