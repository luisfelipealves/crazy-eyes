# Animation Intensity Implementation Plan

> **For agentic workers:** Execute inline with superpowers:executing-plans.

**Goal:** Native Calm/Crazy intensity and independent shake switch.
**Architecture:** Existing WFF transforms read editor configurations; pivotY changes only orbit radius. Preview understands configuration expressions/booleans. Native probes measure13/26px radii.
**Tech Stack:** WFF1, Python/Pillow, Gradle/GitHub Actions, Wear OS4.
**Spec:** docs/superpowers/specs/2026-11-10-animation-intensity-design.md

## Global Constraints
Wear OS4+, resource-only, defaultCrazy/shakeON; calm13/20px tilt/fallback and13px orbit; Crazy26/40px and26px orbit.3s shake/opposite directions/threshold25m/s². Preserve shape, pupil size, tap/blink/battery/AOD/clock. No merge.

## Review Focus
- Configuration expressions resolve string IDs on WFF1 and don't change unsupported-sensor fallback.
- Pivot changes preserve neutral gaze and pupil size in both eyes.
- ShakeOFF retains tilt and automatic expressions in either mode.
- All complete styles remain independently masked and battery/tap/AOD intact.
- Native fixtures match product source except editor defaults; smaller orbit cannot pass large-orbit validation.

### Task1: Motion settings and tested APK
**Files:** WFFXML, both strings.xml, watchface/build.gradle.kts; tools/watchface_preview.py, tools/watchface_device_check.py; tools/tests/test_watchface_animation_intensity.py and device/shake tests; workflow and WATCHFACE_TESTING.md.
**Interfaces:** preview evaluate(expression,values), render_preview(XML,values); validate_trials(baseline,traces,orbit_radius=26); run(package,output,expect_spin=True,orbit_radius=26).
- [ ] Write tests for settings, half amplitude, neutral geometry, both shake states and preserved interactions; run RED against0.1.7.
- [ ] Add native configs/transforms/localized labels, preview support and parameterized orbit validator; run targeted/full suite/schema/actionlint GREEN.
- [ ] Build calmON/crazyOFF fixtures, verify exactdefault differences and exercise both native variants alongside all existing regressions.
- [ ] Independent review, commit/publish draft stackedPR, inspect native evidence, save APK and deliver. Keep physical test pending/no merge.
