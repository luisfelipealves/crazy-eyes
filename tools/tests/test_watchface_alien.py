from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from PIL import ImageChops
from tools.watchface_preview import render_preview

XML=Path('watchface/src/main/res/raw/watchface.xml')

class AlienEyeTest(unittest.TestCase):
    def test_existing_style_id_now_has_alien_label_in_both_languages(self):
        tree=ET.parse(XML)
        option=tree.find("UserConfigurations/ListConfiguration[@id='eye_style']/ListOption[@id='monster']")
        for locale,want in [('values','Alien'),('values-pt','Alienígena'),('values-pt-rBR','Alienígena')]:
            values={x.get('name'):x.text for x in ET.parse(XML.parent.parent/locale/'strings.xml').getroot()}
            self.assertEqual(values[option.get('displayName')],want)

    def test_alien_eyes_are_green_and_distinct_from_cat_and_cartoon(self):
        values={'CONFIGURATION.eye_style':'monster','CONFIGURATION.eye_color':'blue'}
        picture=render_preview(XML,values=values)
        for style in ('cartoon','cat','robot'):
            other=render_preview(XML,values=values | {'CONFIGURATION.eye_style':style})
            for x in (54,243):
                self.assertIsNotNone(ImageChops.difference(picture,other).crop((x,122,x+153,329)).getbbox())
        for x in (54,243):
            colors=[picture.getpixel((i,j)) for i in range(x,x+153) for j in range(122,329)]
            self.assertGreater(sum(g>r*1.25 and g>b*1.10 and g>55 for r,g,b in colors),500)

    def test_alien_reacts_to_tap_and_keeps_ambient_budget(self):
        v={'CONFIGURATION.eye_style':'monster','CONFIGURATION.eye_color':'blue'}
        normal=render_preview(XML,values=v)
        poked=render_preview(XML,values=v,poke=('left_poke',0))
        self.assertIsNotNone(ImageChops.difference(normal,poked).crop((54,122,207,329)).getbbox())
        self.assertIsNone(ImageChops.difference(normal,poked).crop((243,122,396,329)).getbbox())
        ambient=render_preview(XML,ambient=True,values=v)
        self.assertLess(sum(ambient.convert('L').histogram()[1:])/(450*450),.15)
        self.assertIsNotNone(ambient.crop((54,122,207,329)).getbbox())
