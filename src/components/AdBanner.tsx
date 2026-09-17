'use client';

import { useEffect, useRef } from 'react';

declare global {
  interface Window {
    atOptions?: {
      key: string;
      format: string;
      height: number;
      width: number;
      params: Record<string, string>;
    };
  }
}

interface AdBannerProps {
  adKey?: string;
  width?: number;
  height?: number;
  className?: string;
}

export default function AdBanner({
  adKey,
  width = 728,
  height = 90,
  className = '',
}: AdBannerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const key = adKey || process.env.NEXT_PUBLIC_ADSTERRA_KEY;

  useEffect(() => {
    if (!key) return;
    const container = containerRef.current;
    if (!container || container.childElementCount > 0) return;

    window.atOptions = {
      key,
      format: 'iframe',
      height,
      width,
      params: {},
    };

    const invokeScript = document.createElement('script');
    invokeScript.src = `https://www.highperformanceformat.com/${key}/invoke.js`;
    invokeScript.async = true;
    container.appendChild(invokeScript);
  }, [key, width, height]);

  if (!key) return null;

  return (
    <div className={`flex justify-center my-8 ${className}`} aria-hidden="true">
      <div ref={containerRef} style={{ width, height }} />
    </div>
  );
}
