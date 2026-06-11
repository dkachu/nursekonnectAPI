export interface MonitoringEvent {
  message: string;
  context?: Record<string, string | number | boolean | null>;
}

export class MonitoringService {
  captureRuntimeError(error: Error, context?: MonitoringEvent["context"]): void {
    this.capture({ message: error.message, context });
  }

  captureApiError(message: string, context?: MonitoringEvent["context"]): void {
    this.capture({ message, context });
  }

  private capture(event: MonitoringEvent): void {
    // Intentionally no-op until a production monitoring vendor is configured.
    // Do not log healthcare data or tokens to the browser console.
    void event;
  }
}

export const monitoringService = new MonitoringService();
