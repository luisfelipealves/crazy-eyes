# Visible intensity options and faster Crazy mode

User reports missing option names in the animation-intensity selector and asks for faster movement in the intense mode. Ship0.1.10-experimental/code11, Wear OS4+/WFF1/resource-only. Preserve configuration IDs/defaults, four whole-eye styles/colors, clock, masks, battery expressions, tap/blink and AOD. No merge.

## Labels
The WFF displayName/screenReaderText resources are present in English and pt-BR. List options lack icons; the physical Samsung editor does not show their text. Add monochrome transparent400px PNG option icons with baked-in captions Calm/Crazy and Tranquilo/Maluco, preserving accessible labels. Generic Portuguese resources cover pt-PT and pt-BR. Native editor capture plus packaged/local image inspection verifies the artifacts; Samsung presentation remains physical testing.

Approach: captioned icons work in image-based editors and survive icon tinting. Text resources alone already exist and are insufficient on the reported editor. A custom companion editor would add runtime/platform complexity and is unnecessary.

## Speed
Crazy follows tilt50% more sensitively (26/40px travel saturates at30° instead of45°), looks randomly every1s rather than2s, and completes its shake orbit in2s instead of3s. Calm keeps45° sensitivity,2s fallback and3s orbit, with existing13/20 travel and13px radius. Crazy retains26/40 travel and26px radius. OFF gates both rotation controllers while preserving tilt.

One shared graphic subtree sits in two concentric static-pivot controllers: outer Crazy2s, inner Calm3s. Only the selected mode can trigger a controller. This avoids unsupported expression-valued Animation duration and duplicates no style assets. Both controllers use padded152px canvases and static center pivots76px. Parent y41/54 and pupil x40,y27/14 retain the proven world pivots(77,117)/(77,130), neutral center(77,104) and72px pupil size, avoiding clipping of a rotating inner controller.

## Verification
Tests cover resource/icon visibility contracts/locales/tint-safe caption ink, low-angle tilt gain and clamping,1s/2s fallback cadence, exclusive controller trigger/OFF, unchanged neutral/tap/battery/AOD and2s/3s native validator boundaries. Native probes measure low-angle tilt19.5px Crazy versus6.5px Calm, opposite full orbit and settling for each duration, and OFF. Align probe shocks away from periodic blink so temporal samples remain valid. Native editor probe captures UI hierarchy/screens and checks both option names, followed by visual inspection.
