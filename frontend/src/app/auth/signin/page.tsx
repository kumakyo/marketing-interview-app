'use client';

import { Suspense } from 'react';
import { signIn } from 'next-auth/react';
import { useSearchParams } from 'next/navigation';

const QUANTITATIVE_URL =
  process.env.NEXT_PUBLIC_QUANTITATIVE_URL ||
  'https://tames-frontend-staging-128899916170.asia-northeast1.run.app';

function SidebarNav() {
  const navItems = [
    { label: 'ホーム', icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
      </svg>
    )},
    { label: 'ペルソナ設定', icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z" />
      </svg>
    )},
    { label: 'インタビュー', icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 0 1-.825-.242m9.345-8.334a2.126 2.126 0 0 0-.476-.095 48.64 48.64 0 0 0-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0 0 11.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155" />
      </svg>
    )},
    { label: '分析結果', icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" />
      </svg>
    )},
    { label: 'レポート', icon: (
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
      </svg>
    )},
  ];

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-56 flex-col border-r border-gray-200 bg-white">
      <div className="px-5 pt-5 pb-4">
        <h1 className="text-lg font-semibold text-gray-900">AI Interview</h1>
      </div>
      <nav className="flex-1 space-y-1 px-3">
        {navItems.map((item) => (
          <div
            key={item.label}
            className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-gray-400 cursor-default"
          >
            <span className="text-gray-300">{item.icon}</span>
            {item.label}
          </div>
        ))}
        <div className="pt-4 mt-4 border-t border-gray-200">
          <a
            href={QUANTITATIVE_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-gray-400 hover:bg-gray-50 hover:text-gray-600 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
            </svg>
            AI Survey
          </a>
        </div>
      </nav>

      <div className="border-t border-gray-200 px-4 py-3">
        <div className="space-y-1 text-xs">
          <div className="flex items-center justify-between">
            <span className="text-gray-400">バックエンド:</span>
            <span className="inline-block h-2 w-2 rounded-full bg-green-500" />
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-400">フロントエンド:</span>
            <span className="inline-block h-2 w-2 rounded-full bg-green-500" />
          </div>
        </div>
      </div>
    </aside>
  );
}

function SignInContent() {
  const searchParams = useSearchParams();
  const error = searchParams?.get('error');
  const callbackUrl = searchParams?.get('callbackUrl') || '/';

  const errorMessages: Record<string, string> = {
    OAuthSignin: 'Google認証の開始に失敗しました。',
    OAuthCallback: 'Google認証のコールバックに失敗しました。',
    OAuthCreateAccount: 'アカウントの作成に失敗しました。',
    Callback: '認証コールバックでエラーが発生しました。',
    OAuthAccountNotLinked: 'このメールアドレスは既に別のアカウントで使用されています。',
    SessionRequired: 'ログインが必要です。',
  };

  return (
    <div className="flex min-h-screen">
      <SidebarNav />

      <main className="ml-56 flex flex-1 items-center justify-center">
        <div className="w-full max-w-md rounded-xl border border-gray-200 bg-white p-8">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">ログイン</h2>
            <p className="mt-1 text-sm text-gray-500">
              AI Interview Platform にログイン
            </p>
          </div>

          {error && (
            <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {errorMessages[error] || `認証エラー: ${error}`}
            </div>
          )}

          {/* Email field (decorative, disabled) */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">メールアドレス</label>
            <input
              type="email"
              placeholder="your@email.com"
              disabled
              className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm text-gray-400 bg-gray-50"
            />
          </div>

          {/* Password field (decorative, disabled) */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-1">パスワード</label>
            <input
              type="password"
              placeholder="••••••••"
              disabled
              className="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm text-gray-400 bg-gray-50"
            />
          </div>

          {/* Login button (decorative, disabled) */}
          <button
            disabled
            className="w-full rounded-lg bg-blue-600 py-2.5 text-sm font-medium text-white opacity-50 cursor-not-allowed mb-4"
          >
            ログイン
          </button>

          <div className="flex items-center gap-3 my-4">
            <div className="h-px flex-1 bg-gray-200" />
            <span className="text-xs text-gray-400">または</span>
            <div className="h-px flex-1 bg-gray-200" />
          </div>

          <button
            onClick={() => signIn('google', { callbackUrl })}
            className="w-full flex items-center justify-center gap-3 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
            </svg>
            Google でログイン
          </button>

          <p className="mt-6 text-center text-sm text-gray-500">
            アカウントをお持ちでないですか？{' '}
            <span className="text-blue-600 hover:underline cursor-pointer font-medium">新規登録</span>
          </p>
        </div>
      </main>
    </div>
  );
}

export default function SignIn() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
        </div>
      }
    >
      <SignInContent />
    </Suspense>
  );
}
