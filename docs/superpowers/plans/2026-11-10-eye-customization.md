# Eye Customization Implementation Plan

> **For agentic workers:** Execute inline with superpowers:executing-plans.

**Goal:** Let the user choose four eye styles and six colors in the watch-face editor.

**Architecture:** Native WFF1 configurations select vector pupils inside the existing motion groups. Preview tooling resolves the same configurations for local visual regression checks.

**Tech Stack:** WFF1 XML, Android resources, Python/Pillow verification, Gradle/GitHub Actions.

**Spec:** docs/superpowers/specs/2026-11-10-eye-customization-design.md

## Global Constraints

Wear OS 4+, resource-only APK, existing package and label. Preserve font 40, inverted gyro, radius-26 shake, tap masks, fallback wander and AOD. No features beyond item 1.

## Review Focus

- Both eyes receive the selected style/color, including sensorless fallback.
- Black pupil and white reflections do not inherit iris color.
- Editing is enabled and all localized labels resolve.
- Ambient output remains below the pixel budget for every selection.
- Replacing the bitmap pupil does not detach shake/gyro transforms or tap masking.

### Task 1: Editable eyes and verification

**Files:** watchface.xml, watch_face_info.xml, strings.xml (default and pt-rBR), build.gradle.kts; tools/watchface_preview.py; tools/tests/test_watchface_customization.py and existing shake selectors; docs/WATCHFACE_TESTING.md.

**Interfaces:** User settings eye_style (cartoon/cat/robot/monster) and eye_color (gray/blue/green/brown/purple/amber). render_preview values accepts CONFIGURATION.eye_style and CONFIGURATION.eye_color IDs.

- [x] Write behavior tests for distinct rendered styles/colors and run RED on the original face.
- [x] Implement WFF configurations, vector pupil groups and preview support; set version 0.1.4.
- [x] Run all Python tests, schema, visual review and diff checks; expect no failures.
- [ ] Review the complete change, commit, create a draft stacked PR, and build APK in CI.
- [ ] Verify APK schema/no DEX and exact packaged definition; save and deliver APK with physical editor testing instructions.
