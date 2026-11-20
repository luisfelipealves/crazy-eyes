import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

XML = Path('watchface/src/main/res/raw/watchface.xml')

class ComplicationsTest(unittest.TestCase):
    def test_two_separate_user_editable_slots_below_the_eyes(self):
        root=ET.parse(XML)
        slots=root.findall('./Scene/ComplicationSlot')
        self.assertEqual(len(slots),2)
        self.assertEqual(len({s.get('slotId') for s in slots}),2)
        for slot in slots:
            self.assertGreaterEqual(int(slot.get('y')),330)
            self.assertTrue({'SHORT_TEXT','MONOCHROMATIC_IMAGE','EMPTY'}.issubset(set(slot.get('supportedTypes').split())))
            self.assertIsNotNone(slot.find("Complication[@type='SHORT_TEXT']//Parameter[@expression='[COMPLICATION.TEXT]']"))
            self.assertIsNotNone(slot.find("Complication[@type='MONOCHROMATIC_IMAGE']//Image[@resource='[COMPLICATION.MONOCHROMATIC_IMAGE]']"))

    def test_complication_text_and_icon_follow_clock_color(self):
        for slot in ET.parse(XML).findall('./Scene/ComplicationSlot'):
            font=slot.find("Complication[@type='SHORT_TEXT']//Font")
            icon=slot.find("Complication[@type='MONOCHROMATIC_IMAGE']/PartImage")
            self.assertEqual(font.get('color'),'[CONFIGURATION.time_color.0]')
            self.assertEqual(icon.get('tintColor'),'[CONFIGURATION.time_color.0]')
