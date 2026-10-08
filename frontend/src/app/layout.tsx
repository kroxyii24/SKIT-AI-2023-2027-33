import "./globals.css"

export const metadata = {
  title: "JanSwasthya AI",
  description: "AI-powered public health awareness and healthcare access platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}