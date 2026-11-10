# Rectangle overlay: mask composition fix

User reports a rectangle covering each eye; tapping/blinking exposes the correct design underneath. The stored0.1.5 native screenshot confirms rectangular sclera even in Cartoon. Root cause: WFF sibling masks are combined as a union, whereas the local preview incorrectly multiplied them as intersections. The full rectangular tap thumbnail therefore expands the sibling silhouette mask. Schema validation cannot detect this semantic mistake.

Fix: keep the selected silhouette as the outer lid's only mask and move backgrounds, pupil motion and the animated tap mask into a nested content group. The two clipping stages now intersect through their parent hierarchy. Correct preview semantics to union sibling masks. Preserve style IDs, editor settings, visual designs, frames, all motion/timing and AOD.

Verification must cover the real renderer: keep the captured0.1.5 image as a negative fixture, add independent native pixel probes, and build four test variants changing only the default style. A fresh install of each variant must show the complete matching silhouette without a rectangle on both eyes, in consecutive passing captures spanning at least0.7s (longer than the0.24s periodic blink), resetting after any failed frame. Run these checks before the older motion timing check so its capture-latency flakiness cannot hide a style failure. This tests initial native rendering; editor switching/persistence remains physical testing.

Alternative rejected: rewrite configuration IDs/selection before proving a configuration defect. The correct design is already visible under the overlay, and the observed native mask composition explains the rectangle. Version0.1.6-experimental; draft PR; no merge.
