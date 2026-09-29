# Video guide link index

`/boss-video-guides` lists third-party boss walkthroughs as **links only**.
Nothing is embedded, downloaded, re-hosted or copied.

## Why links

A hyperlink neither copies nor displays the linked work, so it avoids the
embedding question entirely. US courts are split on embedded players, and the
split is worse for video than for images because a performance right does not
require a fixed copy. Links sidestep that, and they also avoid the search
engine "reused content" pattern of a page whose visible body is someone else's
player.

## Data file

`src/data/videos.json` maps a page slug to an array of entries:

```json
{
  "puppet-boss": [
    {
      "title": "exact video title, verbatim",
      "channel": "uploader name",
      "url": "https://www.youtube.com/watch?v=...",
      "duration": "12:40",
      "covers": "both phases; ends before the enrage timer",
      "bestFor": "players on Dual Swords; the parry timings differ for Long Sword",
      "caveat": "recorded before the 2026-11 balance patch",
      "timestamps": [
        { "at": "4:12", "label": "phase two parry" },
        { "at": "11:05", "label": "finisher" }
      ]
    }
  ]
}
```

`timestamps[].at` is turned into a `?t=` deep link by the component, so write
it as `m:ss` or `h:mm:ss`.

Optional fields may be omitted. `covers` and `bestFor` are the two that make
the page worth more than the YouTube search results, so fill them whenever the
video supports it.

## Rules

- Only link videos actually watched and verified. No invented timestamps.
- One preferred link per boss where possible.
- Never copy a video description; summarise in our own words.
- Never hotlink thumbnails from `i.ytimg.com` - a text link stays clear of the
  image-display question entirely.
- Use the YouTube Data API for metadata, not page scraping.
- Anything a patch has overtaken gets a `caveat`, not deletion.

## Empty before launch

The file ships as `{}` and `VideoGuideLinks` renders nothing when a page has no
entries, so there are no empty shells on live pages. Populate at launch.
