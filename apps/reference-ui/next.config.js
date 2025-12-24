/** @type {import('next').NextConfig} */
const nextConfig = {
  // No output: 'export' for web service

  // Image optimization settings
  images: {
    domains: ['localhost'],
    unoptimized: false,
  },

  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
        ],
      },
    ]
  },

  async rewrites() {
    return [
      // API rewrites are handled by environment variables in this app, 
      // but we keep the structure for future flexibility.
    ]
  },
}

module.exports = nextConfig
