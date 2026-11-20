from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from PIL import ImageChops
from tools.watchface_preview import render_preview

XML = Path('watchface/src/main/res/raw/watchface.xml')

class TimeOptionsTest(unittest.TestCase):
    def test_options_exist_and_default_appearance_is_preserved(self):
        root=ET.parse(XML)
        for config_id, default, count in [('time_size','medium',3),('time_font','system',3),('time_color','gray',6)]:
            config=root.find(f'UserConfigurations/*[@id="{config_id}"]')
            self.assertIsNotNone(config)
            self.assertEqual(config.get('defaultValue'),default)
            self.assertEqual(len(config),count)

    def test_each_time_option_visibly_changes_the_clock(self):
        default=render_preview(XML)
        for settings in [{'CONFIGURATION.time_size':'small'}, {'CONFIGURATION.time_size':'large'},
                         {'CONFIGURATION.time_font':'serif'}, {'CONFIGURATION.time_font':'mono'},
                         {'CONFIGURATION.time_color':'blue'}]:
            image=render_preview(XML,values=settings)
            diff=ImageChops.difference(default,image)
            self.assertIsNotNone(diff.crop((0,0,450,110)).getbbox(),settings)
            self.assertIsNone(diff.crop((0,110,450,450)).getbbox(),settings)

    def test_each_combination_has_clock_in_ambient_and_12_hour_modes(self):
        for size in ('small','medium','large'):
            for font in ('system','serif','mono'):
                for is24 in (True,False):
                    values={'CONFIGURATION.time_size':size,'CONFIGURATION.time_font':font,'IS_24_HOUR_MODE':is24}
                    image=render_preview(XML,ambient=True,values=values)
                    self.assertIsNotNone(image.crop((70,0,380,110)).getbbox(),values)
                    self.assertLess(sum(image.convert('L').histogram()[1:])/(450*450),.15)
