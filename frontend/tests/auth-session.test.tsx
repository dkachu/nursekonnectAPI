import { act, render, renderHook, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ProtectedRoute } from "@/routes/ProtectedRoute";
import { RoleBasedRoute } from "@/routes/RoleBasedRoute";
import { AuthStoreProvider } from "@/stores/auth-store";
import { useAuthStore } from "@/stores/use-auth-store";
import type { AuthUser } from "@/types";

const patientUser: AuthUser = {
  id: 1,
  email: "patient@example.com",
  first_name: "Amina",
  last_name: "Otieno",
  role: "PATIENT",
  email_verified: true,
  phone_verified: true,
  profile: { id: 10, phone_number: "+254712345678" },
};

const authMocks = vi.hoisted(() => ({
  restoreSession: vi.fn<() => Promise<AuthUser>>(),
  login: vi.fn(),
  logout: vi.fn(),
  refreshSession: vi.fn(),
  getCurrentUser: vi.fn(),
}));

vi.mock("@/services/auth.service", () => ({
  authService: {
    restoreSession: authMocks.restoreSession,
    login: authMocks.login,
    logout: authMocks.logout,
    refreshSession: authMocks.refreshSession,
    getCurrentUser: authMocks.getCurrentUser,
  },
}));

function wrapper({ children }: { children: ReactNode }): ReactNode {
  return <AuthStoreProvider>{children}</AuthStoreProvider>;
}

describe("session restoration", () => {
  beforeEach(() => {
    authMocks.restoreSession.mockReset();
    authMocks.login.mockReset();
    authMocks.logout.mockReset();
    authMocks.refreshSession.mockReset();
    authMocks.getCurrentUser.mockReset();
  });

  it("hydrates the authenticated user from the session bootstrap flow", async () => {
    authMocks.restoreSession.mockResolvedValueOnce(patientUser);

    const { result } = renderHook(() => useAuthStore(), { wrapper });

    expect(result.current.isRestoringSession).toBe(true);
    await waitFor(() => expect(result.current.isRestoringSession).toBe(false));

    expect(result.current.currentUser).toEqual(patientUser);
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.role).toBe("PATIENT");
  });

  it("clears auth state when session restoration fails", async () => {
    authMocks.restoreSession.mockRejectedValueOnce(new Error("expired"));

    const { result } = renderHook(() => useAuthStore(), { wrapper });

    await waitFor(() => expect(result.current.isRestoringSession).toBe(false));

    expect(result.current.currentUser).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  it("shows loading before protected routes decide authentication", async () => {
    let resolveRestore!: (user: AuthUser) => void;
    const restoration = new Promise<AuthUser>((resolve) => {
      resolveRestore = resolve;
    });
    authMocks.restoreSession.mockReturnValueOnce(restoration);

    render(
      <AuthStoreProvider>
        <MemoryRouter initialEntries={["/secure"]}>
          <Routes>
            <Route element={<ProtectedRoute />}>
              <Route path="/secure" element={<p>Protected content</p>} />
            </Route>
            <Route path="/login" element={<p>Login page</p>} />
          </Routes>
        </MemoryRouter>
      </AuthStoreProvider>,
    );

    expect(screen.getByLabelText("Loading content")).toBeInTheDocument();
    await act(async () => {
      resolveRestore(patientUser);
      await restoration;
    });
    expect(await screen.findByText("Protected content")).toBeInTheDocument();
  });

  it("restores role-based route access after bootstrap", async () => {
    authMocks.restoreSession.mockResolvedValueOnce(patientUser);

    render(
      <AuthStoreProvider>
        <MemoryRouter initialEntries={["/patient-only"]}>
          <Routes>
            <Route element={<RoleBasedRoute roles={["PATIENT"]} />}>
              <Route path="/patient-only" element={<p>Patient workspace</p>} />
            </Route>
            <Route path="/forbidden" element={<p>Forbidden</p>} />
          </Routes>
        </MemoryRouter>
      </AuthStoreProvider>,
    );

    expect(await screen.findByText("Patient workspace")).toBeInTheDocument();
  });
});
