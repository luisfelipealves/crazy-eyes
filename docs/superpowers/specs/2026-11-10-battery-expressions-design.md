# Automatic battery expressions

The user selected item2 from the proposed roadmap: tired eyes at low battery, more animated eyes while charging. Use native WFF1 BATTERY_PERCENT and BATTERY_CHARGING_STATUS; no app code or permissions.

Implementation choices: at20% or below while not charging, lower the upper opening by80units with a0.35s transition. At21% or above return to the normal opening. Charging takes priority even at low battery; open the eyes and pulse both irises between88% and100% size with a3.7s period. Full/charged status reported as charging by Wear OS also uses this expression. Frames, style/iris colors and clock stay fixed. Changes apply in sensor fallback too. Ambient output remains identical.

Keep the corrected mask hierarchy: mood clipping has its own nested group, separate from tap and silhouette clipping. One mask per stage avoids sibling-mask union regressions. Put pulse scaling below the existing shake group so it does not alter the orbit pivot or gyro translation. Scaling never exceeds the original bounds.

Alternative considered: additional animated expression bitmaps or a companion service add assets/runtime state without needing them. Native transforms use the existing resource-only design and keep all four styles. No new editor setting, nighttime behavior, complications or other roadmap items.

Verify threshold20/21, charging precedence, both pupils animating, no pulse while unplugged, fallback and unchanged AOD. Native tests must actually change emulator battery level/power, observe tired/open transitions and measure horizontal iris width variation, which an ordinary vertical blink cannot fake. Test charging disconnect at20% and recovery to21% for each style. Restore80%/unplugged afterward for existing motion tests. Deliver0.1.7-experimental as a draft stacked PR and APK for physical testing; do not merge.
