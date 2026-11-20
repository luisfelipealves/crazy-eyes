# Mask Composition Fix Implementation Plan

> **For agentic workers:** Execute inline with superpowers:executing-plans.

**Goal:** Remove the rectangular overlay and verify all four native silhouettes.

**Architecture:** Nested groups separate silhouette clipping from animated tap clipping. Preview follows WFF sibling-mask union. CI renders four fresh-install style-default variants and checks independent visual probes.

**Tech Stack:** WFF1 XML, Python/Pillow, Gradle/GitHub Actions, Wear OS4 emulator.

**Spec:** docs/superpowers/specs/2026-11-10-mask-composition-design.md

## Global Constraints

Preserve four styles/six colors, existing configuration IDs, Wear OS4+, resource-only APK, gyro/shake/clock/tap behavior and AOD. No merge; physical user test follows delivery.

## Review Focus

- The real0.1.5 rectangle screenshot must fail independent native probes.
- Preview sibling masks must union; nested masks must intersect.
- Fixed frames stay outside blink/tap clipping.
- CI must validate all four actual default renders, not just a local simulation.
- Product APK must retain the original default and exact reviewed XML after variant builds.

### Task1: Fix composition and deliver a natively checked APK

- [x] Observe failing native-mask semantics test; correct preview and reproduce three full-style regression failures on0.1.5.
- [x] Nest animated content under silhouette clipping; run26 passing tests and WFF1/AOD validation.
- [x] Add real negative screenshot, native silhouette probes and four-style CI fixtures; validate workflow with actionlint.
- [ ] Independent review and draft stacked PR; run CI build and all four native style checks.
- [ ] Inspect real screenshots, validate product APK, save and deliver0.1.6 with native evidence.
