import Link from "next/link";
import { PageFact } from "@/lib/content";
import { linkFactValue } from "@/lib/fact-links";

const ELEMENT_COLORS: Record<string, string> = {
  fire: "#e8590c",
  ice: "#15aabf",
  lightning: "#e6b800",
  earth: "#8d6e63",
  light: "#d4a017",
  dark: "#7c4dff",
  physical: "#787878",
  void: "#5c6bc0",
};

const AFFINITY_LABELS = new Set(["weak to", "resists", "absorbs", "immune"]);

function elementColor(token: string): string | null {
  const key = token.trim().toLowerCase().replace(/[^a-z]/g, "");
  if (!key) return null;
  if (ELEMENT_COLORS[key]) return ELEMENT_COLORS[key];
  for (const [name, color] of Object.entries(ELEMENT_COLORS)) {
    if (key.startsWith(name)) return color;
  }
  return null;
}

function asElementList(value: string): string[] | null {
  const tokens = value
    .split(/[,·]/)
    .map((token) => token.trim())
    .filter(Boolean);

  if (tokens.length === 0) return null;
  return tokens.every((token) => elementColor(token) !== null) ? tokens : null;
}

function Chip({ text }: { text: string }) {
  const color = elementColor(text);
  if (!color) return <span className="text-foreground">{text}</span>;

  return (
    <span
      className="inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium"
      style={{
        color,
        borderColor: `${color}66`,
        backgroundColor: `${color}1f`,
      }}
    >
      {text}
    </span>
  );
}

function FactValue({ label, value }: PageFact) {
  const isAffinity = AFFINITY_LABELS.has(label.trim().toLowerCase());

  if (isAffinity) {
    const elements = asElementList(value);
    if (elements) {
      return (
        <span className="flex flex-wrap gap-1.5">
          {elements.map((element, i) => (
            <Link
              key={i}
              href="/enemy-weaknesses"
              className="transition-opacity hover:opacity-80"
            >
              <Chip text={element} />
            </Link>
          ))}
        </span>
      );
    }
  }

  const href = linkFactValue(label, value);
  if (href) {
    return (
      <Link
        href={href}
        className="text-foreground underline decoration-dotted decoration-muted-foreground/50 underline-offset-2 transition-colors hover:text-accent hover:decoration-accent"
      >
        {value}
      </Link>
    );
  }

  return <span className="text-foreground">{value}</span>;
}

interface FactsCardProps {
  facts?: PageFact[];
  title?: string;
}

export default function FactsCard({ facts, title = "Quick Facts" }: FactsCardProps) {
  if (!facts || facts.length === 0) return null;

  return (
    <section
      aria-label={title}
      className="mb-8 overflow-hidden rounded-lg border border-border bg-card"
    >
      <div className="border-b border-border bg-muted/40 px-5 py-2.5">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          {title}
        </h2>
      </div>
      <dl className="divide-y divide-border">
        {facts.map((fact, i) => (
          <div
            key={i}
            className="grid grid-cols-[104px_1fr] gap-x-4 px-5 py-2.5 sm:grid-cols-[140px_1fr]"
          >
            <dt className="text-sm font-medium text-muted-foreground">
              {fact.label}
            </dt>
            <dd className="text-sm leading-relaxed">
              <FactValue label={fact.label} value={fact.value} />
            </dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
