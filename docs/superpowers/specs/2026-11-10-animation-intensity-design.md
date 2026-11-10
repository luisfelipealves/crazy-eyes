# Animation intensity design

User selected roadmap item3: Calm/Crazy modes and an independent shake switch. Build on0.1.7 in native WFF1, preserve Wear OS4+, package, four complete styles/six colors, clock40, inverted axes, battery expressions, tap/blink/AOD. Default Crazy + shake ON preserves the current behavior. No merge; deliver0.1.8 experimental for physical testing.

## Behavior and approach
Native editor ListConfiguration animation_intensity: calm/crazy (defaultcrazy); BooleanConfiguration shake_enabled (defaultTRUE). English and pt-BR labels. Calm halves tilt26/40→13/20, random fallback26/40→13/20 and shake orbit26→13px. Shake retains opposite directions, threshold25m/s² and3s decay. Static pupil size/neutral gaze remain identical. OFF only suppresses shake trigger, not tilt/fallback/tap/blink/charging. Battery pulse remains as in0.1.7 including its documented minute-boundary polish issue.

Use configuration expressions in existing transforms and a transformable pivotY (49/72 vs62/72), avoiding duplicated style graphics. Alternative: duplicate complete motion subtrees per mode; rejected because it multiplies style/mask maintenance. No companion service/app required.

Official references: https://developer.android.com/training/wearables/wff/personalization/user-configurations and https://developer.android.com/reference/wear-os/wff/group/group (pivotY is transformable).

## Verification
Tests prove config defaults/labels, both axes/eyes amplitude, reduced geometric orbit with unchanged neutral size, shake suppression in both modes, fallback and unchanged battery/tap/AOD. Native Wear OS checks existing four styles/moods/Crazy orbit plus Calm13px orbit and shakeOFF with low-g tilt calibration. Fixtures change only config defaults; productAPK retains defaults. Physical editor selection/persistence remains user testing.
