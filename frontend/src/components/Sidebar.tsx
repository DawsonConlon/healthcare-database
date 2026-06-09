/*
 * components/Sidebar.tsx - Application navigation sidebar.
 *
 * Fixed-width, always-visible sidebar with links to all main sections.
 * Active link is highlighted using react-router-dom's NavLink, which
 * automatically applies the active class when the current URL matches.
 *
 * Nav items with pages not yet built (Appointments, Providers) still appear
 * as links - they will show placeholder pages until their sessions are done.
 */

import { NavLink } from "react-router-dom";

// Each sidebar item needs a route path, a display label, and a short
// description used as the aria-label for accessibility.
const NAV_ITEMS = [
  { to: "/", label: "Dashboard", exact: true },
  { to: "/patients", label: "Patients", exact: false },
  { to: "/appointments", label: "Appointments", exact: false },
  { to: "/providers", label: "Providers", exact: false },
];

export function Sidebar() {
  return (
    <aside
      // w-56 = 224px fixed width. shrink-0 prevents the sidebar from
      // squashing when the main content area needs more space.
      className="w-56 shrink-0 bg-card border-r border-border flex flex-col h-screen"
    >
      {/* App title / logo area */}
      <div className="px-5 py-4 border-b border-border">
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-widest">
          Clinic DB
        </p>
        <p className="text-sm text-muted-foreground mt-0.5">Patient Management</p>
      </div>

      {/* Navigation links */}
      <nav className="flex-1 px-2 py-3 space-y-0.5">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            // NavLink passes an { isActive } object to the className function.
            // We use it to swap the highlighted style when the route matches.
            // "end" on "/" prevents Dashboard from staying active on all routes.
            end={item.exact}
            className={({ isActive }) =>
              [
                "block px-3 py-2 rounded-md text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground" // highlighted: white-on-dark
                  : "text-muted-foreground hover:bg-muted hover:text-foreground",
              ].join(" ")
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Footer: environment label so it is obvious this is local dev */}
      <div className="px-5 py-3 border-t border-border">
        <p className="text-xs text-muted-foreground">Local dev - no real PHI</p>
      </div>
    </aside>
  );
}
