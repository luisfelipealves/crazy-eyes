# Whole Eye Styles Implementation Plan

> **For agentic workers:** Execute inline with superpowers:executing-plans.

**Goal:** Correct eye customization so every style changes the full eye.

**Architecture:** Native frame/background/opening selections surround unchanged pupil motion groups. Neutral animated tap bands close the opening without hiding frames. Ambient branches use matching silhouettes.

**Tech Stack:** WFF1 XML, Python/Pillow assets and preview checks, Android/Gradle CI.

**Spec:** docs/superpowers/specs/2026-11-10-whole-eye-styles-design.md

## Global Constraints

Wear OS4+, resource-only APK, existing package/name, font40, inverted gyro, radius26/3s shake, fallback, tap isolation and six iris colors. No merge before user testing.

## Review Focus

- Square frame corners must not be clipped by the legacy oval mask.
- Cat and Monster change outer silhouette, not only iris details.
- Fixed frames remain visible when blink/tap closes the opening.
- Pupils remain masked by their selected opening during tilt, shake and fallback.
- AOD matches all four silhouettes and stays below15% lit pixels.

### Task1: Complete style correction and test APK

**Files:** watchface.xml; watchface_assets.py and new neutral band resources; customization/assets tests; validate_watchface.py; version and test instructions.

**Interfaces:** existing eye_style and eye_color configuration IDs remain unchanged. render_preview values and poke API remain unchanged.

- [x] Write visual regression assertions for complete silhouettes, metal frame and per-style AOD; observe four failures on0.1.4.
- [x] Implement full frames/opening masks/backgrounds and neutral tap band; version0.1.5.
- [x] Run complete Python suite, WFF schema and all AOD budgets; inspect previews.
- [ ] Independently review, commit and publish draft stacked PR; build APK.
- [ ] Validate exact packaged XML/no DEX, save APK and deliver for physical testing.
