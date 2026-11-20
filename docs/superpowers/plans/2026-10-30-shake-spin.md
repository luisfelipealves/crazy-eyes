# Shake spin implementation plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task by task.

**Goal:** Test a WFF shake reaction that outlasts the shake for about 3 seconds.

**Architecture:** Directed angular interpolation around an eccentric pupil pivot; unchanged outer tilt and poke mask. Prove or reject the temporal hypothesis with injected acceleration on an actual Wear OS emulator.

**Tech stack:** WFF 1, Android resource-only APK, Python/Pillow, adb, GitHub Actions.

**Spec:** docs/superpowers/specs/2026-10-30-shake-spin-design.md

## Global constraints
- Keep minSdk 33, WFF 1, no executable APK code or new permissions.
- Preserve the clock above the eyes and the existing stable face.
- Separate experimental package com.luisfelipe.crazyeyes.watchface.shake, label Crazy Eyes Shake.
- No merge or publication to stores.

## Review focus
- Resting gravity and slow tilt must not trigger a full orbit.
- Pupil centroids must move oppositely after acceleration stops, not only during it.
- Repeated shakes must remain recoverable; no continuous spin after settling.
- Poke masks still clip moving pupils and AOD stays static.
- A schema-valid interpolation is insufficient evidence of renderer timing.

### Task 1: Characterize the renderer, then implement or reject

**Files:** tools/watchface_device_check.py; .github/workflows/android.yml; watchface/src/main/res/raw/watchface.xml; watchface/build.gradle.kts; watchface/src/main/res/values/strings.xml; tools/watchface_preview.py; docs/WATCHFACE_TESTING.md.

**Interfaces:** Consumes an installed resource-only APK on a Wear OS 4+ emulator. Produces screenshots and a pass/fail result for after-shake pupil motion.

- [x] Add an adb/Pillow integration check: idle image, brief 40:0:9.8 acceleration, return to 0:0:9.8, timed screenshots. Require opposite vertical displacement after release and baseline recovery after 3.6 seconds. Reject setup failures separately.
- [x] Run the baseline on the emulator: expected failure because no motion remains after release.
- [x] Add the minimal directed rotation and eccentric pivot to sensor-supported pupils; adapt the static preview renderer for rotation and comparisons, without simulating the temporal engine.
- [x] Run all existing Python tests, WFF schema and resource-only APK checks, lint, build, and the emulator integration check. If the hypothesis fails, do not ship it as complete; investigate before any further fix.
- [x] Obtain one independent whole-branch review; report actual evidence and physical-test limits. Commit and publish only on the agent test branch.

Native timing assertion and conservative replay are documented in docs/SHAKE_VERIFICATION.md. The native images prove the effect; the original CI assertion used screenshot completion times and was corrected. Physical watch testing remains pending.
