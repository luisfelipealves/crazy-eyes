from pathlib import Path
import unittest
from PIL import ImageChops
from tools.watchface_preview import render_preview

XML = Path('watchface/src/main/res/raw/watchface.xml')
STYLES = ('cartoon', 'cat', 'robot', 'monster')


def view(style, battery, charging=False, seconds=1, **extra):
    return render_preview(XML, values={'CONFIGURATION.eye_style': style,
        'BATTERY_PERCENT': battery, 'BATTERY_CHARGING_STATUS': charging,
        'SECOND_MILLISECOND': seconds, **extra})


class BatteryExpressionTest(unittest.TestCase):
    def test_twenty_percent_closes_upper_lids_but_twenty_one_is_awake(self):
        for style in STYLES:
            with self.subTest(style=style):
                awake, tired = view(style, 21), view(style, 20)
                for x in (130, 319):
                    self.assertGreater(min(awake.getpixel((x, 182))), 150)
                    self.assertEqual(tired.getpixel((x, 182)), (0, 0, 0))
                    self.assertGreater(min(tired.getpixel((x, 272))), 150)
                self.assertIsNone(ImageChops.difference(awake, tired).crop((0, 0, 450, 85)).getbbox())

    def test_charging_wakes_low_battery_eyes_and_animates_both_pupils(self):
        for style in STYLES:
            with self.subTest(style=style):
                a, b = view(style, 5, True, 1), view(style, 5, True, 2)
                for x in (130, 319):
                    self.assertGreater(min(a.getpixel((x, 182))), 150)
                    self.assertIsNotNone(ImageChops.difference(a, b).crop((x-45, 180, x+45, 275)).getbbox())
                self.assertIsNone(ImageChops.difference(a, b).crop((0, 0, 450, 85)).getbbox())

    def test_unplugged_pupils_do_not_pulse(self):
        self.assertIsNone(ImageChops.difference(view('cartoon', 80, False, 1), view('cartoon', 80, False, 2)).getbbox())

    def test_moods_work_without_sensor_and_do_not_affect_ambient(self):
        for style in STYLES:
            tired = view(style, 15, ACCELEROMETER_IS_SUPPORTED=False)
            self.assertEqual(tired.getpixel((130, 182)), (0, 0, 0))
            charging_a = view(style, 15, True, 1, ACCELEROMETER_IS_SUPPORTED=False)
            charging_b = view(style, 15, True, 2, ACCELEROMETER_IS_SUPPORTED=False)
            self.assertIsNotNone(ImageChops.difference(charging_a, charging_b).getbbox())
            ambient = render_preview(XML, ambient=True, values={'CONFIGURATION.eye_style': style})
            for battery, charging in ((15, False), (15, True), (100, True)):
                state = render_preview(XML, ambient=True, values={'CONFIGURATION.eye_style': style,
                    'BATTERY_PERCENT': battery, 'BATTERY_CHARGING_STATUS': charging})
                self.assertIsNone(ImageChops.difference(ambient, state).getbbox())
