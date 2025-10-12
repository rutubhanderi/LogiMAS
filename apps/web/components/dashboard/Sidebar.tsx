  'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '../../contexts/AuthContext';

interface NavLink {
  name: string;
  href: string;
  permission?: string;
  excludeRoles?: string[];
}

const navLinks: NavLink[] = [
  { name: 'Chat', href: '/dashboard/chat', permission: 'access_chat' },
  { name: 'Tracking', href: '/dashboard/tracking', permission: 'view_tracking' },
  { name: 'Knowledge Base', href: '/dashboard/knowledge', permission: 'access_knowledge_base' },
  { name: 'Analysis', href: '/dashboard/analysis', permission: 'perform_analysis' },
  { name: 'Report Incident', href: '/dashboard/report-incident', permission: 'report_incident' },
  { name: 'Place Order', href: '/dashboard/place-order', permission: 'place_order' },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { hasPermission, user, logout } = useAuth();

  // Filter nav links based on user permissions
  const visibleLinks = navLinks.filter((link) => {
    // If no permission is specified, show to everyone
    if (!link.permission) return true;
    
    // Check if user has the required permission
    return hasPermission(link.permission);
  });

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  return (
    // Dark sidebar with a subtle border on the right
    <div className="w-64 bg-[#0d1b2a] text-slate-300 h-screen flex flex-col p-4 border-r border-slate-700">
      <div className="text-3xl font-bold text-white mb-12 pl-3 pt-3">LogiMAS</div>
      
      <nav className="flex-grow">
        <ul className="space-y-3">
          {visibleLinks.map((link) => (
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
      
      {/* User info and logout button at the bottom */}
      <div className="flex-shrink-0 border-t border-slate-700 pt-4">
        {user && (
          <div className="text-sm text-slate-400 mb-3 pl-3">
            <div className="font-medium text-slate-300 capitalize">{user.role.replace('_', ' ')}</div>
            <div className="text-xs truncate" title={user.email}>{user.email}</div>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="w-full text-left p-3 rounded-lg transition-colors text-base font-medium hover:bg-red-600/20 hover:text-red-400"
        >
          Logout
        </button>
      </div>
    </div>
  );
}