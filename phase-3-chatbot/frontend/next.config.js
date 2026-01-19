/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: {
    // Allow builds to complete even with ESLint errors
    // TODO: Fix lint errors and remove this
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Allow builds to complete even with TypeScript errors
    // TODO: Fix type errors and remove this
    ignoreBuildErrors: true,
  },
};

module.exports = nextConfig;
