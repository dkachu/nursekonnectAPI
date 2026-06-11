import { Link } from "react-router-dom";
import type { ReactNode } from "react";
import { Logo } from "@/components/brand/Logo";

const currentYear = new Date().getFullYear();

export function Footer(): ReactNode {
  return (
    <footer className="border-t border-border bg-background">
      <div className="mx-auto grid max-w-7xl gap-8 px-4 py-10 sm:px-6 md:grid-cols-3 lg:px-8">
        <div className="space-y-3">
          <Logo compact />
          <p className="max-w-sm text-sm leading-6 text-muted-foreground">
            Connecting Patients With Trusted Home-Based Nurses
          </p>
        </div>
        <div>
          <h2 className="text-sm font-semibold">Quick Links</h2>
          <div className="mt-3 grid gap-2 text-sm text-muted-foreground">
            <Link className="hover:text-foreground" to="/">
              Home
            </Link>
            <Link className="hover:text-foreground" to="/nurses">
              Find Nurses
            </Link>
            <Link className="hover:text-foreground" to="/dashboard">
              Dashboard
            </Link>
            <a className="hover:text-foreground" href="mailto:support@nursekonnect.co.ke">
              Support
            </a>
          </div>
        </div>
        <div>
          <h2 className="text-sm font-semibold">Contact Information</h2>
          <div className="mt-3 grid gap-2 text-sm text-muted-foreground">
            <span>support@nursekonnect.co.ke</span>
            <span>+254 700 000 000</span>
            <span>Kenya</span>
          </div>
        </div>
      </div>
      <div className="border-t border-border px-4 py-4 text-center text-sm text-muted-foreground">
        © NurseKonnect {currentYear}. All rights reserved.
      </div>
    </footer>
  );
}
