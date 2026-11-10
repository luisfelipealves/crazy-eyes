from pathlib import Path
import unittest
from PIL import Image
from tools.watchface_preview import render_preview
from tools.watchface_style_device_check import assert_style, STYLES

XML = Path('watchface/src/main/res/raw/watchface.xml')


class NativeSilhouetteProbeTest(unittest.TestCase):
    def test_accepts_each_complete_style(self):
        for style in STYLES:
            with self.subTest(style=style):
                assert_style(render_preview(XML, values={'CONFIGURATION.eye_style': style}), style)

    def test_rejects_actual_native_015_rectangle_overlay(self):
        picture = Image.open(Path(__file__).parent / 'fixtures/native-015-rectangle-overlay.png')
        for style in STYLES:
            with self.subTest(style=style), self.assertRaisesRegex(AssertionError, 'rectangular overlay'):
                assert_style(picture, style)

    def test_rejects_a_different_selected_style(self):
        for actual, expected in (('cat', 'robot'), ('robot', 'cat'), ('cartoon', 'monster'), ('monster', 'cartoon')):
            with self.subTest(actual=actual, expected=expected), self.assertRaises(AssertionError):
                assert_style(render_preview(XML, values={'CONFIGURATION.eye_style': actual}), expected)
