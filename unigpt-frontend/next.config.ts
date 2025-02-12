import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  output: "export", // Remove if using SSR
  trailingSlash: true, // Optional: Match Vercel routing
};

export default nextConfig;
