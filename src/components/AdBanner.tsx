interface AdBannerProps {
  scriptUrl?: string;
  slot?: 1 | 2;
  className?: string;
}

export default function AdBanner({ scriptUrl, slot = 1, className = '' }: AdBannerProps) {
  const src =
    scriptUrl ||
    (slot === 2
      ? process.env.NEXT_PUBLIC_ADSTERRA_SCRIPT_URL_2
      : process.env.NEXT_PUBLIC_ADSTERRA_SCRIPT_URL);

  if (!src) return null;

  return (
    <div
      className={`ad-slot my-8 flex w-full justify-center ${className}`}
      data-ad-slot={slot}
    >
      <script src={src} async data-cfasync="false" />
    </div>
  );
}
