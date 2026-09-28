"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";

interface SearchEntry {
  s: string;
  t: string;
  d: string;
  k: string;
  x: string;
}

function score(entry: SearchEntry, terms: string[]): number {
  const title = entry.t.toLowerCase();
  const body = `${entry.k} ${entry.x} ${entry.d}`.toLowerCase();
  let total = 0;
  for (const term of terms) {
    const inTitle = title.indexOf(term);
    if (inTitle === 0) total += 120;
    else if (inTitle > 0) total += 70;
    else if (body.includes(term)) total += 25;
    else return -1;
  }
  return total + Math.max(0, 30 - entry.t.length / 3);
}

export default function SearchDialog() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [index, setIndex] = useState<SearchEntry[] | null>(null);
  const [active, setActive] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setOpen((v) => !v);
      }
      if (event.key === "Escape") setOpen(false);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    if (!open || index) return;
    fetch("/search-index.json")
      .then((r) => r.json())
      .then(setIndex)
      .catch(() => setIndex([]));
  }, [open, index]);

  useEffect(() => {
    if (open) {
      setActive(0);
      const id = window.setTimeout(() => inputRef.current?.focus(), 30);
      return () => window.clearTimeout(id);
    }
    setQuery("");
  }, [open]);

  const results = useMemo(() => {
    if (!index) return [];
    const terms = query.toLowerCase().split(/\s+/).filter(Boolean);
    if (terms.length === 0) return [];
    return index
      .map((entry) => ({ entry, s: score(entry, terms) }))
      .filter((r) => r.s > 0)
      .sort((a, b) => b.s - a.s)
      .slice(0, 12)
      .map((r) => r.entry);
  }, [index, query]);

  const onKeyDown = useCallback(
    (event: React.KeyboardEvent) => {
      if (event.key === "ArrowDown") {
        event.preventDefault();
        setActive((i) => Math.min(i + 1, results.length - 1));
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        setActive((i) => Math.max(i - 1, 0));
      } else if (event.key === "Enter" && results[active]) {
        window.location.href = `/${results[active].s}`;
      }
    },
    [results, active]
  );

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-label="Search the site"
        className="flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:border-accent hover:text-accent"
      >
        <span aria-hidden="true">⌕</span>
        <span className="hidden sm:inline">Search</span>
        <kbd className="hidden rounded border border-border px-1.5 py-0.5 text-[10px] sm:inline">
          ⌘K
        </kbd>
      </button>

      {open && (
        <div
          className="fixed inset-0 z-50 flex items-start justify-center bg-black/60 p-4 pt-[12vh]"
          onClick={() => setOpen(false)}
        >
          <div
            className="w-full max-w-xl overflow-hidden rounded-xl border border-border bg-card shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center gap-3 border-b border-border px-4">
              <span aria-hidden="true" className="text-muted-foreground">
                ⌕
              </span>
              <input
                ref={inputRef}
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value);
                  setActive(0);
                }}
                onKeyDown={onKeyDown}
                placeholder="Search bosses, weapons, Pictos, areas..."
                className="w-full bg-transparent py-3.5 text-sm text-foreground outline-none placeholder:text-muted-foreground"
              />
              <kbd className="rounded border border-border px-1.5 py-0.5 text-[10px] text-muted-foreground">
                esc
              </kbd>
            </div>

            <div className="max-h-[52vh] overflow-y-auto">
              {query.trim() === "" && (
                <p className="px-4 py-6 text-center text-sm text-muted-foreground">
                  {index
                    ? `Search ${index.length} pages — bosses, enemies, weapons, Pictos, areas.`
                    : "Loading index..."}
                </p>
              )}
              {query.trim() !== "" && results.length === 0 && (
                <p className="px-4 py-6 text-center text-sm text-muted-foreground">
                  No pages match &ldquo;{query}&rdquo;.
                </p>
              )}
              <ul>
                {results.map((entry, i) => (
                  <li key={entry.s}>
                    <Link
                      href={`/${entry.s}`}
                      onClick={() => setOpen(false)}
                      onMouseEnter={() => setActive(i)}
                      className={`flex items-baseline justify-between gap-4 px-4 py-2.5 text-sm transition-colors ${
                        i === active ? "bg-muted/60 text-accent" : "text-foreground"
                      }`}
                    >
                      <span className="truncate">{entry.t}</span>
                      <span className="shrink-0 text-[11px] uppercase tracking-wide text-muted-foreground">
                        {entry.k}
                      </span>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
