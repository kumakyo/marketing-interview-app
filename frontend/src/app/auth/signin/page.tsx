'use client';

import { signIn } from 'next-auth/react';
import { useState } from 'react';

export default function SignIn() {
  const [isLoading, setIsLoading] = useState(false);

  const handleGoogleSignIn = async () => {
    setIsLoading(true);
    try {
      await signIn('google', { callbackUrl: '/' });
    } catch (error) {
      console.error('ログインエラー:', error);
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-blue-50 to-purple-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* ロゴ・タイトル */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              tames interview
            </h1>
            <p className="text-gray-600">
              AIを活用したマーケティングインタビューシステム
            </p>
          </div>

          {/* 説明 */}
          <div className="bg-blue-50 rounded-lg p-4 mb-6">
            <p className="text-sm text-blue-900">
              📝 このアプリケーションを使用するには、Googleアカウントでログインしてください。
            </p>
            <p className="text-sm text-blue-900 mt-2">
              ✅ ログインすると、過去のインタビュー結果を保存・確認できます。
            </p>
          </div>

          {/* Googleログインボタン */}
          <button
            onClick={handleGoogleSignIn}
            disabled={isLoading}
            className="w-full bg-white border-2 border-gray-300 hover:border-gray-400 text-gray-700 font-semibold py-4 px-6 rounded-lg flex items-center justify-center space-x-3 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm hover:shadow-md"
          >
            {isLoading ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-900"></div>
                <span>ログイン中...</span>
              </div>
            ) : (
              <>
                <svg className="w-6 h-6" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                  />
                  <path fill="none" d="M1 1h22v22H1z" />
                </svg>
                <span>Googleでログイン</span>
              </>
            )}
          </button>

          {/* プライバシー注記 */}
          <div className="mt-6 text-center">
            <p className="text-xs text-gray-500">
              ログインすることで、
              <a href="#" className="text-blue-600 hover:text-blue-800">利用規約</a>
              および
              <a href="#" className="text-blue-600 hover:text-blue-800">プライバシーポリシー</a>
              に同意したものとみなされます。
            </p>
          </div>
        </div>

        {/* フッター情報 */}
        <div className="mt-8 text-center text-sm text-gray-600">
          <p>🔒 あなたのデータは安全に保護されています</p>
          <p className="mt-2">© 2025 tames interview. All rights reserved.</p>
        </div>
      </div>
    </div>
  );
}

