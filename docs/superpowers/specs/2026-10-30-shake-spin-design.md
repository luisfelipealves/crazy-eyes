# Shake spin experiment

The user requested that shaking the wrist makes the pupils orbit in opposite directions and continue for a few seconds after the motion ends. Use approximately 3 seconds, then restore normal tilt. Retain the curved time above the eyes, tap masks, no-sensor fallback and ambient behavior.

## Approaches

- A conditional animated image would disappear as soon as its acceleration condition becomes false; it cannot by itself retain the effect after release.
- A native sensor timer would implement this directly in the standalone app, but that would not add the requested behavior to the WFF watch face.
- Experimental WFF angular interpolation can retain motion during a transition. A tiny directed rotation while acceleration exceeds a threshold, followed by a directed return to zero, should travel the remaining full orbit over 3 seconds. This is a hypothesis to verify in the actual Wear OS renderer, not a supported shake event or a timer.

Proceed with the third approach in an isolated test face. Detect total acceleration greater than 25 m/s² (gravity alone is about 9.8); clockwise on the left, counterclockwise on the right, EASE_OUT duration 3 seconds, no repeats. Use a 14-unit eccentric pivot so even pupils at rest visibly orbit. Keep the existing parent-scoped eye masks. Motion sensing remains interactive-only. Install the experiment under a separate package and label so the working face remains available.

## Evidence required

An emulator check must first show the existing face has no motion after a brief injected acceleration ends, then show opposite pupil displacements after release and return to baseline after approximately 3 seconds. This tests the WFF renderer rather than a Python imitation of its animation. Schema and static preview checks remain useful but cannot establish the temporal behavior. Do not claim success or deliver the experiment as working if the device check fails. Real wrist sensitivity and battery still need physical testing.
