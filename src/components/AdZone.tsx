'use client';

import { useEffect } from 'react';

const BOT_UA =
  /(bot|crawler|spider|crawl|slurp|headless|phantomjs|selenium|webdriver|puppeteer|playwright|electron|curl|wget|python|go-http|java\/|okhttp|scrapy|node-fetch|axios|httpclient|lighthouse|facebookexternalhit|telegrambot|whatsapp|slack-imgproxy)/i;

function looksLikeAutomation(): boolean {
  const w = window as unknown as Record<string, unknown>;
  if (navigator.webdriver === true) return true;
  if (w.__nightmare || w.callPhantom || w.__phantomas || w.__playwright || w.__selenium_unwrapped)
    return true;
  if (!navigator.languages || navigator.languages.length === 0) return true;
  return false;
}

export default function AdZone({ src }: { src: string }) {
  useEffect(() => {
    if (looksLikeAutomation() || BOT_UA.test(navigator.userAgent)) return;
    if (document.querySelector(`script[data-ad-zone="${src}"]`)) return;

    const inject = () => {
      const tag = document.createElement("script");
      tag.src = src;
      tag.async = true;
      tag.dataset.adZone = src;
      tag.setAttribute("data-cfasync", "false");
      document.head.appendChild(tag);
    };

    if (document.visibilityState === "visible") {
      inject();
      return;
    }
    const onVisible = () => {
      if (document.visibilityState !== "visible") return;
      document.removeEventListener("visibilitychange", onVisible);
      inject();
    };
    document.addEventListener("visibilitychange", onVisible);
    return () => document.removeEventListener("visibilitychange", onVisible);
  }, [src]);

  return null;
}
