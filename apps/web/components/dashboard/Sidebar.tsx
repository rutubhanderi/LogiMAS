"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

// The navigation links for the dashboard sidebar.
const navLinks = [
  { name: "Chat", href: "/dashboard/chat" },
  { name: "Tracking", href: "/dashboard/tracking" },
  { name: "Knowledge Base", href: "/dashboard/knowledge" },
  { name: "Analysis", href: "/dashboard/analysis" },
];

export function Sidebar() {
  // usePathname is a client-side hook to get the current URL path.
  // We need it to determine which link is "active".
  const pathname = usePathname();

  return (
    <div className="w-64 bg-slate-800 text-white h-screen flex flex-col p-4 shadow-2xl">
      <div className="text-2xl font-bold mb-10 pl-3">LogiMAS</div>

      <nav className="flex-grow">
        <ul className="space-y-2">
          {navLinks.map((link) => (
            <li key={link.name}>
              <Link
                href={link.href}
                className={`block w-full text-left p-3 rounded-md transition-colors ${
                  // This logic highlights the link if the current path matches the link's href.
                  pathname === link.href
                    ? "bg-blue-600 font-semibold"
                    : "hover:bg-slate-700"
                }`}
              >
                {link.name}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      {/* The Sign Out button remains commented out or removed since auth is disabled. */}
    </div>
  );
}
