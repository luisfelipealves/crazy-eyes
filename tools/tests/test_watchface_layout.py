from pathlib import Path
import unittest
from PIL import ImageChops
from tools.watchface_preview import render_preview

XML = Path('watchface/src/main/res/raw/watchface.xml')


class WatchfaceLayoutTest(unittest.TestCase):
    def test_time_remains_visible_above_eyes_in_ambient(self):
        ambient = render_preview(XML, ambient=True)
        self.assertIsNotNone(ambient.crop((100, 0, 350, 85)).getbbox())
        self.assertEqual(ambient.getpixel((130, 225)), (0, 0, 0))

    def test_ambient_with_time_illuminates_less_than_fifteen_percent(self):
        ambient = render_preview(XML, ambient=True)
        self.assertLess(sum(ambient.convert('L').histogram()[1:]) / (450 * 450), .15)

    def test_tap_mask_closes_only_the_hit_eye_without_exposing_pupil(self):
        normal = render_preview(XML)
        poked = render_preview(XML, poke=('left_poke', 0))
        self.assertGreater(normal.getpixel((100, 150))[0], 180)
        self.assertEqual(poked.getpixel((100, 150)), (0, 0, 0))
        self.assertIsNone(ImageChops.difference(normal.crop((240, 120, 400, 335)),
                                               poked.crop((240, 120, 400, 335))).getbbox())

    def test_missing_sensor_uses_the_selected_gaze_cadence(self):
        for mode,interval in [('calm',2),('crazy',1)]:
            values = {'ACCELEROMETER_IS_SUPPORTED':False,'CONFIGURATION.animation_intensity':mode}
            a=render_preview(XML,values=values | {'SECONDS_IN_DAY':10})
            b=render_preview(XML,values=values | {'SECONDS_IN_DAY':10+interval/2})
            c=render_preview(XML,values=values | {'SECONDS_IN_DAY':10+interval})
            self.assertIsNone(ImageChops.difference(a,b).getbbox())
            self.assertIsNotNone(ImageChops.difference(a,c).getbbox())

    def test_device_twelve_hour_setting_changes_only_the_time(self):
        data = {'HOUR_0_23_Z': '23', 'HOUR_1_12': 11}
        full = render_preview(XML, values=data)
        twelve = render_preview(XML, values=data | {'IS_24_HOUR_MODE': False})
        difference = ImageChops.difference(full, twelve)
        self.assertIsNotNone(difference.crop((0, 0, 450, 100)).getbbox())
        self.assertIsNone(difference.crop((0, 100, 450, 450)).getbbox())

if __name__ == '__main__': unittest.main()
