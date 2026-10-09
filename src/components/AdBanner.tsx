import AdZone from "./AdZone";

interface AdBannerProps {
  scriptUrl?: string;
  className?: string;
}

export default function AdBanner({ scriptUrl, className = "" }: AdBannerProps) {
  const src =
    scriptUrl || process.env.NEXT_PUBLIC_ADSTERRA_SCRIPT_URL;

  if (!src) return null;

  if (process.env.NEXT_PUBLIC_AD_GATE === "off") {
    return (
      <script
        src={src}
        async
        data-cfasync="false"
        className={className || undefined}
      />
    );
  }

  return <AdZone src={src} />;
}
