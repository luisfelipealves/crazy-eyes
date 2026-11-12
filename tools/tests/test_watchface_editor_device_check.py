import importlib.util
import unittest

class EditorLabelsTest(unittest.TestCase):
    def test_only_visible_option_labels_count_not_app_name_or_hidden_nodes(self):
        self.assertIsNotNone(importlib.util.find_spec('tools.watchface_editor_device_check'),'Native editor must be inspected')
        from tools.watchface_editor_device_check import visible_intensity_labels
        xml='''<hierarchy><node text="Crazy Eyes Shake" bounds="[0,0][400,80]"/><node text="Calm" bounds="[0,0][0,0]"/><node content-desc="Maluco, selected" bounds="[80,100][380,200]"/><node text="Tranquilo" bounds="[80,220][380,320]"/></hierarchy>'''
        self.assertEqual(visible_intensity_labels(xml),{'calm','crazy'})
        self.assertEqual(visible_intensity_labels('<hierarchy><node text="Crazy Eyes Shake" bounds="[0,0][400,80]"/></hierarchy>'),set())

        self.assertEqual(visible_intensity_labels('<hierarchy><node text="Calm" bounds="[0,500][400,600]"/></hierarchy>'),set())
