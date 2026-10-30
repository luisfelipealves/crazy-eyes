package com.luisfelipe.crazyeyes

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.SystemClock
import android.view.Surface

/** Resource ownership is explicit: register only while the Activity is visible and focused. */
class MotionInput(
    context: Context,
    private val rotation: () -> Int,
    private val onTilt: (Float, Float, Long) -> Unit
) : SensorEventListener {
    private val manager = context.getSystemService(SensorManager::class.java)
    private var registered = false
    private var initialized = false
    private var smoothX = 0f
    private var smoothY = 0f

    fun start() {
        if (registered) return
        initialized = false
        val sensors = listOf(Sensor.TYPE_GRAVITY, Sensor.TYPE_ACCELEROMETER)
        for (type in sensors) {
            val sensor = manager?.getDefaultSensor(type) ?: continue
            try {
                if (manager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_GAME)) {
                    registered = true
                    return
                }
            } catch (_: SecurityException) {
                // Sensor policies can disable access; the engine already falls back to random gaze.
            }
        }
    }

    fun stop() {
        manager?.unregisterListener(this)
        registered = false
        initialized = false
    }

    override fun onSensorChanged(event: SensorEvent) {
        if (!registered || event.values.size < 2) return
        val x = event.values[0]
        val y = event.values[1]
        if (!x.isFinite() || !y.isFinite()) return
        val amount = if (!initialized) 1f else .18f
        smoothX += (x - smoothX) * amount
        smoothY += (y - smoothY) * amount
        initialized = true
        val degrees = when (rotation()) {
            Surface.ROTATION_90 -> 90
            Surface.ROTATION_180 -> 180
            Surface.ROTATION_270 -> 270
            else -> 0
        }
        val gaze = TiltMapping.fromGravity(smoothX, smoothY, degrees)
        onTilt(gaze.x, gaze.y, SystemClock.uptimeMillis())
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) = Unit
}
