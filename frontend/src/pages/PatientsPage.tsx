/*
 * pages/PatientsPage.tsx - Searchable patient list with add and detail views.
 *
 * This page does three things:
 *   1. Lists all active patients from GET /patients, with live search
 *   2. Lets staff add a new patient via a dialog form (POST /patients)
 *   3. Shows a detail panel on the right when a table row is clicked
 *
 * The detail panel is a basic placeholder - the full edit form is built in UI-3.
 * The search is debounced 300ms so we do not fire a request on every keystroke.
 */

import { useCallback, useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  type CreatePatientPayload,
  type Patient,
  createPatient,
  listPatients,
} from "@/api/patients";

// ---------------------------------------------------------------------------
// Detail panel - shown on the right when a row is selected
// ---------------------------------------------------------------------------

function PatientDetailPanel({
  patient,
  onClose,
}: {
  patient: Patient;
  onClose: () => void;
}) {
  return (
    // Slide-in panel pinned to the right side of the content area.
    // In UI-3 this will expand into a full edit form.
    <div className="w-80 shrink-0 rounded-lg border border-border bg-card p-5">
      {/* Header row with close button */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-foreground">Patient Detail</h2>
        <button
          onClick={onClose}
          className="text-muted-foreground hover:text-foreground text-lg leading-none"
          aria-label="Close detail panel"
        >
          x
        </button>
      </div>

      {/* Patient summary fields */}
      <div className="space-y-3 text-sm">
        <DetailRow label="Name" value={`${patient.first_name} ${patient.last_name}`} />
        <DetailRow label="Date of birth" value={patient.date_of_birth} />
        <DetailRow label="Province" value={patient.province ?? "Not recorded"} />
        <DetailRow
          label="Consent"
          value={patient.consent_given ? "Given" : "Not given"}
        />

        {/* patient_id is surfaced here so devs can copy it for testing */}
        <div className="pt-3 border-t border-border">
          <p className="text-xs text-muted-foreground mb-1">Patient ID (UUID)</p>
          <p className="font-mono text-xs text-muted-foreground break-all">
            {patient.patient_id}
          </p>
        </div>
      </div>

      {/* Placeholder button - will navigate to the full detail page in UI-3 */}
      <div className="mt-5">
        <Button variant="outline" size="sm" className="w-full" disabled>
          Full record (UI-3)
        </Button>
      </div>
    </div>
  );
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-foreground">{value}</p>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Add Patient dialog
// ---------------------------------------------------------------------------

// Empty form state - reset to this when the dialog closes
const EMPTY_FORM: CreatePatientPayload = {
  first_name: "",
  last_name: "",
  date_of_birth: "",
  consent_given: false,
};

function AddPatientDialog({
  open,
  onClose,
  onCreated,
}: {
  open: boolean;
  onClose: () => void;
  onCreated: (patient: Patient) => void;
}) {
  const [form, setForm] = useState<CreatePatientPayload>(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset form state every time the dialog opens
  useEffect(() => {
    if (open) {
      setForm(EMPTY_FORM);
      setError(null);
    }
  }, [open]);

  // Generic change handler - works for text inputs and the checkbox
  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      // Checkbox values come from "checked", text inputs from "value"
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);

    try {
      const created = await createPatient(form);
      onCreated(created); // tell the parent to add this row to the table
      onClose();
    } catch {
      // The API returns 422 with detail array on validation failures.
      // For now we show a generic message - richer handling can come in UI-3.
      setError("Failed to save patient. Check all fields and try again.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Add Patient</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 py-2">
          {/* Error banner */}
          {error && (
            <p className="text-sm text-destructive border border-destructive/40 bg-destructive/10 rounded px-3 py-2">
              {error}
            </p>
          )}

          {/* First name */}
          <div className="space-y-1">
            <label className="text-sm font-medium text-foreground" htmlFor="first_name">
              First name
            </label>
            <Input
              id="first_name"
              name="first_name"
              value={form.first_name}
              onChange={handleChange}
              required
              placeholder="Jane"
            />
          </div>

          {/* Last name */}
          <div className="space-y-1">
            <label className="text-sm font-medium text-foreground" htmlFor="last_name">
              Last name
            </label>
            <Input
              id="last_name"
              name="last_name"
              value={form.last_name}
              onChange={handleChange}
              required
              placeholder="Smith"
            />
          </div>

          {/* Date of birth - browser native date picker */}
          <div className="space-y-1">
            <label className="text-sm font-medium text-foreground" htmlFor="date_of_birth">
              Date of birth
            </label>
            <Input
              id="date_of_birth"
              name="date_of_birth"
              type="date"
              value={form.date_of_birth}
              onChange={handleChange}
              required
            />
          </div>

          {/* Consent checkbox - PIPEDA requires explicit opt-in */}
          <div className="flex items-center gap-2">
            <input
              id="consent_given"
              name="consent_given"
              type="checkbox"
              checked={form.consent_given}
              onChange={handleChange}
              className="h-4 w-4 rounded border-border accent-primary"
            />
            <label className="text-sm text-foreground" htmlFor="consent_given">
              Patient has given consent (PIPEDA)
            </label>
          </div>

          <DialogFooter className="pt-2">
            <Button type="button" variant="outline" onClick={onClose} disabled={saving}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? "Saving..." : "Add Patient"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// ---------------------------------------------------------------------------
// Main page component
// ---------------------------------------------------------------------------

export function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<Patient | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  // Ref to store the debounce timer so we can clear it between keystrokes
  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Wrap the fetch in useCallback so the debounce always calls a stable reference
  const fetchPatients = useCallback(async (query: string) => {
    setLoading(true);
    setError(null);
    try {
      // Pass the search string only when it is non-empty - the API skips the
      // ILIKE filter when no ?search= param is present
      const data = await listPatients(query.trim() || undefined);
      setPatients(data);
    } catch {
      setError("Could not load patients. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch all patients on first render
  useEffect(() => {
    fetchPatients("");
  }, [fetchPatients]);

  // Re-fetch whenever the search input changes, debounced 300ms.
  // Clearing the timer on every keystroke means we only fire after the user
  // stops typing for 300ms, not on every individual character.
  function handleSearchChange(e: React.ChangeEvent<HTMLInputElement>) {
    const value = e.target.value;
    setSearch(value);

    if (debounceTimer.current) clearTimeout(debounceTimer.current);
    debounceTimer.current = setTimeout(() => {
      fetchPatients(value);
    }, 300);
  }

  // When a new patient is created, prepend it to the list and select it
  // to show the detail panel without a full re-fetch
  function handlePatientCreated(patient: Patient) {
    setPatients((prev) => [patient, ...prev]);
    setSelected(patient);
  }

  return (
    <div className="flex gap-6 h-full">
      {/* Left column: list + controls */}
      <div className="flex-1 min-w-0">
        {/* Page header */}
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-semibold text-foreground">Patients</h1>
            <p className="text-sm text-muted-foreground mt-0.5">
              {loading ? "Loading..." : `${patients.length} active patient${patients.length !== 1 ? "s" : ""}`}
            </p>
          </div>
          <Button onClick={() => setDialogOpen(true)}>Add Patient</Button>
        </div>

        {/* Search input */}
        <Input
          type="search"
          placeholder="Search by last name..."
          value={search}
          onChange={handleSearchChange}
          className="mb-4 max-w-xs"
        />

        {/* Error banner */}
        {error && (
          <div className="mb-4 rounded-md border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
            {error}
          </div>
        )}

        {/* Patient table */}
        <div className="rounded-lg border border-border overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Date of birth</TableHead>
                <TableHead>Province</TableHead>
                <TableHead>Consent</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {/* Empty state: no results (either no patients or search returned nothing) */}
              {!loading && patients.length === 0 && (
                <TableRow>
                  <TableCell
                    colSpan={4}
                    className="text-center text-muted-foreground py-10"
                  >
                    {search
                      ? `No patients found matching "${search}"`
                      : "No patients yet. Click Add Patient to create the first one."}
                  </TableCell>
                </TableRow>
              )}

              {/* One row per patient */}
              {patients.map((patient) => (
                <TableRow
                  key={patient.patient_id}
                  // Highlight the selected row and make the row clickable
                  onClick={() =>
                    setSelected((prev) =>
                      prev?.patient_id === patient.patient_id ? null : patient
                    )
                  }
                  className={[
                    "cursor-pointer",
                    selected?.patient_id === patient.patient_id
                      ? "bg-muted"
                      : "",
                  ].join(" ")}
                >
                  <TableCell className="font-medium">
                    {patient.last_name}, {patient.first_name}
                  </TableCell>
                  <TableCell>{patient.date_of_birth}</TableCell>
                  <TableCell>{patient.province ?? "-"}</TableCell>
                  {/* Consent badge: green for given, amber for not given */}
                  <TableCell>
                    <span
                      className={[
                        "inline-block px-2 py-0.5 rounded text-xs font-medium",
                        patient.consent_given
                          ? "bg-green-900/40 text-green-400"
                          : "bg-amber-900/40 text-amber-400",
                      ].join(" ")}
                    >
                      {patient.consent_given ? "Given" : "Not given"}
                    </span>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* Right column: detail panel - only visible when a row is selected */}
      {selected && (
        <PatientDetailPanel
          patient={selected}
          onClose={() => setSelected(null)}
        />
      )}

      {/* Add Patient dialog */}
      <AddPatientDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onCreated={handlePatientCreated}
      />
    </div>
  );
}
