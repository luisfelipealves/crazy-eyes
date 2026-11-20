import tempfile
import unittest
from pathlib import Path
from PIL import Image
from tools.watchface_assets import generate


class WatchfaceAssetsTest(unittest.TestCase):
    def test_neutral_poke_band_keeps_square_corners_open_and_recovers(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate(Path(tmp))
            open_mask = Image.open(Path(tmp) / 'open_band.png').getchannel('A')
            self.assertEqual(open_mask.getextrema(), (255, 255))
            animation = Image.open(Path(tmp) / 'poke_band.webp')
            closed = animation.convert('RGBA').getchannel('A')
            self.assertEqual(closed.getpixel((0, 103)), 255)
            self.assertEqual(closed.getpixel((76, 30)), 0)
            animation.seek(animation.n_frames - 1)
            self.assertEqual(animation.convert('RGBA').getchannel('A').tobytes(), open_mask.tobytes())

    def test_poke_closes_then_recovers_to_open_thumbnail(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate(Path(tmp))
            animation = Image.open(Path(tmp) / 'poke_mask.webp')
            first = animation.convert('RGBA').getchannel('A')
            animation.seek(animation.n_frames - 1)
            last = animation.convert('RGBA').getchannel('A')
            self.assertLess(first.getbbox()[3] - first.getbbox()[1], 25)
            self.assertGreater(last.getbbox()[3] - last.getbbox()[1], 200)
            self.assertEqual(last.tobytes(), Image.open(Path(tmp) / 'eye_mask.png').getchannel('A').tobytes())
            durations = []
            for i in range(animation.n_frames):
                animation.seek(i)
                animation.load()
                durations.append(animation.info['duration'])
            self.assertEqual(sum(durations), 900)

    def test_ambient_outline_stays_under_pixel_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            generate(Path(tmp))
            im = Image.open(Path(tmp) / 'eyes_ambient.png').convert('RGB')
            lit = sum(im.convert('L').histogram()[1:])
            self.assertLess(lit / (im.width * im.height), .10)  # reserve headroom for the time
            self.assertGreater(lit, 1000)
            self.assertEqual(im.getpixel((130, 225)), (0, 0, 0))

if __name__ == '__main__':
    unittest.main()
