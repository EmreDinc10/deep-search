/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  env: {
    NEXT_PUBLIC_API_URL: 'https://deep-search-backend.onrender.com',
  },
}

module.exports = nextConfig
