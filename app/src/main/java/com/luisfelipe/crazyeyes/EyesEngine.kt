package com.luisfelipe.crazyeyes

import kotlin.math.exp
import kotlin.math.hypot
import kotlin.math.sin
import kotlin.random.Random

data class Gaze(val x: Float, val y: Float) {
    fun bounded(): Gaze {
        val length = hypot(x, y)
        return if (length > 1f) Gaze(x / length, y / length) else this
    }
}

enum class InputSource { TOUCH, TILT, RANDOM }
data class EyePose(val gaze: Gaze, val openness: Float = 1f, val irritation: Float = 0f)
data class EyesFrame(val left: EyePose, val right: EyePose, val source: InputSource)

/** Shared geometry keeps rendering, hit testing and finger convergence in agreement. */
object EyeGeometry {
    const val LEFT_X = .29f
    const val RIGHT_X = .71f
    const val Y = .50f
    const val RADIUS_X = .17f
    const val RADIUS_Y = .23f

    fun hit(x: Float, y: Float): Int? {
        for ((index, center) in listOf(LEFT_X, RIGHT_X).withIndex()) {
            val dx = (x - center) / RADIUS_X
            val dy = (y - Y) / RADIUS_Y
            if (dx * dx + dy * dy <= 1f) return index
        }
        return null
    }
}

object TiltMapping {
    fun fromGravity(x: Float, y: Float, rotationDegrees: Int): Gaze {
        val gx = x / 9.81f
        val gy = y / 9.81f
        return when (rotationDegrees) {
            90 -> Gaze(gy, gx)
            180 -> Gaze(-gx, gy)
            270 -> Gaze(-gy, -gx)
            else -> Gaze(gx, -gy)
        }.bounded()
    }
}

/** Pure state machine: all times are monotonic milliseconds, positions normalized to the square. */
class EyesEngine(private val random: Random = Random.Default) {
    private var tilt: Gaze? = null
    private var tiltAt = Long.MIN_VALUE
    private var finger: Gaze? = null
    private var down: Gaze? = null
    private var downAt = 0L
    private var maxTravel = 0f
    private var leftGaze = Gaze(0f, 0f)
    private var rightGaze = Gaze(0f, 0f)
    private var lastFrame: Long? = null
    private var randomTarget = Gaze(0f, 0f)
    private var nextLook = 0L
    private var nextBlink = 3500L
    private var blinkAt: Long? = null
    private var pokeAt: Long? = null
    private var pokedEye: Int? = null

    fun setTilt(x: Float, y: Float, nowMs: Long) {
        if (!x.isFinite() || !y.isFinite()) return
        tilt = Gaze(x, y).bounded()
        tiltAt = nowMs
    }

    fun pointerDown(x: Float, y: Float, nowMs: Long) {
        finger = Gaze(x, y)
        down = finger
        downAt = nowMs
        maxTravel = 0f
    }

    fun pointerMove(x: Float, y: Float) {
        val start = down ?: return
        finger = Gaze(x, y)
        maxTravel = maxOf(maxTravel, hypot(x - start.x, y - start.y))
    }

    /** Returns true only for a short stationary tap, to request system haptics. */
    fun pointerUp(x: Float, y: Float, nowMs: Long, touchSlop: Float): Boolean {
        if (down == null) return false
        pointerMove(x, y)
        val isTap = nowMs - downAt in 0L..250L && maxTravel <= touchSlop
        cancelTouch()
        if (isTap) {
            val hit = EyeGeometry.hit(x, y)
            if (hit != null) {
                pokedEye = hit
                pokeAt = nowMs
            } else {
                blinkAt = nowMs
            }
        }
        return isTap
    }

    fun cancelTouch() {
        finger = null
        down = null
        maxTravel = 0f
    }

    fun resetInput() {
        cancelTouch()
        tilt = null
        tiltAt = Long.MIN_VALUE
        lastFrame = null
        pokeAt = null
        blinkAt = null
        nextLook = 0L
        nextBlink = 0L
    }

    fun frame(nowMs: Long): EyesFrame {
        val touch = finger
        val recentTilt = tilt?.takeIf { nowMs >= tiltAt && nowMs - tiltAt < 2000L }
        val source = when {
            touch != null -> InputSource.TOUCH
            recentTilt != null -> InputSource.TILT
            else -> InputSource.RANDOM
        }
        if (source == InputSource.RANDOM && nowMs >= nextLook) {
            randomTarget = Gaze(random.nextFloat() * 1.8f - .9f, random.nextFloat() * 1.4f - .7f).bounded()
            nextLook = nowMs + random.nextLong(900L, 2400L)
        }
        val base = recentTilt ?: randomTarget
        fun target(centerX: Float): Gaze = if (touch == null) base else
            Gaze((touch.x - centerX) / .25f, (touch.y - EyeGeometry.Y) / .30f).bounded()

        // Frame-independent exponential easing; never snap after releasing the finger.
        val elapsed = (lastFrame?.let { nowMs - it } ?: 500L).coerceIn(0L, 500L)
        lastFrame = nowMs
        val amount = (1.0 - exp(-elapsed / 85.0)).toFloat()
        fun smooth(old: Gaze, goal: Gaze) = Gaze(
            old.x + (goal.x - old.x) * amount,
            old.y + (goal.y - old.y) * amount
        ).bounded()
        leftGaze = smooth(leftGaze, target(EyeGeometry.LEFT_X))
        rightGaze = smooth(rightGaze, target(EyeGeometry.RIGHT_X))

        if (nextBlink == 0L) nextBlink = nowMs + random.nextLong(3000L, 6500L)
        if (nowMs >= nextBlink) {
            blinkAt = nowMs
            nextBlink = nowMs + random.nextLong(3000L, 6500L)
        }
        val blinkAge = blinkAt?.let { nowMs - it }
        val blink = if (blinkAge != null && blinkAge in 0L..180L)
            1f - .96f * sin(Math.PI * blinkAge / 180.0).toFloat() else 1f
        val pokeAge = pokeAt?.let { nowMs - it }
        val strength = if (pokeAge != null && pokeAge in 0L until 900L) 1f - pokeAge / 900f else 0f
        fun pose(index: Int, gaze: Gaze): EyePose {
            if (strength <= 0f) return EyePose(gaze, blink)
            return if (index == pokedEye) {
                val age = pokeAge ?: 900L
                val openness = if (age < 130L) .06f else
                    (.06f + .94f * ((age - 130f) / 770f)).coerceIn(.06f, 1f)
                EyePose(gaze, minOf(openness, blink), strength)
            } else EyePose(gaze, blink * (1f + .12f * strength))
        }
        return EyesFrame(pose(0, leftGaze), pose(1, rightGaze), source)
    }
}
