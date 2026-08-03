# playground footer — design

Date: 2026-08-03
Status: approved

## What we are building

A footer line on the playground page that tells at a glance how many text
operations the playground offers.

## Locked decisions

- A `<footer id="footer">` element at the bottom of the page body (after the
  result paragraph) with the exact text `textkit playground · N operations`,
  where N is the number of entries in `OPERATIONS` in `textkit/web.py`,
  rendered server-side (no JavaScript involved).
- The `·` separator is the middle-dot character.
- Markup-only change in `textkit/web.py`; no new endpoints, no styling,
  no external assets.
- Everything else on the page stays exactly as specified in the previous
  playground specs.

## Main user scenario

1. Open `/` — the bottom of the page shows `textkit playground · 5 operations`.
2. The footer is static: typing, Apply and Clear do not change it.

## Out of scope

Styling, localisation, version numbers, links in the footer.
