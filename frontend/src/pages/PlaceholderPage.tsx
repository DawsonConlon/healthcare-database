/*
 * pages/PlaceholderPage.tsx - Generic placeholder for unbuilt sections.
 *
 * Appointments and Providers appear in the sidebar but are not built yet.
 * This component is shown for those routes so the nav links work without
 * throwing a 404. Each section will replace it in a future session.
 */

interface PlaceholderPageProps {
  title: string;
  plannedSession: string;
}

export function PlaceholderPage({ title, plannedSession }: PlaceholderPageProps) {
  return (
    <div>
      <h1 className="text-2xl font-semibold text-foreground mb-1">{title}</h1>
      <p className="text-sm text-muted-foreground">
        This section is planned for {plannedSession}.
      </p>
    </div>
  );
}
