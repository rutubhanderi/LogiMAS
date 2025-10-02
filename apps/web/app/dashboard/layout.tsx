import { Sidebar } from "../../components/dashboard/Sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    // Set up the core flex layout: sidebar on the left, main content taking the rest of the space
    <div className="flex h-screen bg-slate-100">
      <Sidebar />
      <main className="flex-grow p-6 sm:p-8 md:p-10 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}