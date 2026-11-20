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


def validate_trials(baseline, traces, orbit_radius=26, duration=3):
    for trial, samples in enumerate(traces):
        active = []
        for sample in samples:
            if .1 < sample['seconds'] < duration - .15:
                phases = []
                for i in (0, 1):
                    dx = sample['eyes'][i][0] - baseline[i][0]
                    dy = sample['eyes'][i][1] - baseline[i][1] - orbit_radius
                    if abs(math.hypot(dx, dy) - orbit_radius) > 5:
                        raise AssertionError(f'Pupil left expected orbit in trial {trial}')
                    angle = math.atan2(dy, dx)
                    phases.append(((angle + math.pi / 2) if i == 0 else (-math.pi / 2 - angle)) % math.tau)
                if abs((phases[0] - phases[1] + math.pi) % math.tau - math.pi) > .6:
                    raise AssertionError(f'Orbital phases do not oppose in trial {trial}')
                active.append((sample['seconds'], phases))
        if len(active) < 3 or active[-1][0] < duration * .43:
            raise AssertionError(f'Insufficient ongoing post-release motion in trial {trial}; see measurements.json')
        for eye in (0, 1):
            phases = [frame[1][eye] for frame in active]
            if phases[0] >= math.pi or phases[-1] < 1.25 * math.pi or any(b < a - .15 for a, b in zip(phases, phases[1:])):
                raise AssertionError(f'Wrong orbital direction or incomplete post-release orbit in trial {trial}')
        settled = [s for s in samples if s['seconds'] > duration + .2]
        if len(settled) < 2 or settled[-1]['seconds'] - settled[0]['seconds'] < .5 or any(
                math.dist(s['eyes'][i], baseline[i]) > 3 for s in settled for i in (0, 1)):
            raise AssertionError(f'Pupils did not settle within the expected duration in trial {trial}')


def validate_tilt_gain(baseline, tilted, expected):
    deltas=[(tilted[i][0]-baseline[i][0],tilted[i][1]-baseline[i][1]) for i in (0,1)]
    if any(abs(abs(dx)-expected)>2 or abs(dy)>3 for dx,dy in deltas) or deltas[0][0]*deltas[1][0]<=0:
        raise AssertionError(f'Unexpected low-angle tilt gain: {deltas}; expected {expected}px')


def validate_calibration(baseline, tilted, recovered):
    deltas = [(tilted[i][0] - baseline[i][0], tilted[i][1] - baseline[i][1]) for i in (0, 1)]
    if min(math.hypot(*d) for d in deltas) < 10 or sum(a * b for a, b in zip(*deltas)) < 50:
        raise RuntimeError('SETUP: injected low-g acceleration did not move both pupils through the tilt renderer')
    if any(math.dist(recovered[i], baseline[i]) > 3 for i in (0, 1)):
        raise RuntimeError('SETUP: pupils did not recover after sensor calibration')


