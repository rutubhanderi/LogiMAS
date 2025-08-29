"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from 'next/navigation';
import { LayoutDashboard, BrainCircuit, BarChart3, Settings } from 'lucide-react';
import { clsx } from 'clsx';

const navLinks = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Knowledge Base', href: '/knowledge-base', icon: BrainCircuit },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 flex-shrink-0 bg-sidebar-background text-sidebar-foreground p-6 flex flex-col">
      <div className="mb-10">
        <Link href="/dashboard">
          <Image src="/logimas-logo.png" alt="logiMAS Logo" width={120} height={40} />
        </Link>
      </div>

      <nav className="flex-grow">
        <ul className="space-y-3">
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <li key={link.name}>
                <Link
                  href={link.href}
                  className={clsx(
                    "flex items-center space-x-3 rounded-md p-3 text-sm font-medium transition-colors",
                    {
                      'bg-primary text-primary-foreground': isActive,
                      'text-gray-300 hover:bg-zinc-700 hover:text-white': !isActive,
                    }
                  )}
                >
                  <link.icon className="h-5 w-5" />
                  <span>{link.name}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="mt-auto">
        <div className="border-t border-zinc-700 my-4"></div>
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-full bg-gray-500"></div>
          <div className="flex-1">
            <p className="text-sm font-semibold">Rutu Bhanderi</p>
          </div>
          <Settings className="h-5 w-5 text-gray-400 cursor-pointer hover:text-white" />
        </div>
      </div>
    </aside>
  );
}