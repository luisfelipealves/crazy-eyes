from pathlib import Path
import tempfile
import unittest
from tools.watchface_preview import render_preview


class NativeMaskSemanticsTest(unittest.TestCase):
    def test_sibling_masks_form_a_union_as_in_wear_os(self):
        # Independent WFF semantics: two separated masks reveal both red strips.
        xml = '''<WatchFace width="100" height="100"><Scene>
        <Group name="masked" x="0" y="0" width="100" height="100">
          <PartDraw x="0" y="0" width="100" height="100">
            <Rectangle x="0" y="0" width="100" height="100"><Fill color="#FF0000"/></Rectangle>
          </PartDraw>
          <PartDraw x="0" y="0" width="100" height="100" renderMode="MASK">
            <Rectangle x="0" y="0" width="30" height="100"><Fill color="#FFFFFF"/></Rectangle>
          </PartDraw>
          <PartDraw x="0" y="0" width="100" height="100" renderMode="MASK">
            <Rectangle x="70" y="0" width="30" height="100"><Fill color="#FFFFFF"/></Rectangle>
          </PartDraw>
        </Group></Scene></WatchFace>'''
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'raw' / 'watchface.xml'
            path.parent.mkdir(); path.write_text(xml)
            view = render_preview(path)
        self.assertEqual(view.getpixel((10, 50)), (255, 0, 0))
        self.assertEqual(view.getpixel((90, 50)), (255, 0, 0))
        self.assertEqual(view.getpixel((50, 50)), (0, 0, 0))
