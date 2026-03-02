import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Cloud Run用の最適化設定
  output: 'standalone',
  
  // 画像最適化の設定
  images: {
    unoptimized: true,
  },
  
  // 環境変数の検証
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
};

export default nextConfig;
