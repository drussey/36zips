# Snapshot: the Bird Money restyle

Acid lime + violet after Gucci Mane's *Bird Money* cover (`birdmoney.jpeg`).
Reverted 2026-09-03 at the user's request; kept here so it can be flipped back.

Re-apply:

    cp site/snapshots/birdmoney/{index.html,style.css,app.js} site/

`app.js` is identical to the gold theme's — the restyle was CSS plus the
masthead markup only. No rebuild needed; `site/data.js` was never touched.
