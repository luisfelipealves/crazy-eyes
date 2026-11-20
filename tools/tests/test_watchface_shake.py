"""Boundary tests for the sensor expressions actually shipped in the WFF XML."""
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from tools.watchface_preview import DEFAULTS, evaluate


class WatchfaceShakeTest(unittest.TestCase):
    def test_gravity_in_any_orientation_is_quiet_but_a_shake_arms_opposite_rotations(self):
        root = ET.parse(Path('watchface/src/main/res/raw/watchface.xml'))
        expressions = []
        for eye in ('left_tilt', 'right_tilt'):
            transform = root.find(f'.//Group[@name="{eye}"]/Group/Transform[@target="angle"]')
            self.assertIsNotNone(transform, 'Sensor-supported pupils have no shake reaction')
            expressions.append(transform.get('value'))
        fixtures = [
            ((0, 0, 9.8), (0, 0)),
            ((0, -9.8, 0), (0, 0)),
            ((-9.8, 0, 0), (0, 0)),
            ((6.93, 0, 6.93), (0, 0)),
            ((0, 0, 24.9), (0, 0)),
            ((40, 0, 9.8), (15, -15)),
            ((0, -40, 9.8), (15, -15)),
            ((0, 0, 40), (15, -15)),
        ]
        for axes, expected in fixtures:
            values = DEFAULTS | {'CONFIGURATION.shake_enabled': 'TRUE','CONFIGURATION.animation_intensity':'crazy'} | dict(zip(('ACCELEROMETER_X', 'ACCELEROMETER_Y', 'ACCELEROMETER_Z'), axes))
            with self.subTest(axes=axes):
                self.assertEqual(tuple(evaluate(e, values) for e in expressions), expected)
