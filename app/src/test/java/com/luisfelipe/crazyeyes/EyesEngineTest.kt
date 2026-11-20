package com.luisfelipe.crazyeyes

import kotlin.math.hypot
import kotlin.random.Random
import org.junit.Assert.*
import org.junit.Test

class EyesEngineTest {
    private fun engine() = EyesEngine(Random(42))

    @Test fun freshTiltControlsBothEyes() {
        val e = engine()
        e.setTilt(.8f, -.3f, 0)
        val f = e.frame(600)
        assertEquals(InputSource.TILT, f.source)
        assertTrue(f.left.gaze.x > .6f)
        assertTrue(f.right.gaze.y < -.2f)
    }

    @Test fun fingerOverridesTiltAndEyesConvergeOnIt() {
        val e = engine()
        e.setTilt(-1f, -1f, 0)
        e.pointerDown(.5f, .5f, 0)
        val f = e.frame(600)
        assertEquals(InputSource.TOUCH, f.source)
        assertTrue(f.left.gaze.x > .5f)
        assertTrue(f.right.gaze.x < -.5f)
    }

    @Test fun sensorWithoutEventsUsesRandomGazeAndKeepsChanging() {
        val e = engine()
        val frames = (0L..12000L step 500).map { e.frame(it) }
        assertTrue(frames.all { it.source == InputSource.RANDOM })
        assertTrue(frames.map { it.left.gaze }.distinct().size > 3)
        assertTrue(frames.all { hypot(it.left.gaze.x, it.left.gaze.y) <= 1.001f })
    }

    @Test fun staleSensorFallsBackAndRecoversOnNextSample() {
        val e = engine()
        e.setTilt(.6f, 0f, 100)
        assertEquals(InputSource.TILT, e.frame(2099).source)
        assertEquals(InputSource.RANDOM, e.frame(2100).source)
        e.setTilt(-.6f, 0f, 2200)
        assertEquals(InputSource.TILT, e.frame(2200).source)
    }

    @Test fun invalidSampleDoesNotDisableRandomFallback() {
        val e = engine()
        e.setTilt(Float.NaN, 0f, 0)
        assertEquals(InputSource.RANDOM, e.frame(50).source)
    }

    @Test fun quickTapSquintsHitEyeThenRecovers() {
        val e = engine()
        e.pointerDown(.29f, .5f, 0)
        assertTrue(e.pointerUp(.29f, .5f, 100, .03f))
        val f = e.frame(100)
        assertTrue(f.left.openness < .15f)
        assertTrue(f.right.openness > 1f)
        assertEquals(0f, e.frame(1001).left.irritation, .001f)
        assertEquals(1f, e.frame(1001).left.openness, .001f)
    }

    @Test fun dragOutAndBackIsNeverAPoke() {
        val e = engine()
        e.pointerDown(.29f, .5f, 0)
        e.pointerMove(.8f, .5f)
        e.pointerMove(.29f, .5f)
        assertFalse(e.pointerUp(.29f, .5f, 100, .03f))
        assertEquals(0f, e.frame(100).left.irritation, .001f)
    }

    @Test fun longHoldFollowsFingerWithoutPoking() {
        val e = engine()
        e.pointerDown(.29f, .5f, 0)
        assertFalse(e.pointerUp(.29f, .5f, 600, .03f))
    }

    @Test fun cancelledGestureNeverPokesAndReleasesGaze() {
        val e = engine()
        e.pointerDown(.29f, .5f, 0)
        e.cancelTouch()
        assertFalse(e.pointerUp(.29f, .5f, 100, .03f))
        assertEquals(InputSource.RANDOM, e.frame(100).source)
    }

    @Test fun resetClearsTouchesAndOldSensorData() {
        val e = engine()
        e.setTilt(.5f, .5f, 0)
        e.pointerDown(.2f, .2f, 10)
        e.resetInput()
        assertEquals(InputSource.RANDOM, e.frame(20).source)
    }

    @Test fun hugeSensorAndOffscreenFingerCannotPushPupilsOutsideEye() {
        val e = engine()
        e.setTilt(200f, -200f, 0)
        assertTrue(hypot(e.frame(500).left.gaze.x, e.frame(500).left.gaze.y) <= 1.001f)
        e.pointerDown(30f, -30f, 600)
        assertTrue(hypot(e.frame(1100).left.gaze.x, e.frame(1100).left.gaze.y) <= 1.001f)
    }

    @Test fun gravityMapsToScreenRotation() {
        val expected = listOf(
            Triple(0, 1f, 0f), Triple(90, 0f, 1f),
            Triple(180, -1f, 0f), Triple(270, 0f, -1f)
        )
        for ((rotation, x, y) in expected) {
            val mapped = TiltMapping.fromGravity(9.81f, 0f, rotation)
            assertEquals(x, mapped.x, .001f)
            assertEquals(y, mapped.y, .001f)
        }
    }
}
