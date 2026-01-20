/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Note: eslint config removed - not supported in Next.js 16
  // ESLint is skipped by default in production builds
  typescript: {
    // Allow builds to complete even with TypeScript errors
    ignoreBuildErrors: true,
  },
  turbopack: {}, // Add an empty turbopack config to silence the error
};

module.exports = nextConfig;
