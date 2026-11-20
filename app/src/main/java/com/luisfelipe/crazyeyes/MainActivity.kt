package com.luisfelipe.crazyeyes

import android.app.Activity
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.Bundle
import android.os.PowerManager
import android.view.WindowInsets
import android.view.WindowInsetsController

class MainActivity : Activity() {
    private lateinit var eyes: EyesView
    private lateinit var motion: MotionInput
    private var resumed = false
    private var focused = false
    private val screenState = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) { updateActivityState() }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.setDecorFitsSystemWindows(false)
        eyes = EyesView(this)
        setContentView(eyes)
        motion = MotionInput(this, { display?.rotation ?: 0 }, eyes.engine::setTilt)
        registerReceiver(screenState, IntentFilter().apply {
            addAction(Intent.ACTION_SCREEN_OFF)
            addAction(Intent.ACTION_SCREEN_ON)
        }, RECEIVER_NOT_EXPORTED)
        hideSystemBars()
    }

    override fun onResume() {
        super.onResume()
        resumed = true
        updateActivityState()
    }

    override fun onPause() {
        resumed = false
        updateActivityState()
        super.onPause()
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        focused = hasFocus
        if (::eyes.isInitialized) updateActivityState()
        if (hasFocus) hideSystemBars()
    }

    private fun updateActivityState() {
        val awake = getSystemService(PowerManager::class.java)?.isInteractive == true
        val active = resumed && focused && awake
        eyes.setActive(active)
        if (active) motion.start() else motion.stop()
    }

    private fun hideSystemBars() {
        window.insetsController?.apply {
            hide(WindowInsets.Type.systemBars())
            systemBarsBehavior = WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        }
    }

    override fun onDestroy() {
        motion.stop()
        eyes.setActive(false)
        unregisterReceiver(screenState)
        super.onDestroy()
    }
}
