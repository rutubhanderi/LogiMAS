import { AuthProvider } from "../contexts/AuthContext";
import "./globals.css";
import "leaflet/dist/leaflet.css";

export const metadata = {
  title: "LogiMAS Platform",
  description: "Logistics Multi-Agent System",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
