/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Disable Turbopack to avoid HMR panics in dev mode (Next.js 16 issue)
  devIndicators: false,
};

module.exports = nextConfig;
