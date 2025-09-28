import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css"; // This imports Tailwind's styles

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "LogiMAS Tracking",
  description: "Logistics Multi-Agent System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-50`}>
        <main>{children}</main>
      </body>
    </html>
  );
}