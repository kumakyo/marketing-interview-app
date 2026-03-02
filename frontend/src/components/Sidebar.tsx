'use client';

import { useSession, signOut } from 'next-auth/react';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
  active?: boolean;
}

const QUANTITATIVE_URL =
  process.env.NEXT_PUBLIC_QUANTITATIVE_URL ||
  'https://tames-frontend-staging-128899916170.asia-northeast1.run.app';

function HomeIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="m2.25 12 8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
    </svg>
  );
}

function UsersIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z" />
    </svg>
  );
}

function ChatIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 0 1-.825-.242m9.345-8.334a2.126 2.126 0 0 0-.476-.095 48.64 48.64 0 0 0-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0 0 11.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155" />
    </svg>
  );
}

function ChartIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 0 1 3 19.875v-6.75ZM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V8.625ZM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 0 1-1.125-1.125V4.125Z" />
    </svg>
  );
}

function DocumentIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
    </svg>
  );
}

interface SidebarProps {
  currentStep?: number;
  connectionStatus?: string;
}

export default function Sidebar({ currentStep = -1, connectionStatus = 'connected' }: SidebarProps) {
  const { data: session } = useSession();
  const pathname = usePathname();
  const [backendOk, setBackendOk] = useState(false);
  const [frontendOk, setFrontendOk] = useState(true);

  useEffect(() => {
    setBackendOk(connectionStatus === 'connected');
  }, [connectionStatus]);

  const navItems: NavItem[] = [
    { label: 'ホーム', href: '/', icon: <HomeIcon />, active: pathname === '/' && currentStep <= 0 },
    { label: 'ペルソナ設定', href: '#personas', icon: <UsersIcon />, active: currentStep === 1 },
    { label: 'インタビュー', href: '#interview', icon: <ChatIcon />, active: currentStep === 2 },
    { label: '分析結果', href: '#analysis', icon: <ChartIcon />, active: currentStep === 3 },
    { label: 'レポート', href: '#report', icon: <DocumentIcon />, active: false },
  ];

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-56 flex-col border-r border-gray-200 bg-white">
      {/* App title */}
      <div className="px-5 pt-5 pb-4">
        <h1 className="text-lg font-semibold text-gray-900">AI Interview</h1>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3">
        {navItems.map((item) => (
          <a
            key={item.label}
            href={item.href}
            className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
              item.active
                ? 'bg-blue-600 text-white'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <span className={item.active ? 'text-white' : 'text-gray-400'}>{item.icon}</span>
            {item.label}
          </a>
        ))}

        {/* External link to Survey */}
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

      {/* User section */}
      <div className="border-t border-gray-200 px-4 py-3">
        {session?.user ? (
          <>
            <div className="mb-2">
              <p className="text-xs text-gray-500">ログイン中</p>
              <p className="truncate text-sm text-gray-700">{session.user.email}</p>
            </div>
            <button
              onClick={() => signOut({ callbackUrl: '/auth/signin' })}
              className="flex w-full items-center justify-center gap-2 rounded-lg border border-gray-200 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15m3 0 3-3m0 0-3-3m3 3H9" />
              </svg>
              ログアウト
            </button>
          </>
        ) : null}

        {/* Status indicators */}
        <div className="mt-3 space-y-1 text-xs">
          <div className="flex items-center justify-between">
            <span className="text-gray-400">バックエンド:</span>
            <span className={`inline-block h-2 w-2 rounded-full ${backendOk ? 'bg-green-500' : 'bg-red-400'}`} />
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-400">フロントエンド:</span>
            <span className={`inline-block h-2 w-2 rounded-full ${frontendOk ? 'bg-green-500' : 'bg-red-400'}`} />
          </div>
        </div>
      </div>
    </aside>
  );
}
