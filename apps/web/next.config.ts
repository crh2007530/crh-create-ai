import type { NextConfig } from "next";

const isGithubPages = process.env.GITHUB_PAGES === "true";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: isGithubPages ? "export" : undefined,
  basePath: isGithubPages ? "/crh-create-ai" : undefined,
  assetPrefix: isGithubPages ? "/crh-create-ai/" : undefined,
  images: {
    unoptimized: true
  }
};

const serverNextConfig: NextConfig = {
  ...nextConfig,
  async rewrites() {
    const apiUrl = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8000";
    return [
      {
        source: "/api/backend/:path*",
        destination: `${apiUrl}/:path*`
      }
    ];
  }
};

export default isGithubPages ? nextConfig : serverNextConfig;
