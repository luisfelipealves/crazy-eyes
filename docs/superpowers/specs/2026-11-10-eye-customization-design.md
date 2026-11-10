# Eye customization

The user approved implementing item 1 (eye colors and styles) for physical testing. Scope: native watch-face editor with four styles (Cartoon, Cat, Robot, Little monster) and six iris colors (Gray, Blue, Green, Brown, Purple, Amber). These counts and palettes are implementation choices. Default Cartoon/Gray retains the original appearance.

Use WFF1 UserConfigurations, ListConfiguration and ColorConfiguration, with vector PartDraw pupils. The existing moving PartImage becomes a Group so the complete selected pupil follows the unchanged gyro and shake transforms. Sensorless wander uses the same designs. Enable Editable. Labels use English fallback and Brazilian Portuguese resources.

Alternatives considered: pre-rendered color/style images increase assets and duplicate palettes; a companion app adds installation and synchronization work. Native editor and vector shapes fit the existing resource-only face and make colors independent of pupil shape.

Keep Wear OS 4+, current package/name, font 40, inverted gyro, radius-26 opposite shake, per-eye tap masks, and existing AOD outlines. No automatic expressions, motion settings, date settings or complications in this increment. Native editor persistence is managed by Wear OS and requires physical testing.

Validate all 24 combinations, mask/fallback/AOD behavior, WFF1 schema, Android build/lint/tests, resource-only APK, and manual visual previews. Deliver 0.1.4-experimental APK through a draft stacked PR; do not merge before user testing.
