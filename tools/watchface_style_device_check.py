"""Assert complete eye silhouettes from real Wear OS screenshots.

These probes are independent of the Python preview. In particular, they reject
the white rectangular overlay captured from the0.1.5 native renderer.
"""
import argparse
import io
from pathlib import Path
import subprocess
import time
from PIL import Image

STYLES = ('cartoon', 'cat', 'robot', 'monster')


def assert_style(picture, style):
    picture = picture.convert('RGB').resize((450, 450))
    for origin in (54, 243):
        def rgb(x, y):
            pixels = [picture.getpixel((origin + x + dx, 122 + y + dy))
                      for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
            return tuple(sum(p[c] for p in pixels) / len(pixels) for c in (0, 1, 2))

        def require(condition, message, value):
            if not condition:
                raise AssertionError(f'{style} eye at{origin}: {message}; RGB={value}')

        corner = rgb(3, 4)
        require(max(corner) < 30, 'rectangular overlay or missing silhouette clipping', corner)
        inside = rgb(76, 60)
        require(min(inside) > 150, 'opening is closed, missing, or wrong face selected', inside)
        top = rgb(76, 10)
        if style == 'cartoon':
            require(min(top) > 180, 'original tall oval is missing', top)
        else:
            require(max(top) < 30, 'wrong outer silhouette at top of eye', top)
        if style == 'robot':
            metal = rgb(6, 33)
            require(30 < max(metal) < 210 and metal[2] > metal[0] + 5,
                    'square metal frame is missing or covered', metal)
        elif style == 'cat':
            outside = rgb(6, 33)
            require(max(outside) < 30, 'almond corner is covered', outside)
            cream = rgb(76, 40)
            require(cream[0] > cream[2] + 20 and cream[1] > cream[2] + 10,
                    'cat opening is missing', cream)
        elif style == 'monster':
            skin = rgb(10, 43)
            require(skin[1] > 80 and skin[1] > skin[0] + 10 and skin[2] < skin[1] - 30,
                    'irregular green socket is missing or covered', skin)


class StyleStability:
    """Do not mistake a transient blink that hides the overlay for a fix."""
    def __init__(self, checker=assert_style):
        self.checker = checker
        self.first_pass = None
        self.passes = 0
        self.error = None

    def observe(self, picture, style, seconds):
        try:
            self.checker(picture, style)
        except AssertionError as error:
            self.first_pass = None
            self.passes = 0
            self.error = error
            return False
        self.error = None
        if self.first_pass is None:
            self.first_pass = seconds
        self.passes += 1
        return self.passes >= 2 and seconds - self.first_pass >= .7


def run(package, style, output):
    output.mkdir(parents=True, exist_ok=True)
    def adb(*args):
        return subprocess.check_output(['adb', *args], timeout=25)
    adb('emu', 'power', 'ac', 'off')
    adb('emu', 'power', 'status', 'discharging')
    adb('emu', 'power', 'capacity', '80')
    adb('emu', 'sensor', 'set', 'acceleration', '0:0:9.8')
    adb('shell', 'settings', 'put', 'system', 'screen_off_timeout', '600000')
    adb('shell', 'input', 'keyevent', 'KEYCODE_WAKEUP')
    adb('shell', 'input', 'keyevent', 'KEYCODE_BACK')
    adb('shell', 'input', 'keyevent', 'KEYCODE_BACK')
    deadline = time.monotonic() + 90
    next_activation = 0
    stability = StyleStability()
    try:
        while True:
            now = time.monotonic()
            if now >= next_activation:
                # Activation can precede cold-boot package registration. Retry
                # against actual visible state rather than assume broadcast success.
                adb('shell', 'am', 'broadcast', '--async', '-a',
                    'com.google.android.wearable.app.DEBUG_SURFACE', '--es', 'operation',
                    'set-watchface', '--es', 'watchFaceId', package)
                next_activation = now + 10
            capture_started = time.monotonic()
            picture = Image.open(io.BytesIO(adb('exec-out', 'screencap', '-p')))
            picture.save(output / (style + '.png'))
            if stability.observe(picture, style, capture_started):
                print(f'PASS native {style}: stable complete eye silhouettes visible; no rectangular overlay', flush=True)
                return
            if time.monotonic() >= deadline:
                raise stability.error or AssertionError(f'{style}: insufficient stable, fully visible captures')
            time.sleep(.5)  # Allow selection transition or a periodic blink to finish.
    finally:
        (output / (style + '-logcat.txt')).write_bytes(adb('logcat', '-d', '-v', 'brief'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', required=True)
    parser.add_argument('--style', choices=STYLES, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.package, args.style, args.output)
