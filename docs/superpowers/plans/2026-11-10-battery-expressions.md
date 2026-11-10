# Battery Expressions Implementation Plan

> **For agentic workers:** Execute inline with superpowers:executing-plans.

**Goal:** Add automatic tired and charging expressions to all four styles.

**Architecture:** A separate mood mask clips the existing animated opening. Pupil child groups scale only while charging. WFF sources handle state without native app code.

**Tech Stack:** WFF1 XML, Python/Pillow verification, Gradle/GitHub Actions, Wear OS4 emulator.

**Spec:** docs/superpowers/specs/2026-11-10-battery-expressions-design.md

## Global Constraints

Wear OS4+, resource-only APK, existing package/styles/colors/clock/gyro/shake/tap behavior and unchanged AOD. Low battery<=20%; charging overrides tired state. No additional roadmap items or merge.

## Review Focus

- Mood/tap/silhouette masks remain independent clipping stages.
- Charging pulse scales both axes below the shake pivot and within original bounds.
- Charging at low battery opens the eye; unplugging at20% closes it again.
- Normal blink/reflections cannot masquerade as charging pulse in native tests.
- Battery test teardown restores normal power before existing native motion checks.

### Task1: Battery moods and test APK

- [x] Write threshold/charging/fallback/AOD behavior tests; observe failures on0.1.6.
- [x] Add native WFF expressions, separate mask and bounded pulse groups; preview supports boolean expressions and horizontal scaling.
- [x] Add native mood probes and blink false-positive regression; run36tests, schema and workflow validation.
- [ ] Independent review, draft stacked PR and CI build.
- [ ] Verify native mood transitions/pulse on all four styles and product APK; save and deliver.
