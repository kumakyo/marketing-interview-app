/** @type {import('next').NextConfig} */
const nextConfig = {
  // --- ここから追加 ---
  output: 'standalone',
  // ビルド時の型エラーを無視
  typescript: {
    ignoreBuildErrors: true,
  },
  // ビルド時のESLintエラーを無視
  eslint: {
    ignoreDuringBuilds: true,
  },
  // --- ここまで追加 ---

  // 外部デバイスからのアクセスを許可
  experimental: {},
  
  // 画像の最適化設定
  images: {
    domains: ['api.dicebear.com'],
  },
  
  // 開発サーバーの設定
  async headers() {
    return [
      {
        // すべてのAPIルートに適用
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Credentials', value: 'true' },
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS, PATCH' },
          { key: 'Access-Control-Allow-Headers', value: 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version, Authorization' },
          { key: 'Access-Control-Max-Age', value: '86400' },
        ],
      },
      {
        // すべてのページに適用
        source: '/:path*',
        headers: [
          { key: 'X-DNS-Prefetch-Control', value: 'on' },
          { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
        ],
      },
    ];
  },
  
  // リライト設定（APIプロキシ）
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return [
      {
        source: '/backend-api/:path*',
        destination: `${apiUrl}/:path*`,
      },
    ];
  },
}

module.exports = nextConfig