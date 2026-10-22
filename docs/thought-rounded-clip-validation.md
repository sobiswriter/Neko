# Rounded blur clipping fix — 2026-10-22

![Rounded glass on test-owned light/dark backgrounds](neko-thoughts-native.png)

This supersedes the native compositor technique in [the previous report](thought-backdrop-validation.md). The user reported that blur extended beyond the rounded corners and exposed a square.

## Reproduction and root cause

Qt's mask excluded the corners, and Windows `GetWindowRgn` confirmed a complex native region excluding the same points. Nevertheless, the accent blur changed pixels outside that region. The earlier check inspected only the mask and therefore missed the compositor spill.

A before/after capture of the same test-owned striped window reproduced differences of **18–62 channel levels** outside the nominal rounded corners. Reapplying a DWM blur region returned success but did not fix the spill. Other accent variants either still spilled or provided no blur. These experiments are rejected, not production dependencies. Microsoft's [rounded-window guidance](https://learn.microsoft.com/en-us/windows/apps/desktop/modernize/ui/apply-rounded-corners) also warns that per-pixel alpha/window-region windows cannot rely on its automatic corner rounding.

## Correction and tradeoff

Remove the private accent/composition API entirely. Capture only the small area behind the thought while its window is hidden, soften it with Qt's existing graphics effect at approximately **3 logical pixels**, and paint it **inside the same 20px rounded path** as the glass. A small capture margin supplies blur-edge pixels. The 88% overall opacity and faint tint/rim remain.

The sample is local RAM used for UI rendering: nothing is saved or uploaded, there is no recording loop, and the stored sample is cleared when the thought hides. **It is a per-thought snapshot:** live video or scrolling underneath does not update during the 5.5–10s thought. This is an explicit tradeoff for reliable clipping and controllable light blur; the older no-desktop-capture description applies to the superseded native implementation.

Hide an existing thought before replacement and use [DwmFlush](https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/nf-dwmapi-dwmflush) before sampling, so the prior caption is removed. Recompute size/position and sample before showing the new caption. Light/dark text color adapts to the sample for readability. If a sample is unavailable, keep plain translucent glass with the existing text shadow.

Clear the old fixed-height constraints before measuring replacement words; the native reuse trial exposed a tall caption retaining its height after becoming short. The new size regression covers short → long → short.

## Verification

- Seven focused source tests passed: blur softens detail/preserves colors within two channel levels and DPR 2 metadata, missing-sample fallback, clearing the sample on hide, replacement sizing, rounded/input-transparent rendering/read time, changing words and quiet/visible-thought rules.
- `tools/preview_thoughts.py` now compares actual screen pixels **outside** the rounded corners with the unmodified test-owned background, rather than trusting the mask. All 36 sampled outside points across initial display, resized/moved reuse and restored-size reuse had **zero change** at DPR 1.0.
- Native click-through to the underlying test window and unchanged foreground focus passed. Both light/dark captions and all three show/resize/hide sequences passed.
- Stripe contrast is 62 under the light 3px softening versus 70 outside. The former native effect gave 13 but spilled outside the corners; the new effect is intentionally gentler. The preview uses the companion's actual shadow treatment.
- The [machine-readable measurements](thoughts-native.json) contain sizes, opacity, all outside-corner differences and lifecycle cases.

Full-suite, Windows 10, physical mixed-DPI and long-session checks were not repeated. See release metadata below for the exact packaged deliverable and package check result.

## Release

Both exact-executable packaging checks passed: resource/module hashes and native startup/tray/topmost/single-instance behavior. Only test-owned processes were stopped.

- Current: `dist/DesktopNeko.exe`, 100,255,727 bytes; SHA-256 `e7794b04c72e3de8ab300b76d4d1feb2cbc210a24e06642c4ca01cc91f2d9aee`.
- Previous: `dist/DesktopNeko-previous.exe`, 100,255,334 bytes; SHA-256 `716f99473a6cb20b4734471bce96b904478b20c0f2fb870049a0d56f42c6dfbe`.
