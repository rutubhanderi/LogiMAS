'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { clearAuthTokens, getUser } from '@/lib/auth';
import { useState, useEffect } from 'react';

interface MenuItem {
  name: string;
  href: string;
  icon: React.ReactNode;
}

interface SidebarProps {
  menuItems: MenuItem[];
  role: 'admin' | 'customer' | 'delivery_guy';
}

export default function Sidebar({ menuItems, role }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const userData = getUser();
    setUser(userData);
  }, []);

  const handleLogout = () => {
    clearAuthTokens();
    // Use replace to prevent going back to a protected page
    router.replace('/signin');
  };

  const roleLabels = {
    admin: 'Admin',
    customer: 'Customer',
    delivery_guy: 'Delivery Person',
  };

  // --- MODIFIED LOGIC: Map the role to the correct file path ---
  // This handles the inconsistency between the 'delivery_guy' role and the '/delivery' folder.
  const rolePath = role === 'delivery_guy' ? 'delivery' : role;

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <Link href="/">
          <h1 className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">LogiMAS</h1>
        </Link>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{roleLabels[role]}</p>
      </div>

      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {menuItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              {item.icon}
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-gray-200 dark:border-gray-700 space-y-2">
        {/* CORRECTED: The profile link now uses the corrected 'rolePath' */}
        <Link
          href={`/${rolePath}/profile`}
          className="flex items-center gap-3 px-4 py-3 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
          <div className="flex-1">
            <p className="font-medium">Profile</p>
            {user && <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user.email}</p>}
          </div>
        </Link>

        <button onClick={handleLogout} className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
          <span className="font-medium">Logout</span>
        </button>
      </div>
    </div>
  );
}