from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from PIL import Image
from tools import watchface_style_device_check as native_check
from tools.watchface_preview import render_preview
from tools.watchface_style_device_check import assert_style, STYLES

XML = Path('watchface/src/main/res/raw/watchface.xml')


class NativeSilhouetteProbeTest(unittest.TestCase):
    def stability(self):
        self.assertTrue(hasattr(native_check, 'StyleStability'), 'Native verification must require stable frames beyond a blink')
        return native_check.StyleStability()

    def test_acceptance_requires_more_than_a_single_visible_frame(self):
        check = self.stability()
        picture = render_preview(XML)
        self.assertFalse(check.observe(picture, 'cartoon', 0))
        self.assertFalse(check.observe(picture, 'cartoon', .1))
        self.assertTrue(check.observe(picture, 'cartoon', .8))

    def test_a_bad_frame_resets_the_stability_window(self):
        check = self.stability()
        picture = render_preview(XML)
        overlay = Image.open(Path(__file__).parent / 'fixtures/native-015-rectangle-overlay.png')
        self.assertFalse(check.observe(picture, 'cartoon', 0))
        self.assertFalse(check.observe(overlay, 'cartoon', .4))
        self.assertFalse(check.observe(picture, 'cartoon', .8))
        self.assertTrue(check.observe(picture, 'cartoon', 1.6))

    def test_broken_015_composition_cannot_pass_by_blinking(self):
        self.stability()  # Assert the temporal guard exists before generating fixtures.
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'raw/watchface.xml'; path.parent.mkdir()
            (path.parent.parent / 'drawable-nodpi').symlink_to(XML.parent.parent.resolve() / 'drawable-nodpi')
            tree = ET.parse(XML)
            for side in ('left', 'right'):
                lid = tree.find(f'.//Group[@name="{side}_lid"]')
                nested = lid.find('Group')
                index = list(lid).index(nested); lid.remove(nested)
                for child in nested:
                    lid.insert(index, child); index += 1
            tree.write(path)
            phases = {'cartoon': [.010], 'cat': [.045, .050],
                      'robot': [.045, .050, .060, .070], 'monster': [.055, .060, .065, .070]}
            for style in STYLES:
                check = self.stability()
                for cycle in (0, 6):
                    for phase in phases[style] + [1]:
                        view = render_preview(path, values={'CONFIGURATION.eye_style': style,
                                                           'SECOND_MILLISECOND': cycle + phase})
                        self.assertFalse(check.observe(view, style, cycle + phase), (style, cycle, phase))

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
