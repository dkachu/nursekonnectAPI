import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { BrowserRouter } from "react-router-dom";
import { ErrorBoundary } from "@/components/states/ErrorBoundary";
import { AuthStoreProvider } from "@/stores/auth-store";
import { NotificationStoreProvider } from "@/stores/notification-store";
import { UIStoreProvider } from "@/stores/ui-store";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
});

export function AppProviders({ children }: { children: ReactNode }): ReactNode {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <UIStoreProvider>
          <NotificationStoreProvider>
            <AuthStoreProvider>
              <BrowserRouter>{children}</BrowserRouter>
            </AuthStoreProvider>
          </NotificationStoreProvider>
        </UIStoreProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
