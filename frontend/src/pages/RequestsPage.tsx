import type { ReactNode } from "react";
import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { EmptyState } from "@/components/states/EmptyState";
import { ErrorState } from "@/components/states/ErrorState";
import { LoadingState } from "@/components/states/LoadingState";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RequestStatusCard } from "@/features/requests/components/RequestStatusCard";
import { useGeolocation } from "@/hooks/useGeolocation";
import { useCreateRequest, useRequests } from "@/hooks/useRequests";
import { getUserErrorMessage } from "@/utils/errors";

const requestSchema = z.object({
  service_type: z.string().min(1, "Select a service type."),
  priority: z.enum(["NORMAL", "URGENT", "CRITICAL"]),
  description: z.string().min(10, "Describe the care need in at least 10 characters."),
});

type RequestFormValues = z.infer<typeof requestSchema>;

export function RequestsPage(): ReactNode {
  const requests = useRequests();
  const { data = [], isLoading } = requests;
  const createRequest = useCreateRequest();
  const geolocation = useGeolocation();
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const {
    formState: { errors, isSubmitting },
    handleSubmit,
    register,
  } = useForm<RequestFormValues>({
    resolver: zodResolver(requestSchema),
    defaultValues: { priority: "NORMAL", service_type: "GENERAL_NURSING" },
  });

  async function onSubmit(values: RequestFormValues): Promise<void> {
    setSuccess(null);
    setError(null);
    try {
      const location = await geolocation.requestLocation();
      await createRequest.mutateAsync({ ...values, location });
      setSuccess("Care request created successfully.");
    } catch (requestError) {
      setError(getUserErrorMessage(requestError));
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Care Requests"
        description="Create, review, and manage home-based care requests."
      />
      <Card>
        <CardHeader>
          <CardTitle>Create Request</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            className="grid gap-4 md:grid-cols-3"
            onSubmit={(event) => void handleSubmit(onSubmit)(event)}
          >
            <div className="space-y-2">
              <Label htmlFor="service_type">Service type</Label>
              <select
                id="service_type"
                className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
                {...register("service_type")}
              >
                <option value="GENERAL_NURSING">General Nursing</option>
                <option value="WOUND_CARE">Wound Care</option>
                <option value="ELDERLY_CARE">Elderly Care</option>
                <option value="PALLIATIVE_CARE">Palliative Care</option>
                <option value="POST_SURGERY_CARE">Post Surgery Care</option>
                <option value="MATERNITY_CARE">Maternity Care</option>
                <option value="CHRONIC_DISEASE_SUPPORT">Chronic Disease Support</option>
              </select>
              {errors.service_type ? (
                <p className="text-sm text-destructive">{errors.service_type.message}</p>
              ) : null}
            </div>
            <div className="space-y-2">
              <Label htmlFor="priority">Priority</Label>
              <select
                id="priority"
                className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
                {...register("priority")}
              >
                <option value="NORMAL">Normal</option>
                <option value="URGENT">Urgent</option>
                <option value="CRITICAL">Critical</option>
              </select>
              {errors.priority ? (
                <p className="text-sm text-destructive">{errors.priority.message}</p>
              ) : null}
            </div>
            <div className="space-y-2 md:col-span-3">
              <Label htmlFor="description">Description</Label>
              <Input id="description" {...register("description")} />
              {errors.description ? (
                <p className="text-sm text-destructive">{errors.description.message}</p>
              ) : null}
            </div>
            {success ? <p className="text-sm text-emerald-700 md:col-span-3">{success}</p> : null}
            {error ? <p className="text-sm text-destructive md:col-span-3">{error}</p> : null}
            {geolocation.error ? (
              <p className="text-sm text-destructive md:col-span-3">{geolocation.error}</p>
            ) : null}
            <Button
              className="md:col-span-3"
              type="submit"
              disabled={isSubmitting || createRequest.isPending || geolocation.loading}
            >
              {createRequest.isPending || geolocation.loading
                ? "Creating Request"
                : "Use GPS and Create Request"}
            </Button>
          </form>
        </CardContent>
      </Card>
      {isLoading ? <LoadingState /> : null}
      {requests.error ? (
        <ErrorState
          message="Requests could not be loaded."
          onRetry={() => void requests.refetch()}
        />
      ) : null}
      {data.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {data.map((request) => (
            <RequestStatusCard key={request.id} request={request} />
          ))}
        </div>
      ) : null}
      {!isLoading && !requests.error && data.length === 0 ? (
        <EmptyState
          title="No Requests"
          message="Care requests will appear here once they are created or assigned."
        />
      ) : null}
    </div>
  );
}
