# Whole-eye styles correction

The user clarified that a style changes the entire eye, not only the iris/pupil. Robot eyes must be square with a robotic frame; Cat and Monster must also change the complete eye. This corrects the interpretation in the previous eye-customization spec.

Keep the existing four editor options and six iris colors. Cartoon retains the original ovals. Cat uses pointed almond openings, brown eyelids and slit pupils. Robot uses square glass openings, a beveled metal frame with corner fasteners and square optical sensors. Monster uses irregular green sockets, heavy eyelids and the existing unusual pupils. Exact palettes and silhouette geometry are implementation choices.

Use native WFF1 vector groups and masks. Frames surround black openings and sit outside the blinking/tapping panel, so they remain visible when an eye closes. A neutral rectangular animated mask replaces the old oval tap mask in the current layout; legacy resources remain for the baseline comparison. Ambient outlines match the selected full silhouette and stay below 15% lit pixels for every style. Iris colors do not recolor frames or sclera.

Preserve font40, inverted gyro, radius26/3-second opposite shake, sensorless wander, per-eye tap behavior, current package/name and Wear OS4+ compatibility. Geometry masks may naturally occlude a moving pupil at an eyelid/frame boundary. No new product features. Version0.1.5-experimental, draft stacked PR and physical testing; no merge.

Approach: extend existing native groups to style the entire socket and mask rather than adding image skins or a companion app. Local rendered regression tests must fail on0.1.4's unchanged outer shapes, then pass on complete styles. Review actual previews before building the APK; verify WFF1, every AOD variant, Android tests/lint/build and packaged no-DEX contract.
