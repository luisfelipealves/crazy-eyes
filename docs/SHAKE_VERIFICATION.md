# Shake experiment verification

## Result

The Wear OS 4 renderer displayed the experimental WFF face, accepted injected acceleration, and produced opposite pupil orbits after release in two independent trials. The pupils returned to their neutral gaze and stayed there across several later captures. The unchanged baseline XML passed the same calibrated sensor control without producing an after-release orbit.

Evidence: GitHub Actions run [41081193667](https://github.com/luisfelipealves/crazy-eyes/actions/runs/41081193667), artifact `watchface-device-evidence` (ID 12989947027), including screenshots, calibration, measurements and logcat. The APK used by that run is the deliverable; no subsequent change modifies its resources.

## Timing correction

The initial native assertion failed because it timestamped captures after PNG transfer and pixel analysis. These operations sometimes took nearly a second, leaving only two frames in the checker's active time window even though the image sequence showed the full orbit. The harness now timestamps the request before capture and separately retains completion time.

The recorded native images were re-read and their pixel centroids checked against the original measurements. Both complete nine-image sequences were then replayed through the same direction, phase and recovery assertions using conservative request-time lower bounds: each request happens no earlier than its scheduled delay or completion of the preceding capture and analysis. No images or pupil positions were generated or changed.

| Trial | First three capture request lower bounds after release | Recovery |
| --- | --- | --- |
| 0 | 0.300s, 1.298s, 2.247s | Neutral from the capture requested after 3.031s, then several later neutral captures |
| 1 | 0.300s, 1.147s, 1.910s | Within 3 units of neutral in captures requested after 3.816s and later |

Both replayed trials passed. This supports a roughly three-second effect, not millisecond-accurate duration measurement. The original workflow run remains red from the timestamp assertion; the harness correction is committed and rerun by CI.

## Other validation

- 14 Python tests passed, including negative controls for brief twitch, continuous motion, reversed directions and disconnected sensor injection.
- WFF 1 schema and resource references passed; APK has no DEX or native executable code.
- Build, lint and the unchanged app's 19 unit tests passed in the same CI run.
- Independent review found two important evidence gaps; negative fixtures reproduced both and the checker was strengthened before the native run.
- The curved clock, tap masks and static AOD passed existing layout tests.

## Physical test still required

The separate face is **Crazy Eyes Shake**, package `com.luisfelipe.crazyeyes.watchface.shake`. On the real watch, verify shake sensitivity with the screen active, repeat activation, tap while spinning, AOD/resume and battery. The trigger is acceleration magnitude above 25 m/s², not recognition of a multi-pulse gesture. An impact or other strong movement can also trigger it. No merge is authorized by this verification.
