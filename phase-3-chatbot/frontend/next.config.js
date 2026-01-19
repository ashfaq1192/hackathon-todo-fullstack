/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  devIndicators: false,
  // Use Webpack instead of Turbopack for builds
  experimental: {
    turbo: false,
  },
};

module.exports = nextConfig;
