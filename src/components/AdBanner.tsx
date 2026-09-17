'use client';

import { useEffect, useRef } from 'react';

const injectedScripts = new Set<string>();

interface AdBannerProps {
  scriptUrl?: string;
  slot?: 1 | 2;
  className?: string;
}

export default function AdBanner({ scriptUrl, slot = 1, className = '' }: AdBannerProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  const src =
    scriptUrl ||
    (slot === 2
      ? process.env.NEXT_PUBLIC_ADSTERRA_SCRIPT_URL_2
      : process.env.NEXT_PUBLIC_ADSTERRA_SCRIPT_URL);

  useEffect(() => {
    if (!src || injectedScripts.has(src)) return;
    const container = containerRef.current;
    if (!container || container.querySelector('script')) return;

    injectedScripts.add(src);
    const script = document.createElement('script');
    script.src = src;
    script.async = true;
    script.setAttribute('data-cfasync', 'false');
    container.appendChild(script);
  }, [src]);

  if (!src) return null;

  return (
    <div
      ref={containerRef}
      className={`ad-slot my-8 flex w-full justify-center ${className}`}
      data-ad-slot={slot}
    />
  );
}
