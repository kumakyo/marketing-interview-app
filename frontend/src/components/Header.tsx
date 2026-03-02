'use client';

import { useSession, signOut } from 'next-auth/react';
import { useState } from 'react';

const QUANTITATIVE_URL =
  process.env.NEXT_PUBLIC_QUANTITATIVE_URL ||
  'https://tames-frontend-staging-128899916170.asia-northeast1.run.app';

export default function Header() {
  const { data: session } = useSession();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-[var(--border)] bg-white/80 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6">
        {/* Logo & Nav */}
        <div className="flex items-center gap-6">
          <a href="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-[var(--tames-primary)] to-[var(--tames-accent)] text-white text-sm font-bold">
              t
            </div>
            <span className="text-lg font-semibold text-[var(--foreground)]">
              tames
            </span>
          </a>

          <nav className="hidden items-center gap-1 sm:flex">
            <a
              href="/"
              className="rounded-md px-3 py-1.5 text-sm font-medium text-[var(--tames-primary)] bg-blue-50"
            >
              Interview
            </a>
            <a
              href={QUANTITATIVE_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-md px-3 py-1.5 text-sm font-medium text-[var(--muted)] hover:text-[var(--foreground)] hover:bg-gray-50 transition-colors"
            >
              Survey
            </a>
          </nav>
        </div>

        {/* User */}
        {session?.user && (
          <div className="relative">
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              className="flex items-center gap-2 rounded-full border border-[var(--border)] px-3 py-1.5 text-sm hover:bg-gray-50 transition-colors"
            >
              {session.user.image ? (
                <img
                  src={session.user.image}
                  alt=""
                  className="h-6 w-6 rounded-full"
                  referrerPolicy="no-referrer"
                />
              ) : (
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-[var(--tames-primary)] text-white text-xs font-medium">
                  {session.user.name?.charAt(0) || '?'}
                </div>
              )}
              <span className="hidden text-[var(--foreground)] sm:inline">
                {session.user.name}
              </span>
              <svg className="h-4 w-4 text-[var(--muted)]" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
              </svg>
            </button>

            {menuOpen && (
              <>
                <div className="fixed inset-0" onClick={() => setMenuOpen(false)} />
                <div className="absolute right-0 mt-2 w-48 rounded-lg border border-[var(--border)] bg-white shadow-lg py-1">
                  <div className="px-4 py-2 border-b border-[var(--border)]">
                    <p className="text-xs text-[var(--muted)]">{session.user.email}</p>
                  </div>
                  <button
                    onClick={() => signOut({ callbackUrl: '/auth/signin' })}
                    className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 transition-colors"
                  >
                    ログアウト
                  </button>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </header>
  );
}
