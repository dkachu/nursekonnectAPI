import { Link } from "react-router-dom";
import type { ReactNode } from "react";
import { ShieldCheck, Stethoscope, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";

export function HomePage(): ReactNode {
  const cards = [
    {
      title: "Verified nurses",
      description: "NCK-verified professionals for home-based care.",
      icon: ShieldCheck,
    },
    {
      title: "Nearby discovery",
      description: "Find eligible nurses using secure GPS-based matching.",
      icon: MapPin,
    },
    {
      title: "Care continuity",
      description: "Requests, visits, notes, ratings, and follow-ups in one place.",
      icon: Stethoscope,
    },
  ];

  return (
    <section className="mx-auto grid max-w-7xl gap-8 px-4 py-12 sm:px-6 lg:grid-cols-[1fr_420px] lg:px-8 lg:py-16">
      <div className="max-w-3xl">
        <p className="text-sm font-semibold text-primary">Healthcare at home</p>
        <h1 className="mt-4 text-4xl font-semibold tracking-normal text-foreground sm:text-5xl">
          NurseKonnect
        </h1>
        <p className="mt-5 text-lg leading-8 text-muted-foreground">
          A secure platform connecting patients with trusted home-based nurses across Kenya.
        </p>
        <div className="mt-8 flex flex-col gap-3 sm:flex-row">
          <Button asChild size="lg">
            <Link to="/register/patient">Register as Patient</Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link to="/register/nurse">Register as Nurse</Link>
          </Button>
        </div>
      </div>
      <div className="grid gap-4">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <Card key={card.title}>
              <CardHeader className="flex flex-row items-start gap-4 space-y-0">
                <div className="rounded-md border border-blue-200 bg-blue-50 p-2 text-primary">
                  <Icon className="h-5 w-5" aria-hidden="true" />
                </div>
                <div>
                  <CardTitle>{card.title}</CardTitle>
                  <p className="mt-1 text-sm leading-6 text-muted-foreground">{card.description}</p>
                </div>
              </CardHeader>
            </Card>
          );
        })}
      </div>
    </section>
  );
}
