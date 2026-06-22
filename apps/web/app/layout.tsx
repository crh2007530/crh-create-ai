import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "crh create AI",
  description: "Engineering visual problem solving platform"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
