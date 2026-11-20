from pathlib import Path
import unittest
from tools.watchface_preview import render_preview
from tools.watchface_style_device_check import STYLES, assert_style
from tools.watchface_mood_device_check import assert_mood, pupil_widths

XML = Path('watchface/src/main/res/raw/watchface.xml')


class BatteryNativeProbeTest(unittest.TestCase):
    def test_checks_awake_and_tired_images_for_all_styles(self):
        for style in STYLES:
            awake = render_preview(XML, values={'CONFIGURATION.eye_style': style, 'BATTERY_PERCENT': 21})
            tired = render_preview(XML, values={'CONFIGURATION.eye_style': style, 'BATTERY_PERCENT': 20})
            assert_mood(awake, style, False); assert_mood(tired, style, True)
            with self.assertRaises(AssertionError): assert_mood(awake, style, True)
            with self.assertRaises(AssertionError): assert_mood(tired, style, False)

    def test_horizontal_pulse_is_visible_on_both_pupils(self):
        for style in STYLES:
            widths = [pupil_widths(render_preview(XML, values={'CONFIGURATION.eye_style': style,
                'BATTERY_CHARGING_STATUS': True, 'SECOND_MILLISECOND': seconds}))
                for seconds in (1, 2, 3, 4)]
            for eye in (0, 1): self.assertGreaterEqual(max(w[eye] for w in widths) - min(w[eye] for w in widths), 4)

    def test_normal_blink_cannot_fake_the_horizontal_pulse(self):
        for style in STYLES:
            widths = []
            for seconds in (.01, .04, .08, .12, .18, .23, 1, 2):
                image = render_preview(XML, values={'CONFIGURATION.eye_style': style, 'SECOND_MILLISECOND': seconds})
                try: assert_style(image, style)
                except AssertionError: continue
                widths.append(pupil_widths(image))
            for eye in (0, 1): self.assertLess(max(w[eye] for w in widths) - min(w[eye] for w in widths), 4)


class OverlayFocusTest(unittest.TestCase):
    def test_only_dismisses_a_focused_system_overlay_not_history_or_face_blink(self):
        from tools import watchface_mood_device_check as probe
        self.assertTrue(hasattr(probe, 'overlay_has_focus'), 'Overlay dismissal must use actual window focus, not pupil pixels')
        for activity in ('com.google.android.clockwork.sysui.experiences.charging.ChargingActivity',
                         'com.google.android.clockwork.sysui.experiences.globallauncher.AllAppsLauncherActivity'):
            self.assertTrue(probe.overlay_has_focus('mCurrentFocus=Window{123 u0 com.google.android.wearable.sysui/' + activity + '}'))
        history = 'Window{123 u0 com.google.android.wearable.sysui/com.google.android.clockwork.sysui.experiences.charging.ChargingActivity}\n'
        self.assertFalse(probe.overlay_has_focus(history + 'mCurrentFocus=Window{456 u0 com.google.android.wearable.sysui/.mainui.activity.SysUiActivity}'))
        self.assertFalse(probe.overlay_has_focus('mCurrentFocus=null'))

    def test_watchface_clock_stays_visible_through_blinks_but_system_cards_cover_it(self):
        from tools import watchface_mood_device_check as probe
        from PIL import Image, ImageDraw
        self.assertTrue(hasattr(probe, 'watchface_clock_visible'), 'Blinks must not trigger navigation; system full-screen cards must be dismissed')
        for seconds, level in [(1, 80), (.12, 80), (1, 20)]:
            picture = render_preview(XML, values={'SECOND_MILLISECOND': seconds, 'BATTERY_PERCENT': level})
            self.assertTrue(probe.watchface_clock_visible(picture))
        card = Image.new('RGB', (450, 450), 'black')
        ImageDraw.Draw(card).text((40, 110), 'Wear OS\nLow battery\nYou have 20% battery remaining', fill='white')
        self.assertFalse(probe.watchface_clock_visible(card))
