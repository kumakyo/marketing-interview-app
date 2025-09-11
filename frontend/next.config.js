/** @type {import('next').NextConfig} */
const nextConfig = {
  // 開発モードでは通常のNext.jsサーバーとして動作
  ...(process.env.NODE_ENV === 'production' ? {
    output: 'export',
    trailingSlash: true,
    distDir: 'out',
    assetPrefix: './',
  } : {}),
  
  images: {
    unoptimized: true,
  },
  
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  
  // ESLintエラーを一時的に無視（開発中）
  eslint: {
    ignoreDuringBuilds: true,
  },
  
  // TypeScriptエラーを一時的に無視（開発中）
  typescript: {
    ignoreBuildErrors: true,
  },
};

module.exports = nextConfig;
