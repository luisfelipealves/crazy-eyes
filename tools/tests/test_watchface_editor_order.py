import unittest
import xml.etree.ElementTree as ET
from tools.watchface_preview import DEFAULTS, evaluate
from pathlib import Path

XML = Path('watchface/src/main/res/raw/watchface.xml')

class EditorOrderTest(unittest.TestCase):
    def test_time_options_are_first_and_shake_switch_is_removed(self):
        root=ET.parse(XML)
        config=root.find('UserConfigurations')
        ids=[e.get('id') for e in config]
        self.assertEqual(ids[:3],['time_size','time_color','time_font'])
        self.assertNotIn('shake_enabled',ids)
        self.assertNotIn('CONFIGURATION.shake_enabled',XML.read_text())

    def test_shake_reacts_in_all_modes_and_rest_is_idle(self):
        root=ET.parse(XML)
        for mode in ('calm','crazy','wild'):
            for side,sign in (('left',1),('right',-1)):
                transforms=root.find(f'.//Group[@name="{side}_spin"]').findall('.//Transform[@target="angle"]')
                for accel,want in ((0,0),(40,sign*15)):
                    values=DEFAULTS | {'CONFIGURATION.animation_intensity':mode,'ACCELEROMETER_X':accel}
                    self.assertEqual(sum(evaluate(n.get('value'),values) for n in transforms),want)
