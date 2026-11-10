from pathlib import Path
import itertools
import unittest

from PIL import ImageChops
from tools.watchface_preview import render_preview

XML = Path('watchface/src/main/res/raw/watchface.xml')
STYLES = ('cartoon', 'cat', 'robot', 'monster')
COLORS = ('gray', 'blue', 'green', 'brown', 'purple', 'amber')


def configured(style='cartoon', color='gray', **kwargs):
    return render_preview(XML, values={'CONFIGURATION.eye_style': style,
                                      'CONFIGURATION.eye_color': color}, **kwargs)


class WatchfaceCustomizationTest(unittest.TestCase):
    def test_each_style_changes_both_pupils_without_changing_time_or_sclera(self):
        views = [configured(style) for style in STYLES]
        for a, b in itertools.combinations(views, 2):
            for x in (95, 284):
                self.assertIsNotNone(ImageChops.difference(a, b).crop((x, 190, x + 72, 262)).getbbox())
            self.assertIsNone(ImageChops.difference(a, b).crop((0, 0, 450, 180)).getbbox())

    def test_each_color_changes_iris_but_keeps_pupil_and_highlight(self):
        views = [configured(color=color) for color in COLORS]
        self.assertEqual(len({v.getpixel((131, 195)) for v in views}), 6)
        for view in views:
            self.assertEqual(view.getpixel((131, 226)), (6, 8, 13))
            self.assertEqual(view.getpixel((120, 214)), (255, 255, 255))

    def test_all_combinations_work_in_sensor_fallback_and_do_not_change_ambient(self):
        ambient = render_preview(XML, ambient=True)
        fallback_views = set()
        for style, color in itertools.product(STYLES, COLORS):
            normal = configured(style, color)
            fallback = render_preview(XML, values={'CONFIGURATION.eye_style': style,
                                                  'CONFIGURATION.eye_color': color,
                                                  'ACCELEROMETER_IS_SUPPORTED': False})
            fallback_views.add(fallback.tobytes())
            self.assertIsNone(ImageChops.difference(ambient, configured(style, color, ambient=True)).getbbox())
            poked = render_preview(XML, values={'CONFIGURATION.eye_style': style,
                                               'CONFIGURATION.eye_color': color}, poke=('left_poke', 0))
            self.assertEqual(poked.getpixel((100, 150)), (0, 0, 0))
            self.assertIsNone(ImageChops.difference(normal, poked).crop((240, 120, 400, 335)).getbbox())
        self.assertEqual(len(fallback_views), 24)
