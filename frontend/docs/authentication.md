# Authentication

Authentication uses the backend JWT endpoints:

- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `POST /api/auth/logout/`
- `POST /api/auth/register/`
- `POST /api/auth/verify-otp/`
- `POST /api/auth/resend-otp/`

Tokens are held in memory and attached by the Axios interceptor. Refresh retries are centralized in `src/api/client.ts`. If refresh fails, the API client clears in-memory tokens and notifies the auth store so protected routes are no longer accessible. The client is configured with `withCredentials` to support HttpOnly secure-cookie deployments.

Registration logs the user in before redirecting to `/verify` because the backend OTP verification and resend endpoints require JWT authentication.
