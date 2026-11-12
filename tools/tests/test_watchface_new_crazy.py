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

    def test_wild_eyes_spin_immediately_in_opposite_directions(self):
        tree = ET.parse(XML)
        for side, sign in [('left', 1), ('right', -1)]:
            group = tree.find(f'.//Group[@name="{side}_wild_spin"]')
            self.assertIsNotNone(group)
            expr = group.find('Transform[@target="angle"]').get('value')
            for mode in ('calm', 'crazy'):
                self.assertEqual(evaluate(expr, DEFAULTS | {'CONFIGURATION.animation_intensity':mode, 'SECOND_MILLISECOND':1.25}),0)
            a = evaluate(expr, DEFAULTS | {'CONFIGURATION.animation_intensity':'wild','SECOND_MILLISECOND':1.0})
            b = evaluate(expr, DEFAULTS | {'CONFIGURATION.animation_intensity':'wild','SECOND_MILLISECOND':1.25})
            self.assertAlmostEqual((b-a)*sign, 90)

    def test_wild_keeps_spinning_without_accelerometer(self):
        tree = ET.parse(XML)
        for side in ('left', 'right'):
            self.assertIsNotNone(tree.find(f'.//Group[@name="{side}_wild_wander_spin"]'))
