# Labels and Speed Implementation Plan

> **For agentic workers:** Execute inline with superpowers:executing-plans.

**Goal:** Visible intensity choices and faster Crazy movement.
**Architecture:** Captioned locale-aware editor icons; shared pupil under exclusive2s/3s concentric orbit controllers; mode-dependent gyro gain/fallback cadence. Native probes validate duration/gain and inspect editor.
**Tech Stack:** WFF1/Python/Pillow/Gradle/GitHub Actions/Wear OS4.
**Spec:** docs/superpowers/specs/2026-11-11-labels-speed-design.md

## Global Constraints
Preserve IDs/defaultCrazy/ON,13px Calm and26px Crazy radii; Calm3s/Crazy2s; tilt45°Calm/30°Crazy with13/20 and26/40 clamps; fallback2s/1s. All4styles/colors, masks/clock/battery/tap/blink/AOD intact. WFF1/resource-only/OS4+, no merge.

## Review Focus
- Inactive rotation controller stays zero; OFF blocks both, including fallback.
- Nested pivots remain concentric; child pulse and neutral gaze unchanged.
- Icon captions remain readable under monochrome tint/circular crop and Portuguese fallback.
- Fast native validation rejects slow/brief/reversed/never-settling motion; real tilt gain is measured.
- Editor evidence must inspect rendered captions; accessibility labels alone do not prove Samsung appearance.

### Task1: Tested0.1.10 update
**Files:** WFFXML/strings/icon PNGs/generator/version; preview/tests; duration/gain motion checker; editor checker; workflow/testing instructions.
**Interfaces:** validate_trials(baseline,traces,orbit_radius=26,duration=3); validate_tilt_gain(baseline,tilted,expected); render_preview(XML,values); visible_intensity_labels(ui_xml)->set[str].
- [ ] Add failing resource/speed/controller/native boundary tests and observe RED.
- [ ] Implement captions/locales and exclusive speed controllers; update affected original tests; GREEN suite/schema/actionlint.
- [ ] Native tests/gain/editor evidence; inspect screenshots and exact product/fixture APKs.
- [ ] Independent review, draft stackedPR, saveAPK and deliver for physical Samsung testing. No merge.
