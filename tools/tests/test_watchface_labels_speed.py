from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from PIL import Image
from tools.watchface_preview import DEFAULTS, evaluate
from tools import watchface_device_check as native

XML=Path('watchface/src/main/res/raw/watchface.xml')

def values(mode, enabled='TRUE', **extra):
    return DEFAULTS | {'CONFIGURATION.animation_intensity':mode,'CONFIGURATION.shake_enabled':enabled} | extra

class LabelsAndSpeedTest(unittest.TestCase):
    def test_options_have_captioned_tint_safe_icons_and_portuguese_fallback(self):
        config=ET.parse(XML).find('UserConfigurations/ListConfiguration[@id="animation_intensity"]')
        for folder, expected in [('values',{'calm':'Calm','crazy':'Crazy'}),('values-pt',{'calm':'Tranquilo','crazy':'Maluco'})]:
            path=XML.parent.parent/folder/'strings.xml'
            self.assertTrue(path.is_file(),f'Missing editor locale {folder}')
            strings={n.get('name'):n.text for n in ET.parse(path).getroot()}
            for option in config:
                self.assertEqual(strings[option.get('displayName')],expected[option.get('id')])
                icon=option.get('icon')
                self.assertTrue(icon,'An image-based editor otherwise shows an empty option')
                drawable='drawable-pt-nodpi' if folder=='values-pt' else 'drawable-nodpi'
                path=XML.parent.parent/drawable/(icon+'.png')
                self.assertTrue(path.is_file(),str(path))
                with Image.open(path) as image:
                    self.assertLessEqual(max(image.size),400)
                    alpha=image.convert('RGBA').getchannel('A')
                    self.assertGreater(sum(alpha.crop((35,270,365,340)).histogram()[128:]),800,'Option caption is empty')
                    self.assertGreater(alpha.histogram()[0],image.width*image.height//3,'Icon must retain transparent holes under tint')

    def test_crazy_tilt_is_more_responsive_before_clamping(self):
        root=ET.parse(XML)
        for side in ('left','right'):
            gyro=root.find(f'.//Group[@name="{side}_tilt"]/Gyro')
            for mode,want in [('calm',(-13/3,20/3)),('crazy',(-13,20))]:
                got=[evaluate(gyro.get(axis),values(mode,ACCELEROMETER_ANGLE_X=15,ACCELEROMETER_ANGLE_Y=-15)) for axis in ('x','y')]
                for actual,expected in zip(got,want):self.assertAlmostEqual(actual,expected)

    def test_crazy_fallback_changes_each_second_while_calm_holds_two(self):
        root=ET.parse(XML)
        for side in ('left','right'):
            e=root.find(f'.//Group[@name="{side}_wander"]/Transform[@target="x"]').get('value')
            for mode,changes in [('calm',False),('crazy',True)]:
                a=evaluate(e,values(mode,SECONDS_IN_DAY=10.2))
                b=evaluate(e,values(mode,SECONDS_IN_DAY=11.2))
                self.assertEqual(abs(a-b)>.01,changes)

    def test_only_selected_rotation_controller_arms_and_has_its_own_speed(self):
        root=ET.parse(XML)
        for mode,duration in [('calm',3),('crazy',2)]:
            for enabled in ('FALSE','TRUE'):
                for side,sign in [('left',1),('right',-1)]:
                    transforms=root.find(f'.//Group[@name="{side}_spin"]').findall('.//Transform[@target="angle"]')
                    armed=[n for n in transforms if evaluate(n.get('value'),values(mode,enabled,ACCELEROMETER_X=40))]
                    self.assertEqual(len(armed),1 if enabled=='TRUE' else 0)
                    if armed:
                        self.assertEqual(evaluate(armed[0].get('value'),values(mode,enabled,ACCELEROMETER_X=40)),sign*15)
                        self.assertEqual(float(armed[0].find('Animation').get('duration')),duration)

    def test_native_validator_distinguishes_fast_and_slow_orbits(self):
        base=[(131,226),(320,226)]
        def s(t,p):return {'seconds':t,'eyes':p}
        fast=[s(.21,[(157,252),(294,252)]),s(.6,[(131,278),(320,278)]),s(1,[(105,252),(346,252)]),s(1.4,[(118,229),(333,229)]),s(2.3,base),s(2.95,base),s(3.6,base)]
        self.assertIn('duration',__import__('inspect').signature(native.validate_trials).parameters,'Native proof must check the faster stopping time')
        native.validate_trials(base,[fast,fast],duration=2)
        slow=[s(.3,[(157,252),(294,252)]),s(1,[(131,278),(320,278)]),s(1.8,[(105,252),(346,252)]),s(2.35,[(118,229),(333,229)]),s(3.8,base),s(4.43,base),s(5.17,base)]
        with self.assertRaises(AssertionError):native.validate_trials(base,[slow],duration=2)
        native.validate_trials(base,[slow],duration=3)

    def test_native_soft_tilt_proof_rejects_old_crazy_gain(self):
        self.assertTrue(hasattr(native,'validate_tilt_gain'),'A full-range tilt cannot distinguish the faster response')
        base=[(131,226),(320,226)]
        native.validate_tilt_gain(base,[(150.5,226),(339.5,226)],19.5)
        native.validate_tilt_gain(base,[(137.5,226),(326.5,226)],6.5)
        with self.assertRaises(AssertionError):native.validate_tilt_gain(base,[(144,226),(333,226)],19.5)
