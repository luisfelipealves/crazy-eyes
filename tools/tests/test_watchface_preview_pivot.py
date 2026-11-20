"""Characterize transformed pivots from the Wear OS4 native failure evidence."""
from pathlib import Path
import tempfile
import unittest
from tools.watchface_preview import render_preview


class TransformedPivotTest(unittest.TestCase):
    def test_transformed_pivot_is_absolute_while_static_pivot_is_normalized(self):
        # Native0.1.8 rotated around the top of its72px group, not49px down.
        # A white16px disk centered36px down rotates around y=.6805556px.
        definition = '''<WatchFace width="450" height="450"><Scene backgroundColor="#000000">
          <Group name="pivot_probe" x="50" y="100" width="72" height="72" pivotX="0.5" pivotY="0.8611111" angle="180">
            <Transform target="pivotY" value="0.6805556" />
            <PartDraw x="0" y="0" width="72" height="72"><Ellipse x="28" y="28" width="16" height="16"><Fill color="#FFFFFF" /></Ellipse></PartDraw>
          </Group></Scene></WatchFace>'''
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'watchface.xml';path.write_text(definition)
            picture=render_preview(path)
        pixels=[(x,y) for y in range(450) for x in range(450) if min(picture.getpixel((x,y)))>150]
        self.assertTrue(pixels)
        self.assertAlmostEqual(sum(x for x,y in pixels)/len(pixels),86,delta=1)
        self.assertAlmostEqual(sum(y for x,y in pixels)/len(pixels),65.36,delta=1)
