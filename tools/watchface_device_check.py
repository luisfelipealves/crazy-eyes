"""Characterize actual WFF after-shake motion on a connected Wear OS emulator.

This deliberately does not simulate WFF animation. Sensor values enter through
the emulator and centroids are measured from the system renderer's screenshots.
"""
import argparse
import io
import json
import math
from pathlib import Path
import subprocess
import time

from PIL import Image


def adb(*args):
    return subprocess.check_output(['adb', *args], timeout=25)


def capture(output, label):
    picture = Image.open(io.BytesIO(adb('exec-out', 'screencap', '-p'))).convert('RGB')
    picture.save(output / (label + '.png'))
    return picture.resize((450, 450))


def centroids(picture):
    eyes = []
    for origin in (54, 243):
        dark = []
        white = 0
        for y in range(125, 327):
            for x in range(origin + 2, origin + 151):
                # Exclude the black area around the ellipse and its AA boundary.
                if ((x - origin - 76.5) / 74) ** 2 + ((y - 225.5) / 100) ** 2 >= 1:
                    continue
                r, g, b = picture.getpixel((x, y))
                if max(r, g, b) < 80:
                    dark.append((x, y))
                if min(r, g, b) > 150:
                    white += 1
        if not 2000 < len(dark) < 6500 or white < 5000:
            raise ValueError(f'Face not visible, blinking, or obscured: dark={len(dark)}, white={white}')
        eyes.append(tuple(sum(p[i] for p in dark) / len(dark) for i in (0, 1)))
    return eyes


def run(package, output):
    output.mkdir(parents=True, exist_ok=True)
    adb('shell', 'settings', 'put', 'system', 'screen_off_timeout', '600000')
    adb('shell', 'svc', 'power', 'stayon', 'true')
    adb('shell', 'input', 'keyevent', 'KEYCODE_WAKEUP')
    adb('emu', 'sensor', 'set', 'acceleration', '0:0:9.8')
    print(adb('shell', 'am', 'broadcast', '-a', 'com.google.android.wearable.app.DEBUG_SURFACE',
              '--es', 'operation', 'set-watchface', '--es', 'watchFaceId', package).decode(), flush=True)
    deadline = time.monotonic() + 60
    while True:
        try:
            baseline = centroids(capture(output, 'baseline'))
            break
        except ValueError:
            if time.monotonic() > deadline:
                raise RuntimeError('SETUP: could not display the watch face; inspect baseline.png and logcat')
            time.sleep(1)

    traces = []
    # Two independent pulses detect a one-shot-only reaction or a failure to settle.
    for trial in range(2):
        adb('emu', 'sensor', 'set', 'acceleration', '40:0:9.8')
        time.sleep(.35)
        adb('emu', 'sensor', 'set', 'acceleration', '0:0:9.8')
        released = time.monotonic()
        samples = []
        for delay in (.3, .8, 1.4, 2.1, 3.8):
            remaining = released + delay - time.monotonic()
            if remaining > 0:
                time.sleep(remaining)
            picture = capture(output, f'trial-{trial}-{delay}')
            try:
                points = centroids(picture)
            except ValueError:
                continue  # A periodic blink invalidates this one measurement.
            samples.append({'seconds': time.monotonic() - released, 'eyes': points})
        traces.append(samples)
    (output / 'measurements.json').write_text(json.dumps({'baseline': baseline, 'trials': traces}, indent=2))
    for trial, samples in enumerate(traces):
        active = []
        for sample in samples:
            if .2 < sample['seconds'] < 2.8:
                dy = [sample['eyes'][i][1] - baseline[i][1] for i in (0, 1)]
                if dy[0] * dy[1] < -16 and min(map(abs, dy)) > 4:
                    active.append(sample)
        if not active:
            raise AssertionError(f'No opposite pupil orbit after release in trial {trial}; see measurements.json')
        final = samples[-1]
        if final['seconds'] < 3.5 or any(math.dist(final['eyes'][i], baseline[i]) > 3 for i in (0, 1)):
            raise AssertionError(f'Pupils did not settle after about 3 seconds in trial {trial}')
    print('PASS: opposite after-release pupil motion and recovery observed twice in the Wear OS renderer')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', required=True)
    parser.add_argument('--output', type=Path, default=Path('watchface-device-results'))
    args = parser.parse_args()
    try:
        run(args.package, args.output)
    finally:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / 'logcat.txt').write_bytes(adb('logcat', '-d', '-v', 'brief'))
