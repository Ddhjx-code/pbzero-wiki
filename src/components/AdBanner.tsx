'use client';

import { useEffect, useState } from 'react';

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
  const key = adKey || process.env.NEXT_PUBLIC_ADSTERRA_KEY;
  const [srcDoc, setSrcDoc] = useState('');

  useEffect(() => {
    if (!key) return;
    const options = JSON.stringify({
      key,
      format: 'iframe',
      height,
      width,
      params: {},
    });
    setSrcDoc(
      `<!DOCTYPE html><html><head><meta charset="utf-8">` +
        `<style>html,body{margin:0;padding:0;overflow:hidden;background:transparent;}` +
        `body{display:flex;align-items:center;justify-content:center;}</style></head>` +
        `<body><script type="text/javascript">atOptions=${options};</script>` +
        `<script type="text/javascript" src="https://www.highperformanceformat.com/${key}/invoke.js"></script>` +
        `</body></html>`
    );
  }, [key, width, height]);

  if (!key) return null;

  return (
    <div className={`flex justify-center my-8 ${className}`}>
      <iframe
        title="Advertisement"
        width={width}
        height={height}
        srcDoc={srcDoc}
        scrolling="no"
        style={{ border: 0, overflow: 'hidden', maxWidth: '100%' }}
      />
    </div>
  );
}
