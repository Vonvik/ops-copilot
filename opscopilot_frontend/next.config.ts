/** @type {import('next').NextConfig} */
const nextConfig = {
  // Si usas App Router no hace falta experimental aquí
  async rewrites() {
    return [
      // ✅ Proxy SOLO para tu FastAPI
      {
        source: '/api/v1/:path*',
        destination: 'http://127.0.0.1:8000/api/v1/:path*',
      },
      // ❌ NO PONGAS un catch-all '/api/:path*'
      // Deja libres las rutas de NextAuth en /api/auth/*
    ];
  },
};

module.exports = nextConfig;
