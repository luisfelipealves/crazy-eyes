package com.luisfelipe.crazyeyes

import android.graphics.Canvas
import android.graphics.Color
import android.graphics.LinearGradient
import android.graphics.Paint
import android.graphics.Path
import android.graphics.RectF
import android.graphics.Shader
import kotlin.math.min

/** Canvas-only renderer shared by the watch View and visual verification. */
class EyesRenderer {
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val clip = Path()
    private val bounds = RectF()

    fun draw(canvas: Canvas, frame: EyesFrame, width: Int, height: Int) {
        canvas.drawColor(Color.BLACK)
        val size = min(width, height).toFloat()
        if (size <= 0f) return
        val save = canvas.save()
        canvas.translate((width - size) / 2f, (height - size) / 2f)
        eye(canvas, frame.left, EyeGeometry.LEFT_X * size, size)
        eye(canvas, frame.right, EyeGeometry.RIGHT_X * size, size)
        canvas.restoreToCount(save)
    }

    private fun eye(canvas: Canvas, pose: EyePose, centerX: Float, size: Float) {
        val centerY = EyeGeometry.Y * size
        val rx = EyeGeometry.RADIUS_X * size
        val ry = EyeGeometry.RADIUS_Y * size * pose.openness
        bounds.set(centerX - rx, centerY - ry, centerX + rx, centerY + ry)
        val pink = pose.irritation.coerceIn(0f, 1f)
        val top = Color.rgb(255, (255 - pink * 42).toInt(), (255 - pink * 32).toInt())
        val bottom = Color.rgb(222, (231 - pink * 38).toInt(), (240 - pink * 30).toInt())
        paint.alpha = 255
        paint.shader = LinearGradient(centerX, bounds.top, centerX + rx, bounds.bottom,
            top, bottom, Shader.TileMode.CLAMP)
        canvas.drawOval(bounds, paint)
        paint.shader = null

        val save = canvas.save()
        clip.reset()
        clip.addOval(bounds, Path.Direction.CW)
        canvas.clipPath(clip)
        val radius = size * .079f * (1f - .2f * pink)
        val pupilX = centerX + pose.gaze.x * (rx - radius - size * .012f)
        val pupilY = centerY + pose.gaze.y * (EyeGeometry.RADIUS_Y * size - radius - size * .016f)
        paint.color = Color.rgb(44, 51, 63)
        canvas.drawCircle(pupilX, pupilY, radius, paint)
        paint.color = Color.rgb(6, 8, 13)
        canvas.drawCircle(pupilX, pupilY, radius * .77f, paint)
        paint.color = Color.WHITE
        canvas.drawCircle(pupilX - radius * .27f, pupilY - radius * .31f, radius * .17f, paint)
        paint.color = Color.argb(160, 255, 255, 255)
        canvas.drawCircle(pupilX + radius * .28f, pupilY + radius * .29f, radius * .075f, paint)
        canvas.restoreToCount(save)
    }
}
