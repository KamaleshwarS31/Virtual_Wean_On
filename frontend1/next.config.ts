import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Silence workspace root warning (already ignored by default usually)

  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/api/:path*`,
      },
      {
        source: '/storage/:path*',
        destination: `${apiUrl}/storage/:path*`,
      },
    ];
  },
};

export default nextConfig;
