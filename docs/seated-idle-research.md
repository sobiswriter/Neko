# Seated idle study · 2026-10-23

The user rejected the repeated chest-shading breath and explicitly requests no breathing. The goal is a supported, quiet sitting animal with a small connected body action, rather than globally moving the sprite or freezing all body acting.

## Online creator references

- [Pinino Pixel — Kitties Idle Run4](https://pininopixel.itch.io/kitties-idle-run-4): the creator page and its displayed animated cat preview/idle sheet were inspected in the browser. Useful visual cues are a compact seated footprint, readable head/ear/tail details and quiet pauses between accents.
- [Elthen —2D Pixel Art Cat Sprites](https://elthen.itch.io/2d-pixel-art-cat-sprites): the creator page's small animated action grid was inspected. Its separate idle/action silhouettes encourage a restrained sitting pose rather than continuous locomotion. These tiny web previews establish visual inspiration; no exact biological timing or measured motion amplitude is claimed.

No creator artwork was downloaded or imported into runtime. Links are preserved for future review; their web availability can change. The user's permanent [motion library](../references/motion/README.md), especially the seated silhouettes and connected chest/pelvis/support guidance, remains relevant. Running compression is not transplanted into an ordinary sit.

## Proposed mechanics, then prototype corrections

The pelvis and paws support the same ground footprint throughout. One shoulder/inner foreleg yields slightly, holds, and recovers, while the opposite outer foreleg supports. Head/nose stay quiet; a brief ear response precedes a brisk happy blink. This is a proposed stylized acting choice, not observed live-cat biomechanics.

Two built-in ImageGen drafts supply new drawings. Draft1 changes contacts and repeats closed lids too long. Draft2 improves the sequence but still needs anchor registration, exact canonical support and open-eye reuse during the settle. A wide torso composite produces a wrist kink at its contact join; the selected import preserves that outer supporting wrist and draws the shoulder/inner foreleg/right torso together. The black limb contours change, rather than only chest color. No inflation/deflation, global translation, per-pose scaling or painted anatomy is used.

Quiet neutral holds total4.5s within5.8s, with a300ms blink. This cadence is specific to Neko, not a scientific timing claim. The first off-grid350ms settle caused a native paint check to miss a100ms closing pose; align settle/recovery to300ms and observe all phases. Stable geometry and successful paint coverage are technical evidence, not proof that the user will like the result.
