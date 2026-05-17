/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "pub-9e85fcdc5e564734ac6f665ff3f54bf0.r2.dev" }
    ]
  }
};

export default nextConfig;
