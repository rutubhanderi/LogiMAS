'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { isAuthenticated, getUser } from '@/lib/auth';
import Sidebar from './Sidebar';

interface DashboardLayoutProps {
  children: React.ReactNode;
  role: 'admin' | 'customer' | 'delivery_guy';
  menuItems: Array<{
    name: string;
    href: string;
    icon: React.ReactNode;
  }>;
}

export default function DashboardLayout({
  children,
  role,
  menuItems,
}: DashboardLayoutProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check authentication
    if (!isAuthenticated()) {
      router.push('/signin');
      return;
    }

    // Check role
    const user = getUser();
    if (user && user.role !== role) {
      // Redirect to correct dashboard
      router.push(`/${user.role}/dashboard`);
      return;
    }

    setLoading(false);
  }, [router, role]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0">
        <Sidebar menuItems={menuItems} role={role} />
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}
