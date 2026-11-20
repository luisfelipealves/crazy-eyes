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
    def test_each_style_changes_whole_eyes_without_changing_time(self):
        views = [configured(style) for style in STYLES]
        for a, b in itertools.combinations(views, 2):
            for x in (95, 284):
                self.assertIsNotNone(ImageChops.difference(a, b).crop((x, 190, x + 72, 262)).getbbox())
            for x in (54, 243):
                self.assertIsNotNone(ImageChops.difference(a, b).crop((x, 122, x + 153, 185)).getbbox())
            self.assertIsNone(ImageChops.difference(a, b).crop((0, 0, 450, 85)).getbbox())

    def test_each_color_changes_iris_but_keeps_pupil_and_highlight(self):
        views = [configured(color=color) for color in COLORS]
        self.assertEqual(len({v.getpixel((131, 195)) for v in views}), 6)
        for view in views:
            self.assertEqual(view.getpixel((131, 226)), (6, 8, 13))
            self.assertEqual(view.getpixel((120, 214)), (255, 255, 255))

    def test_all_combinations_work_in_sensor_fallback_with_color_independent_ambient(self):
        fallback_views = set()
        for style, color in itertools.product(STYLES, COLORS):
            ambient = configured(style, ambient=True)
            normal = configured(style, color)
            fallback = render_preview(XML, values={'CONFIGURATION.eye_style': style,
                                                  'CONFIGURATION.eye_color': color,
                                                  'ACCELEROMETER_IS_SUPPORTED': False})
            fallback_views.add(fallback.tobytes())
            self.assertIsNone(ImageChops.difference(ambient, configured(style, color, ambient=True)).getbbox())
            poked = render_preview(XML, values={'CONFIGURATION.eye_style': style,
                                               'CONFIGURATION.eye_color': color}, poke=('left_poke', 0))
            self.assertEqual(poked.getpixel((130, 182)), (0, 0, 0))
            self.assertIsNone(ImageChops.difference(normal, poked).crop((240, 120, 400, 335)).getbbox())
        self.assertEqual(len(fallback_views), 24)

    def test_robot_has_a_square_metal_frame_that_remains_when_poked(self):
        robot = configured('robot', 'blue')
        frame = robot.getpixel((60, 155))
        self.assertGreater(sum(frame), 80)
        self.assertGreater(frame[2], frame[0])
        self.assertEqual(frame, render_preview(XML, values={'CONFIGURATION.eye_style': 'robot',
                                                          'CONFIGURATION.eye_color': 'blue'},
                                               poke=('left_poke', 0)).getpixel((60, 155)))

    def test_cat_and_monster_have_their_own_outer_shapes(self):
        self.assertEqual(configured('cat').getpixel((130, 132)), (0, 0, 0))
        skin = configured('monster').getpixel((64, 165))
        self.assertGreater(skin[1], 80)
        self.assertGreater(skin[1], skin[0] + 10)

    def test_ambient_matches_each_style_and_stays_within_pixel_budget(self):
        views = [configured(style, ambient=True) for style in STYLES]
        self.assertEqual(len({v.crop((45, 110, 405, 340)).tobytes() for v in views}), 4)
        for view in views:
            self.assertLess(sum(view.convert('L').histogram()[1:]) / (450 * 450), .15)
