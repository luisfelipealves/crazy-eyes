package com.luisfelipe.crazyeyes

import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.os.SystemClock
import android.view.MotionEvent
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode
import java.io.File

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [35])
@GraphicsMode(GraphicsMode.Mode.NATIVE)
class EyesViewTest {
    private fun view(engine: EyesEngine): EyesView =
        EyesView(RuntimeEnvironment.getApplication(), engine).apply {
            layout(0, 0, 400, 400)
            setActive(true)
        }

    private fun touch(view: EyesView, action: Int, x: Float, y: Float, time: Long) {
        val event = MotionEvent.obtain(0, time, action, x, y, 0)
        try { assertTrue(view.onTouchEvent(event)) } finally { event.recycle() }
    }

    @Test fun actualAndroidDragOutAndBackDoesNotPoke() {
        val engine = EyesEngine()
        val view = view(engine)
        touch(view, MotionEvent.ACTION_DOWN, 116f, 200f, 0)
        touch(view, MotionEvent.ACTION_MOVE, 300f, 200f, 40)
        touch(view, MotionEvent.ACTION_UP, 116f, 200f, 100)
        assertEquals(0f, engine.frame(100).left.irritation, .001f)
        view.setActive(false)
    }

    @Test fun actualAndroidTapPokesCorrectEye() {
        val engine = EyesEngine()
        val view = view(engine)
        touch(view, MotionEvent.ACTION_DOWN, 284f, 200f, 0)
        touch(view, MotionEvent.ACTION_UP, 284f, 200f, 100)
        assertTrue(engine.frame(100).right.openness < .15f)
        assertEquals(0f, engine.frame(100).left.irritation, .001f)
        view.setActive(false)
    }

    @Test fun cancelAndPauseDoNotLeaveFingerInControl() {
        val engine = EyesEngine()
        val view = view(engine)
        touch(view, MotionEvent.ACTION_DOWN, 116f, 200f, 0)
        touch(view, MotionEvent.ACTION_CANCEL, 116f, 200f, 100)
        assertEquals(InputSource.RANDOM, engine.frame(100).source)
        touch(view, MotionEvent.ACTION_DOWN, 116f, 200f, 200)
        view.setActive(false)
        assertEquals(InputSource.RANDOM, engine.frame(200).source)
    }

    @Test fun activityPauseClearsLiveGesture() {
        val controller = Robolectric.buildActivity(MainActivity::class.java).setup()
        val activity = controller.get()
        activity.onWindowFocusChanged(true)
        val view = activity.findViewById<android.view.ViewGroup>(android.R.id.content).getChildAt(0) as EyesView
        view.layout(0, 0, 400, 400)
        val time = SystemClock.uptimeMillis()
        touch(view, MotionEvent.ACTION_DOWN, 116f, 200f, time)
        assertEquals(InputSource.TOUCH, view.engine.frame(time).source)
        controller.pause()
        assertEquals(InputSource.RANDOM, view.engine.frame(time).source)
        controller.stop().destroy()
    }

    @Test fun renderEyesOnBlackAndKeepPupilsInsideTheirWhites() {
        val renderer = EyesRenderer()
        val output = File("build/reports/eyes-preview").apply { mkdirs() }
        val samples = linkedMapOf(
            "normal" to EyesFrame(EyePose(Gaze(0f, 0f)), EyePose(Gaze(0f, 0f)), InputSource.TILT),
            "tilt" to EyesFrame(EyePose(Gaze(.7f, -.7f)), EyePose(Gaze(.7f, -.7f)), InputSource.TILT),
            "follow" to EyesFrame(EyePose(Gaze(.9f, 0f)), EyePose(Gaze(-.9f, 0f)), InputSource.TOUCH),
            "poke" to EyesFrame(EyePose(Gaze(-.2f, 0f), .08f, .9f), EyePose(Gaze(.3f, 0f), 1.12f), InputSource.RANDOM)
        )
        for ((name, frame) in samples) {
            val bitmap = Bitmap.createBitmap(450, 450, Bitmap.Config.ARGB_8888)
            renderer.draw(Canvas(bitmap), frame, 450, 450)
            assertEquals(Color.BLACK, bitmap.getPixel(0, 0))
            assertEquals(Color.BLACK, bitmap.getPixel(225, 0))
            assertEquals(Color.BLACK, bitmap.getPixel(225, 225))
            assertEquals(Color.BLACK, bitmap.getPixel(50, 225))
            assertTrue("Visible sclera in $name", Color.red(bitmap.getPixel(75, 225)) > 180)
            assertTrue("Right sclera stays opaque in $name", Color.red(bitmap.getPixel(375, 225)) > 180)
            if (name == "normal") assertTrue(Color.red(bitmap.getPixel(130, 225)) < 50)
            File(output, "$name.png").outputStream().use { bitmap.compress(Bitmap.CompressFormat.PNG, 100, it) }
            bitmap.recycle()
        }
    }
}
