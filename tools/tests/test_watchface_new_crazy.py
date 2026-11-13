import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from tools.watchface_preview import DEFAULTS, evaluate

XML = Path('watchface/src/main/res/raw/watchface.xml')

class NewCrazyModeTest(unittest.TestCase):
    def test_three_named_options_keep_previous_crazy_as_normal(self):
        config = ET.parse(XML).find('UserConfigurations/ListConfiguration[@id="animation_intensity"]')
        strings = {n.get('name'): n.text for n in ET.parse(XML.parent.parent/'values-pt'/'strings.xml').getroot()}
        self.assertEqual([strings[n.get('displayName')] for n in config], ['Tranquilo', 'Normal', 'Maluco'])
        self.assertEqual(config.get('defaultValue'), 'crazy')

    def test_wild_spin_requires_shake_and_respects_switch(self):
        tree = ET.parse(XML)
        for side, sign in [('left', 1), ('right', -1)]:
            transform = tree.find(f'.//Group[@name="{side}_wild_spin"]/Transform[@target="angle"]')
            expr = transform.get('value')
            for enabled, accel, want in [('TRUE', 0, 0), ('FALSE', 40, 0), ('TRUE', 40, sign*15)]:
                values = DEFAULTS | {'CONFIGURATION.animation_intensity':'wild', 'CONFIGURATION.shake_enabled':enabled, 'ACCELEROMETER_X':accel}
                self.assertEqual(evaluate(expr, values),want)
            self.assertEqual(float(transform.find('Animation').get('duration')), 1)

    def test_no_shake_spin_without_accelerometer(self):
        tree = ET.parse(XML)
        for side in ('left','right'):
            group = tree.find(f'.//Group[@name="{side}_wild_wander_spin"]')
            expr = group.find('Transform[@target="angle"]').get('value')
            for seconds in (1, 1.25):
                self.assertEqual(evaluate(expr, DEFAULTS | {'CONFIGURATION.animation_intensity':'wild', 'SECOND_MILLISECOND':seconds}), 0)
