import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { App } from "@/app/App";
import { AppProviders } from "@/app/providers";

describe("NurseKonnect frontend", () => {
  it("renders branded home page", async () => {
    render(
      <AppProviders>
        <App />
      </AppProviders>,
    );

    expect(await screen.findByText("Register as Patient")).toBeInTheDocument();
    expect(screen.getAllByAltText("NurseKonnect").length).toBeGreaterThan(0);
  });
});
