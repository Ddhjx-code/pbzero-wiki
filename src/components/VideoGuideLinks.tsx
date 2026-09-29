import { VideoEntry } from "@/lib/videos";

interface VideoGuideLinksProps {
  entries: VideoEntry[];
  heading?: string;
}

export default function VideoGuideLinks({
  entries,
  heading = "Video guides",
}: VideoGuideLinksProps) {
  if (entries.length === 0) return null;

  return (
    <section
      aria-label={heading}
      className="mb-8 overflow-hidden rounded-lg border border-border bg-card"
    >
      <div className="border-b border-border bg-muted/40 px-5 py-2.5">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          {heading}
        </h2>
      </div>

      <ul className="divide-y divide-border">
        {entries.map((video, i) => (
          <li key={`${video.url}-${i}`} className="px-5 py-4">
            <a
              href={video.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-medium text-foreground underline decoration-dotted underline-offset-2 transition-colors hover:text-accent"
            >
              {video.title}
            </a>

            <p className="mt-0.5 text-xs text-muted-foreground">
              {video.channel}
              {video.duration && <span> · {video.duration}</span>}
            </p>

            {video.covers && (
              <p className="mt-2 text-xs text-muted-foreground">
                <span className="font-medium text-foreground">Covers:</span>{" "}
                {video.covers}
              </p>
            )}
            {video.bestFor && (
              <p className="mt-1 text-xs text-muted-foreground">
                <span className="font-medium text-foreground">Best for:</span>{" "}
                {video.bestFor}
              </p>
            )}
            {video.caveat && (
              <p className="mt-1 text-xs text-accent">{video.caveat}</p>
            )}

            {video.timestamps && video.timestamps.length > 0 && (
              <ul className="mt-2 flex flex-wrap gap-x-4 gap-y-1">
                {video.timestamps.map((stamp) => (
                  <li key={stamp.at}>
                    <a
                      href={withTimestamp(video.url, stamp.at)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-mono text-xs text-muted-foreground transition-colors hover:text-accent"
                    >
                      {stamp.at} {stamp.label}
                    </a>
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>

      <p className="border-t border-border px-5 py-3 text-xs leading-relaxed text-muted-foreground">
        These are third-party videos hosted on their own platforms. Nothing here
        is hosted, copied or embedded by this site &mdash; the links above take
        you to the uploader. Credit and rights belong to each channel. If a link
        here should not be, <a href="/contact">tell us</a> and we will remove it
        within one working day.
      </p>
    </section>
  );
}

function withTimestamp(url: string, at: string): string {
  const seconds = toSeconds(at);
  if (seconds === null) return url;

  const joiner = url.includes("?") ? "&" : "?";
  return `${url}${joiner}t=${seconds}s`;
}

function toSeconds(label: string): number | null {
  const parts = label
    .replace(/[^\d:]/g, "")
    .split(":")
    .filter(Boolean)
    .map(Number);

  if (parts.length === 0 || parts.some(Number.isNaN)) return null;

  return parts.reduce((total, value) => total * 60 + value, 0);
}
