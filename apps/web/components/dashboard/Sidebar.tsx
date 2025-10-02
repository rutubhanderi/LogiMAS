'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navLinks = [
  { name: 'Chat', href: '/dashboard/chat' },
  { name: 'Tracking', href: '/dashboard/tracking' },
  { name: 'Knowledge Base', href: '/dashboard/knowledge' },
  { name: 'Analysis', href: '/dashboard/analysis' },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    // Dark sidebar with a subtle border on the right
    <div className="w-64 bg-[#0d1b2a] text-slate-300 h-screen flex flex-col p-4 border-r border-slate-700">
      <div className="text-3xl font-bold text-white mb-12 pl-3 pt-3">LogiMAS</div>
      
      <nav className="flex-grow">
        <ul className="space-y-3">
          {navLinks.map((link) => (
            <li key={link.name}>
              <Link
                href={link.href}
                className={`block w-full text-left p-3 rounded-lg transition-colors text-base font-medium ${
                  pathname.startsWith(link.href)
                    ? "bg-blue-600 text-white shadow-md"
                    : "hover:bg-slate-700/50 hover:text-white"
                }`}
              >
                {link.name}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
      {/* Placeholder for a user profile or sign out button at the bottom */}
      <div className="flex-shrink-0 h-16"></div>
    </div>
  );
}