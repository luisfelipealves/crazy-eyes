"""Motion settings must alter travel, never neutral pupil geometry or other feedback."""
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
from PIL import ImageChops
from tools.watchface_preview import DEFAULTS, evaluate, render_preview
from tools.watchface_device_check import centroids, validate_trials

XML = Path('watchface/src/main/res/raw/watchface.xml')


def settings(mode='crazy', shake='TRUE', **more):
    return {'CONFIGURATION.animation_intensity': mode, 'CONFIGURATION.shake_enabled': shake} | more


class AnimationIntensityTest(unittest.TestCase):
    def test_calm_halves_both_tilt_axes_and_retains_inversion(self):
        tree = ET.parse(XML)
        for side in ('left', 'right'):
            gyro = tree.find(f'.//Group[@name="{side}_tilt"]/Gyro')
            for mode, expected in [('calm', (-13, 20)), ('crazy', (-26, 40))]:
                values = DEFAULTS | settings(mode) | {'ACCELEROMETER_ANGLE_X': 90, 'ACCELEROMETER_ANGLE_Y': -90}
                self.assertEqual(tuple(evaluate(gyro.get(k), values) for k in ('x', 'y')), expected)

    def test_shake_triggers_opposite_directions_in_both_modes(self):
        tree = ET.parse(XML)
        for mode in ('calm', 'crazy'):
            for accel, expected in [(0, (0, 0)), (40, (15, -15))]:
                values = DEFAULTS | settings(mode) | {'ACCELEROMETER_X': accel}
                actual = tuple(sum(evaluate(n.get('value'),values) for n in tree.find(f'.//Group[@name="{side}_spin"]').findall('.//Transform[@target="angle"]')) for side in ('left','right'))
                self.assertEqual(actual, expected)

    def test_calm_halves_fallback_travel_even_when_shake_is_off(self):
        tree = ET.parse(XML)
        for side in ('left', 'right'):
            wander = tree.find(f'.//Group[@name="{side}_wander"]')
            for seconds in (0, 2, 10, 42):
                for axis, origin in [('x', 41), ('y', 68)]:
                    expression = wander.find(f'Transform[@target="{axis}"]').get('value')
                    values = DEFAULTS | {'SECONDS_IN_DAY': seconds}
                    crazy = evaluate(expression, values | settings('crazy', 'FALSE')) - origin
                    calm = evaluate(expression, values | settings('calm', 'FALSE') | {'SECONDS_IN_DAY':seconds*2}) - origin
                    self.assertAlmostEqual(calm, crazy / 2)

    def test_neutral_pupil_size_and_clock_stay_identical_in_every_mode(self):
        baseline = render_preview(XML)
        for mode in ('calm', 'crazy'):
            for shake in ('TRUE', 'FALSE'):
                self.assertIsNone(ImageChops.difference(baseline, render_preview(XML, values=settings(mode, shake))).getbbox())

    def test_calm_orbit_is_half_size_with_neutral_gaze_unchanged(self):
        baseline = centroids(render_preview(XML))
        with tempfile.TemporaryDirectory() as directory:
            raw = Path(directory) / 'raw'; raw.mkdir()
            (raw.parent / 'drawable-nodpi').symlink_to(XML.parent.parent.resolve() / 'drawable-nodpi')
            tree = ET.parse(XML)
            for side, angle in [('left', 90), ('right', -90)]:
                tree.find(f'.//Group[@name="{side}_spin"]/Transform[@target="angle"]').set('value', str(angle))
            definition = raw / 'watchface.xml'; tree.write(definition)
            for mode, radius in [('calm', 13), ('crazy', 26)]:
                points = centroids(render_preview(definition, values=settings(mode)))
                for eye, direction in [(0, 1), (1, -1)]:
                    self.assertAlmostEqual((points[eye][0] - baseline[eye][0]) * direction, radius, delta=1)
                    self.assertAlmostEqual(points[eye][1] - baseline[eye][1], radius, delta=1)

    def test_modes_keep_battery_mood_tap_and_ambient_for_all_styles(self):
        for style in ('cartoon', 'cat', 'robot', 'monster'):
            normal = {'CONFIGURATION.eye_style': style}
            for mode in ('calm', 'crazy'):
                values = normal | settings(mode, 'FALSE')
                for extra, arguments in [({'BATTERY_PERCENT': 20}, {}), ({'BATTERY_CHARGING_STATUS': True}, {}),
                                         ({}, {'poke': ('left_poke', 0)}), ({}, {'ambient': True})]:
                    expected = render_preview(XML, values=normal | extra, **arguments)
                    actual = render_preview(XML, values=values | extra, **arguments)
                    self.assertIsNone(ImageChops.difference(expected, actual).getbbox(), (style, mode, extra, arguments))

    def test_native_probe_accepts_13px_orbit_and_rejects_large_orbit_for_calm(self):
        base = [(131, 226), (320, 226)]
        def sample(t, eyes): return {'seconds': t, 'eyes': eyes}
        calm = [sample(.3, [(144, 239), (307, 239)]), sample(.8, [(131, 252), (320, 252)]),
                sample(1.4, [(118, 239), (333, 239)]), sample(2.1, [(124.5, 227.5), (326.5, 227.5)]),
                sample(3.8, base), sample(4.43, base), sample(5.17, base)]
        validate_trials(base, [calm, calm], orbit_radius=13)
        with self.assertRaises(AssertionError):
            validate_trials(base, [calm, calm], orbit_radius=26)
