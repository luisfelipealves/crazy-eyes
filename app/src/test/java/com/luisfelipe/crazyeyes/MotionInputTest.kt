package com.luisfelipe.crazyeyes

import android.hardware.Sensor
import android.hardware.SensorManager
import android.os.SystemClock
import android.view.Surface
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.Shadows.shadowOf
import org.robolectric.annotation.Config
import org.robolectric.shadows.ShadowSensor
import org.robolectric.shadows.ShadowSensorManager

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
class MotionInputTest {
    @Test fun accelerometerFallbackDeliversTiltAndStopReleasesListener() {
        val context = RuntimeEnvironment.getApplication()
        val manager = context.getSystemService(SensorManager::class.java)
        val shadow = shadowOf(manager)
        shadow.addSensor(ShadowSensor.newInstance(Sensor.TYPE_ACCELEROMETER))
        val engine = EyesEngine()
        val input = MotionInput(context, { Surface.ROTATION_180 }, engine::setTilt)
        input.start()
        val sample = ShadowSensorManager.createSensorEvent(3, Sensor.TYPE_ACCELEROMETER)
        sample.values[0] = 9.81f
        shadow.sendSensorEventToListeners(sample)
        val frame = engine.frame(SystemClock.uptimeMillis())
        assertEquals(InputSource.TILT, frame.source)
        assertTrue(frame.left.gaze.x < -.9f)
        input.stop()
        assertFalse(shadow.hasListener(input))
    }

    @Test fun failedRegistrationLeavesEyesInRandomMode() {
        val context = RuntimeEnvironment.getApplication()
        val shadow = shadowOf(context.getSystemService(SensorManager::class.java))
        shadow.addSensor(ShadowSensor.newInstance(Sensor.TYPE_ACCELEROMETER))
        shadow.setForceListenersToFail(true)
        val engine = EyesEngine()
        val input = MotionInput(context, { Surface.ROTATION_0 }, engine::setTilt)
        input.start()
        assertEquals(InputSource.RANDOM, engine.frame(SystemClock.uptimeMillis()).source)
        input.stop()
        assertFalse(shadow.hasListener(input))
    }
}
