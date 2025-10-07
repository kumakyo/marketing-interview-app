/** @type {import('next').NextConfig} */
const nextConfig = {
  // 外部デバイスからのアクセスを許可
  experimental: {
    allowedDevOrigins: ['*']
  },
  // 開発サーバーの設定
  devIndicators: {
    buildActivity: false,
  },
  // 画像の最適化設定
  images: {
    domains: ['api.dicebear.com'],
  },
  // APIルートの設定
  async rewrites() {
    return [
      // 必要に応じてAPIリライトルールを追加
    ];
  },
}

module.exports = nextConfig