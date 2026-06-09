/*
 * App.tsx - Root application component.
 *
 * Sets up the browser router and defines all top-level routes.
 * The layout is a fixed sidebar on the left with the active page
 * content scrolling in the main area on the right.
 *
 * Route map:
 *   /               -> DashboardPage  (stats cards)
 *   /patients       -> PatientsPage   (list, search, add, detail)
 *   /appointments   -> PlaceholderPage (UI-4)
 *   /providers      -> PlaceholderPage (UI-6)
 */

import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Sidebar } from "./components/Sidebar";
import { DashboardPage } from "./pages/DashboardPage";
import { PatientsPage } from "./pages/PatientsPage";
import { PlaceholderPage } from "./pages/PlaceholderPage";

export default function App() {
  return (
    // BrowserRouter enables client-side routing. All navigation happens
    // in the browser without full page reloads.
    <BrowserRouter>
      {/*
       * Full-screen flex container: sidebar on the left, content on the right.
       * h-screen locks the height to the viewport so the sidebar is always
       * visible without scrolling. overflow-hidden prevents the container
       * itself from scrolling - only the main area scrolls.
       */}
      <div className="flex h-screen overflow-hidden bg-background">
        <Sidebar />

        {/*
         * Main content area: flex-1 takes all remaining horizontal space.
         * overflow-y-auto allows long pages to scroll independently of the sidebar.
         * p-8 gives breathing room around the page content.
         */}
        <main className="flex-1 overflow-y-auto p-8">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/patients" element={<PatientsPage />} />
            <Route
              path="/appointments"
              element={
                <PlaceholderPage
                  title="Appointments"
                  plannedSession="UI-4"
                />
              }
            />
            <Route
              path="/providers"
              element={
                <PlaceholderPage
                  title="Providers"
                  plannedSession="UI-6"
                />
              }
            />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
