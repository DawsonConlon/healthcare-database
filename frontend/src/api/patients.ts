/*
 * api/patients.ts - HTTP client functions for the /patients API resource.
 *
 * All functions talk to the FastAPI backend running at localhost:8000.
 * Axios handles JSON serialisation, response parsing, and throws on non-2xx
 * status codes so callers can catch errors with try/catch.
 *
 * Types defined here mirror the Pydantic models in backend/routers/patients.py
 * so both sides agree on the shape of data crossing the wire.
 */

import axios from "axios";

// Base URL for the FastAPI server. In local dev this is always localhost:8000.
const API_BASE = "http://localhost:8000";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/**
 * A single patient as returned by GET /patients and POST /patients.
 * This is the "summary" shape - not every column, just what the list needs.
 */
export interface Patient {
  patient_id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string; // "YYYY-MM-DD" string from the API
  province: string | null;
  consent_given: boolean;
}

/**
 * The body sent to POST /patients when creating a new patient.
 * Only required fields are included here - the form only collects these.
 */
export interface CreatePatientPayload {
  first_name: string;
  last_name: string;
  date_of_birth: string; // "YYYY-MM-DD" string
  consent_given: boolean;
}

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/**
 * Fetch the list of active patients.
 *
 * @param search - Optional last-name substring filter. When provided, the
 *                 backend runs an ILIKE query and returns only matching rows.
 *                 When omitted, all active patients are returned.
 */
export async function listPatients(search?: string): Promise<Patient[]> {
  // Build query params. axios skips undefined values automatically,
  // so passing { params: { search: undefined } } sends no ?search= at all.
  const response = await axios.get<Patient[]>(`${API_BASE}/patients/`, {
    params: { search },
  });
  return response.data;
}

/**
 * Create a new patient record.
 *
 * @param payload - The required fields for a new patient.
 * @returns       The newly created patient including their generated patient_id.
 */
export async function createPatient(
  payload: CreatePatientPayload
): Promise<Patient> {
  const response = await axios.post<Patient>(`${API_BASE}/patients/`, payload);
  return response.data;
}
