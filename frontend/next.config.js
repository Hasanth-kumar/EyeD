/** @type {import('next').NextConfig} */
const nextConfig = {
  // React strict mode for better development experience
  reactStrictMode: true,

  // Image optimization configuration
  images: {
    // Add domains for external images if needed
    domains: [],
    // Remote patterns for more flexible image sources
    remotePatterns: [],
  },

  // TypeScript configuration
  typescript: {
    // Set to false in production if you want to ignore TypeScript errors during build
    // Recommended to keep true and fix errors
    ignoreBuildErrors: false,
  },

  // ESLint configuration
  eslint: {
    // Set to false in production if you want to ignore ESLint errors during build
    // Recommended to keep true and fix errors
    ignoreDuringBuilds: false,
  },

  // Environment variables that should be available on the client
  // These must be prefixed with NEXT_PUBLIC_
  env: {
    // API base URL - defaults to localhost:8000 for development
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },

  // Webpack configuration (if needed for customizations)
  webpack: (config, { isServer }) => {
    // Ensure path aliases from tsconfig.json are resolved
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': require('path').resolve(__dirname, 'src'),
    };
    return config;
  },

  // Headers configuration for security and CORS
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: '*', // Configure this properly for production
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET, POST, PUT, DELETE, OPTIONS',
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'Content-Type, Authorization',
          },
        ],
      },
    ];
  },

  // Rewrites for API proxying (if needed)
  async rewrites() {
    return [
      // Example: Proxy API requests to backend
      // {
      //   source: '/api/:path*',
      //   destination: `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`,
      // },
    ];
  },
}

module.exports = nextConfig

