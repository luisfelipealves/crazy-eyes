"""Static WFF geometry checks; playback timing is verified by the device check."""
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from tools.watchface_device_check import centroids
from tools.watchface_preview import render_preview

XML = Path('watchface/src/main/res/raw/watchface.xml')


class ShakeAmplitudeTest(unittest.TestCase):
    def test_pupils_travel_further_to_both_sides_and_stay_visible(self):
        baseline = centroids(render_preview(XML))
        with tempfile.TemporaryDirectory() as directory:
            raw = Path(directory) / 'raw'
            raw.mkdir()
            (raw.parent / 'drawable-nodpi').symlink_to(XML.parent.parent.resolve() / 'drawable-nodpi')
            for left_angle in (90, 270):
                tree = ET.parse(XML)
                for side, angle in (('left', left_angle), ('right', -left_angle)):
                    tree.find(f'.//PartImage[@name="{side}_spin"]/Transform').set('value', str(angle))
                definition = raw / 'watchface.xml'
                tree.write(definition)
                points = centroids(render_preview(definition))
                for eye in (0, 1):
                    expected_sign = (1 if eye == 0 else -1) * (1 if left_angle == 90 else -1)
                    self.assertGreater((points[eye][0] - baseline[eye][0]) * expected_sign, 24)
                    self.assertGreater(points[eye][1] - baseline[eye][1], 24)
