/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Proxy /api/* → backend service (server-side only).
  // Browser sends relative URLs → Next.js forwards to INTERNAL_API_URL.
  // NEXT_PUBLIC_API_URL stays empty in Docker so browser uses relative paths.
  async rewrites() {
    const backendUrl = process.env.INTERNAL_API_URL || 'http://localhost:8000'
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ]
  },
}

export default nextConfig