def run(package, output, expect_spin=True, orbit_radius=26, duration=3, expected_half_tilt=None):
    output.mkdir(parents=True, exist_ok=True)
    # Wear OS opens ChargingActivity over the selected face while charging.
    # Motion calibration must exercise the face, not that system overlay.
    adb('emu', 'power', 'ac', 'off')
    adb('emu', 'power', 'status', 'discharging')
    adb('shell', 'settings', 'put', 'system', 'screen_off_timeout', '600000')
    adb('shell', 'input', 'keyevent', 'KEYCODE_WAKEUP')
    # HOME toggles the app drawer when already on the Wear OS watch face.
    adb('shell', 'input', 'keyevent', 'KEYCODE_BACK')
    adb('shell', 'input', 'keyevent', 'KEYCODE_BACK')
    adb('emu', 'sensor', 'set', 'acceleration', '0:0:9.8')
    print(adb('shell', 'am', 'broadcast', '--async', '-a', 'com.google.android.wearable.app.DEBUG_SURFACE',
              '--es', 'operation', 'set-watchface', '--es', 'watchFaceId', package).decode(), flush=True)
    deadline = time.monotonic() + 120
    while True:
        try:
            baseline = centroids(capture(output, 'baseline'))
            break
        except ValueError:
            if time.monotonic() > deadline:
                raise RuntimeError('SETUP: could not display the watch face; inspect baseline.png and logcat')
            time.sleep(1)

    def visible_eyes(label):
        for attempt in range(8):
            try:
                return centroids(capture(output, label))
            except ValueError:
                time.sleep(.15)
        raise RuntimeError('SETUP: could not measure pupils during ' + label)

    # The vector magnitude stays at1g, below the shake threshold. This proves
    # injection reaches WFF without accidentally arming the spin experiment.
    adb('emu', 'sensor', 'set', 'acceleration', '6.93:0:6.93')
    time.sleep(.6)
    tilted = visible_eyes('calibration-tilt')
    adb('emu', 'sensor', 'set', 'acceleration', '0:0:9.8')
    time.sleep(.6)
    recovered = visible_eyes('calibration-recovered')
    (output / 'calibration.json').write_text(json.dumps({'baseline': baseline, 'tilted': tilted, 'recovered': recovered}, indent=2))
    validate_calibration(baseline, tilted, recovered)

    if expected_half_tilt is not None:
        adb('emu','sensor','set','acceleration','3.75:0:9.05')
        time.sleep(.6)
        soft=visible_eyes('calibration-soft-tilt')
        validate_tilt_gain(baseline,soft,expected_half_tilt)
        (output/'soft-tilt.json').write_text(json.dumps({'baseline':baseline,'tilted':soft,'expected':expected_half_tilt}))
        adb('emu','sensor','set','acceleration','0:0:9.8')
        time.sleep(.6)
        validate_calibration(baseline,tilted,visible_eyes('soft-tilt-recovered'))

    traces = []
    # Two independent pulses detect a one-shot-only reaction or a failure to settle.
    for trial in range(2):
        # Start just after a periodic blink, leaving a clear3s motion window.
        deadline=time.monotonic()+8
        while int(adb('shell','date','+%s').decode().strip()) % 6 != 1:
            if time.monotonic()>deadline:raise RuntimeError('SETUP: no stable clock window for motion capture')
            time.sleep(.15)
        adb('emu', 'sensor', 'set', 'acceleration', '40:0:9.8')
        time.sleep(.35)
        adb('emu', 'sensor', 'set', 'acceleration', '0:0:9.8')
        released = time.monotonic()
        samples = []
        delays=[round(duration*f,2) for f in (.1,.22,.35,.48,.62,.78,.88)] + [duration+.3,duration+.95,duration+1.6]
        for delay in delays:
            remaining = released + delay - time.monotonic()
            if remaining > 0:
                time.sleep(remaining)
            # PNG transfer and pixel analysis can take almost a second on CI.
            # Timestamp the capture request, not the completion of that work.
            capture_started = time.monotonic() - released
            picture = capture(output, f'trial-{trial}-{delay}')
            try:
                points = centroids(picture)
            except ValueError:
                continue  # A periodic blink invalidates this one measurement.
            samples.append({'seconds': capture_started,
                            'completed_seconds': time.monotonic() - released, 'eyes': points})
        traces.append(samples)
    (output / 'measurements.json').write_text(json.dumps({'baseline': baseline, 'trials': traces, 'expected_duration':duration,'expected_orbit_radius':orbit_radius}, indent=2))
    if expect_spin:
        validate_trials(baseline, traces, orbit_radius, duration)
        print('PASS: opposite after-release pupil motion and stationary recovery observed twice in the Wear OS renderer')
    else:
        for samples in traces:
            settled = [s for s in samples if s['seconds'] > .8]
            if len(settled) < 4 or any(math.dist(s['eyes'][i], baseline[i]) > 3 for s in settled for i in (0, 1)):
                raise AssertionError('Shake-disabled control unexpectedly moves after release')
        print('CONTROL CONFIRMED: tilt injection works, with no after-release orbit')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--package', required=True)
    parser.add_argument('--output', type=Path, default=Path('watchface-device-results'))
    parser.add_argument('--expect-no-spin', action='store_true')
    parser.add_argument('--orbit-radius', type=int, choices=(13, 26), default=26)
    parser.add_argument('--duration',type=float,choices=(2,3,4,6),default=3)
    parser.add_argument('--expected-half-tilt',type=float)
    args = parser.parse_args()
    try:
        run(args.package, args.output, not args.expect_no_spin, args.orbit_radius, args.duration, args.expected_half_tilt)
    finally:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / 'logcat.txt').write_bytes(adb('logcat', '-d', '-v', 'brief'))
