'use client';

import { useEffect, useRef, useState } from 'react';

const BOT_UA =
  /(bot|crawler|spider|crawl|slurp|headless|phantomjs|selenium|webdriver|puppeteer|playwright|electron|curl|wget|python|go-http|java\/|okhttp|scrapy|node-fetch|axios|httpclient|lighthouse|facebookexternalhit|telegrambot|whatsapp|slack-imgproxy)/i;

function automationMarkers(): boolean {
  const w = window as unknown as Record<string, unknown>;
  if (navigator.webdriver === true) return true;
  if (w.__nightmare || w.callPhantom || w.__phantomas || w.__playwright || w.__selenium_unwrapped)
    return true;
  if (!navigator.languages || navigator.languages.length === 0) return true;
  return false;
}

function whenVisible(callback: () => void): () => void {
  if (document.visibilityState === 'visible') {
    callback();
    return () => {};
  }
  const onChange = () => {
    if (document.visibilityState === 'visible') {
      document.removeEventListener('visibilitychange', onChange);
      callback();
    }
  };
  document.addEventListener('visibilitychange', onChange);
  return () => document.removeEventListener('visibilitychange', onChange);
}

export default function AdGate({ src, slot }: { src: string; slot: number }) {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const [doc, setDoc] = useState('');

  useEffect(() => {
    if (automationMarkers() || BOT_UA.test(navigator.userAgent)) return;

    let observer: IntersectionObserver | null = null;
    let mounted = true;

    const arm = () => {
      if (!mounted) return;
      const go = () => {
        if (!mounted) return;
        setDoc(
          '<!DOCTYPE html><html><head><meta charset="utf-8">' +
            '<style>html,body{margin:0;padding:0;overflow:hidden}</style></head>' +
            `<body><script src="${src}" data-cfasync="false"></script></body></html>`,
        );
      };
      if (!hostRef.current || typeof IntersectionObserver === 'undefined') {
        go();
        return;
      }
      observer = new IntersectionObserver(
        entries => {
          if (entries.some(entry => entry.isIntersecting)) {
            observer?.disconnect();
            go();
          }
        },
        { rootMargin: '160px 0px' },
      );
      observer.observe(hostRef.current);
    };

    const offVisible = whenVisible(arm);
    return () => {
      mounted = false;
      observer?.disconnect();
      offVisible();
    };
  }, [src]);

  return (
    <div ref={hostRef} className="ad-slot flex w-full justify-center" data-ad-slot={slot}>
      {doc ? (
        <iframe
          title="Advertisement"
          srcDoc={doc}
          width={728}
          height={90}
          className="max-w-full border-0"
          sandbox="allow-scripts allow-same-origin allow-popups"
        />
      ) : null}
    </div>
  );
}
