import type { Metadata, Viewport } from "next";
import "./globals.css";
import { AppProviders } from "@/providers/app-providers";

export const metadata: Metadata = {
  title: {
    default: "RegIntel — Regulatory Intelligence",
    template: "%s · RegIntel",
  },
  description: "Citation-backed compliance intelligence for regulatory change",
  applicationName: "RegIntel",
};

export const viewport: Viewport = {
  themeColor: "#0c1222",
  colorScheme: "dark",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="font-sans antialiased">
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
