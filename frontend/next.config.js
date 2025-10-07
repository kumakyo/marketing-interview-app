/** @type {import('next').NextConfig} */
const nextConfig = {
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
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization' },
        ],
      },
    ];
  },
}

module.exports = nextConfig