import { Component, type ErrorInfo, type ReactNode } from "react";
import { monitoringService } from "@/services/monitoring.service";
import { ErrorState } from "@/components/states/ErrorState";

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false };

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    monitoringService.captureRuntimeError(error, {
      componentStack: info.componentStack ?? null,
    });
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <main className="mx-auto max-w-3xl px-4 py-16">
          <ErrorState
            title="Application Error"
            message="NurseKonnect could not render this screen. Refresh the page or return to a safe route."
            onRetry={() => this.setState({ hasError: false })}
          />
        </main>
      );
    }

    return this.props.children;
  }
}
