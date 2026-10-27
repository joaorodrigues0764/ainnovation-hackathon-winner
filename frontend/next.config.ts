import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // só no Docker (NEXT_OUTPUT=standalone): no Windows o standalone pode precisar de symlinks
  output: process.env.NEXT_OUTPUT === "standalone" ? "standalone" : undefined,
  cacheComponents: true,
  partialPrefetching: true,
  // produção: o browser chama /api no próprio domínio e o Vercel passa ao Render, por isso não há CORS
  rewrites: async () => [
    {
      source: "/api/:path*",
      destination: `${(process.env.API_PROXY_TARGET ?? "https://caixa-explica-api.onrender.com").replace(/\/$/, "")}/:path*`,
    },
  ],
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
