package com.luisfelipe.crazyeyes

import android.content.Context
import android.graphics.Canvas
import android.os.SystemClock
import android.view.HapticFeedbackConstants
import android.view.MotionEvent
import android.view.View
import android.view.ViewConfiguration
import kotlin.math.min

class EyesView(context: Context, internal val engine: EyesEngine = EyesEngine()) : View(context) {
    private val renderer = EyesRenderer()
    private val touchSlop = ViewConfiguration.get(context).scaledTouchSlop
    private var active = false
    private var multiplePointers = false
    private val redraw = object : Runnable {
        override fun run() {
            if (!active) return
            invalidate()
            postDelayed(this, 33L)
        }
    }

    init {
        isClickable = true
        isFocusable = true
        contentDescription = context.getString(R.string.eyes_description)
        setBackgroundColor(android.graphics.Color.BLACK)
    }

    fun setActive(value: Boolean) {
        if (active == value) return
        active = value
        removeCallbacks(redraw)
        if (value) post(redraw) else {
            multiplePointers = false
            engine.resetInput()
        }
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        renderer.draw(canvas, engine.frame(SystemClock.uptimeMillis()), width, height)
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        if (!active || width == 0 || height == 0) return true
        val size = min(width, height).toFloat()
        val offsetX = (width - size) / 2f
        val offsetY = (height - size) / 2f
        val x = (event.x - offsetX) / size
        val y = (event.y - offsetY) / size
        when (event.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                multiplePointers = false
                engine.pointerDown(x, y, event.eventTime)
                parent?.requestDisallowInterceptTouchEvent(true)
            }
            MotionEvent.ACTION_POINTER_DOWN -> {
                multiplePointers = true
                engine.cancelTouch()
            }
            MotionEvent.ACTION_MOVE, MotionEvent.ACTION_UP -> {
                if (!multiplePointers) {
                    for (i in 0 until event.historySize) {
                        engine.pointerMove((event.getHistoricalX(i) - offsetX) / size,
                            (event.getHistoricalY(i) - offsetY) / size)
                    }
                    if (event.actionMasked == MotionEvent.ACTION_MOVE) engine.pointerMove(x, y)
                    else if (engine.pointerUp(x, y, event.eventTime, touchSlop / size)) {
                        performClick()
                        performHapticFeedback(HapticFeedbackConstants.CONFIRM)
                    }
                }
                if (event.actionMasked == MotionEvent.ACTION_UP) {
                    engine.cancelTouch()
                    multiplePointers = false
                    parent?.requestDisallowInterceptTouchEvent(false)
                }
            }
            MotionEvent.ACTION_CANCEL -> {
                engine.cancelTouch()
                multiplePointers = false
                parent?.requestDisallowInterceptTouchEvent(false)
            }
        }
        invalidate()
        return true
    }

    override fun performClick(): Boolean = super.performClick()

    override fun onDetachedFromWindow() {
        setActive(false)
        super.onDetachedFromWindow()
    }
}
