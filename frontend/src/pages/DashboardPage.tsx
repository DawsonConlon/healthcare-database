/*
 * pages/DashboardPage.tsx - Home screen showing summary statistics.
 *
 * Calls GET /stats on mount and displays three numbers:
 *   - Total active patients
 *   - Total active providers
 *   - Appointments scheduled for today
 *
 * This page is intentionally simple - the stats endpoint already exists
 * (built in UI-1) and needs no backend work for this session.
 */

import { useEffect, useState } from "react";
import axios from "axios";

// Shape of the response from GET /stats (defined in backend/main.py)
interface Stats {
  total_patients: number;
  total_providers: number;
  appointments_today: number;
}

// A single stat card - reused for all three numbers
function StatCard({
  label,
  value,
}: {
  label: string;
  value: number | null;
}) {
  return (
    <div className="rounded-lg border border-border bg-card p-5">
      <p className="text-sm text-muted-foreground">{label}</p>
      {/* Show a dash while loading, then the real number */}
      <p className="mt-1 text-3xl font-semibold text-foreground">
        {value === null ? "-" : value}
      </p>
    </div>
  );
}

export function DashboardPage() {
  // null = still loading; Stats object = loaded
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch stats once when this component first mounts.
    // No dependency array values means this runs exactly once on mount.
    axios
      .get<Stats>("http://localhost:8000/stats")
      .then((res) => setStats(res.data))
      .catch(() => setError("Could not reach the API. Is the backend running?"));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-semibold text-foreground mb-1">Dashboard</h1>
      <p className="text-sm text-muted-foreground mb-6">
        Live counts from the database
      </p>

      {/* Error banner - only shown if the API is unreachable */}
      {error && (
        <div className="mb-6 rounded-md border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {/* Three stat cards in a row */}
      <div className="grid grid-cols-3 gap-4 max-w-2xl">
        <StatCard
          label="Total Patients"
          value={stats ? stats.total_patients : null}
        />
        <StatCard
          label="Total Providers"
          value={stats ? stats.total_providers : null}
        />
        <StatCard
          label="Appointments Today"
          value={stats ? stats.appointments_today : null}
        />
      </div>
    </div>
  );
}
